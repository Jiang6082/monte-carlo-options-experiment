"""Simple performance benchmark for pricing methods and path counts."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from mc_options.models import MarketParameters, OptionParameters, SimulationParameters  # noqa: E402
from mc_options.pricer import price_option  # noqa: E402


def main() -> None:
    market = MarketParameters(spot=100, rate=0.03, volatility=0.20, maturity=1.0)
    option = OptionParameters(strike=100, option_type="call")
    rows = []

    for paths in [10_000, 50_000, 100_000, 500_000]:
        for method, kwargs in {
            "standard": {},
            "antithetic": {"antithetic": True},
            "moment_matching": {"moment_matching": True},
            "sobol": {"random_method": "sobol"},
        }.items():
            result = price_option(
                market,
                option,
                SimulationParameters(num_paths=paths, num_steps=1, seed=42, **kwargs),
            )
            rows.append(
                {
                    "method": method,
                    "paths": paths,
                    "price": result.price,
                    "standard_error": result.standard_error,
                    "runtime_seconds": result.runtime_seconds,
                }
            )

    benchmark = pd.DataFrame(rows).round(6)
    output_dir = REPO_ROOT / "benchmarks"
    output_dir.mkdir(exist_ok=True)
    benchmark.to_csv(output_dir / "performance.csv", index=False)
    (output_dir / "performance.md").write_text(markdown_table(benchmark), encoding="utf-8")
    print(benchmark.to_string(index=False))
    print(f"\nSaved benchmark artifacts to {output_dir}")


def markdown_table(frame: pd.DataFrame) -> str:
    headers = list(frame.columns)
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for row in frame.astype(str).values.tolist():
        lines.append("| " + " | ".join(row) + " |")
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    main()
