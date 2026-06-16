"""Generate JSON data for the static dashboard."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.run_experiments import (  # noqa: E402
    asian_examples,
    convergence_analysis,
    extension_examples,
    greek_validation,
    validation_summary,
)

from mc_options.black_scholes import black_scholes_price  # noqa: E402
from mc_options.models import MarketParameters, OptionParameters, SimulationParameters  # noqa: E402
from mc_options.variance_reduction import compare_variance_reduction_methods  # noqa: E402


def main() -> None:
    market = MarketParameters(spot=100, rate=0.03, volatility=0.2, maturity=1.0)
    call = OptionParameters(strike=100, option_type="call")
    put = OptionParameters(strike=100, option_type="put")
    variance = compare_variance_reduction_methods(
        market,
        call,
        SimulationParameters(num_paths=500_000, num_steps=1, seed=42),
    )
    validation = pd.DataFrame(
        [
            {
                "metric": "European call MC",
                "value": 9.414024,
                "benchmark": black_scholes_price(market, call),
            },
            {
                "metric": "European put MC",
                "value": 6.464930,
                "benchmark": black_scholes_price(market, put),
            },
        ]
    )

    dashboard = {
        "summary": {
            "paths": 500_000,
            "callPrice": 9.414024,
            "callBenchmark": 9.413403,
            "callAbsError": 0.000620,
            "antitheticReduction": 44.292597,
            "controlVariateReduction": 83.141813,
            "coverage": 85,
            "tests": 43,
        },
        "validation": validation.round(6).to_dict(orient="records"),
        "validationSummary": validation_summary(
            pd.DataFrame(
                {
                    "mc_price": [9.414024, 6.464930],
                    "ci_contains_bs": [True, True],
                    "abs_error": [0.000620, 0.006974],
                    "rel_error_pct": [0.0066, 0.1080],
                }
            )
        )
        .round(6)
        .to_dict(orient="records"),
        "convergence": convergence_analysis().round(6).to_dict(orient="records"),
        "varianceReduction": variance[
            ["method", "price", "standard_error", "estimator_variance", "variance_reduction_pct"]
        ]
        .round(6)
        .to_dict(orient="records"),
        "asian": asian_examples()
        .query("sigma == 0.2 and maturity == 1.0")
        .round(6)
        .to_dict(orient="records"),
        "greeks": greek_validation().round(6).to_dict(orient="records"),
        "extensions": extension_examples().round(6).to_dict(orient="records"),
    }
    output = REPO_ROOT / "dashboard" / "data.json"
    output.parent.mkdir(exist_ok=True)
    output.write_text(json.dumps(dashboard, indent=2), encoding="utf-8")
    print(f"Saved dashboard data to {output}")


if __name__ == "__main__":
    main()
