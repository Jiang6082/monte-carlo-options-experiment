"""Run reproducible project experiments and print markdown tables.

This script is intentionally lightweight: it gives reviewers a single command
to regenerate the headline numbers used in RESULTS.md.
"""
# ruff: noqa: E402

from __future__ import annotations

import sys
from dataclasses import asdict
from pathlib import Path

import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from mc_options.american import price_american_lsm
from mc_options.asian_benchmarks import geometric_asian_price
from mc_options.barrier_analytical import continuous_up_and_out_call
from mc_options.black_scholes import (
    black_scholes_delta,
    black_scholes_gamma,
    black_scholes_price,
    black_scholes_vega,
)
from mc_options.greeks import (
    bump_size_sensitivity,
    finite_difference_delta,
    finite_difference_gamma,
    finite_difference_vega,
    pathwise_delta,
)
from mc_options.implied_vol import implied_volatility
from mc_options.models import MarketParameters, OptionParameters, SimulationParameters
from mc_options.pricer import price_option
from mc_options.stochastic_vol import HestonParameters, simulate_heston_paths
from mc_options.variance_reduction import (
    compare_antithetic_sampling,
    compare_variance_reduction_methods,
)


def black_scholes_validation() -> pd.DataFrame:
    rows: list[dict[str, float | str | bool]] = []
    for strike in [80, 90, 100, 110, 120]:
        for sigma in [0.10, 0.20, 0.40]:
            for maturity in [0.25, 0.5, 1.0, 2.0]:
                market = MarketParameters(
                    spot=100,
                    rate=0.03,
                    volatility=sigma,
                    maturity=maturity,
                )
                for option_type in ["call", "put"]:
                    option = OptionParameters(strike=strike, option_type=option_type)
                    sim = SimulationParameters(num_paths=100_000, num_steps=1, seed=42)
                    result = price_option(market, option, sim)
                    bs_price = black_scholes_price(market, option)
                    abs_error = abs(result.price - bs_price)
                    rows.append(
                        {
                            "option_type": option_type,
                            "strike": strike,
                            "sigma": sigma,
                            "maturity": maturity,
                            "mc_price": result.price,
                            "bs_price": bs_price,
                            "abs_error": abs_error,
                            "rel_error_pct": 100 * abs_error / bs_price if bs_price else 0.0,
                            "ci_contains_bs": result.ci_low <= bs_price <= result.ci_high,
                            "standard_error": result.standard_error,
                        }
                    )
    return pd.DataFrame(rows)


def convergence_analysis() -> pd.DataFrame:
    market = MarketParameters(spot=100, rate=0.03, volatility=0.2, maturity=1.0)
    option = OptionParameters(strike=100, option_type="call")
    benchmark = black_scholes_price(market, option)
    rows = []
    for paths in [1_000, 5_000, 10_000, 50_000, 100_000, 500_000]:
        sim = SimulationParameters(num_paths=paths, num_steps=1, seed=42)
        result = price_option(market, option, sim)
        rows.append(
            {
                "num_paths": paths,
                "price": result.price,
                "bs_price": benchmark,
                "abs_error": abs(result.price - benchmark),
                "standard_error": result.standard_error,
                "ci_width": result.ci_high - result.ci_low,
                "runtime_seconds": result.runtime_seconds,
            }
        )
    return pd.DataFrame(rows)


def asian_examples() -> pd.DataFrame:
    rows = []
    for sigma in [0.10, 0.20, 0.40]:
        for maturity in [0.5, 1.0, 2.0]:
            for steps in [12, 52, 252]:
                market = MarketParameters(
                    spot=100,
                    rate=0.03,
                    volatility=sigma,
                    maturity=maturity,
                )
                sim = SimulationParameters(num_paths=50_000, num_steps=steps, seed=42)
                european = price_option(
                    market,
                    OptionParameters(strike=100, option_type="call", payoff_type="european"),
                    sim,
                )
                asian = price_option(
                    market,
                    OptionParameters(strike=100, option_type="call", payoff_type="asian"),
                    sim,
                )
                geometric = geometric_asian_price(
                    market,
                    OptionParameters(strike=100, option_type="call", payoff_type="asian"),
                    num_monitoring_dates=steps,
                )
                rows.append(
                    {
                        "sigma": sigma,
                        "maturity": maturity,
                        "monitoring_steps": steps,
                        "european_call": european.price,
                        "asian_call": asian.price,
                        "geometric_asian_call": geometric,
                        "asian_discount_pct": 100 * (european.price - asian.price) / european.price,
                    }
                )
    return pd.DataFrame(rows)


def greek_validation() -> pd.DataFrame:
    market = MarketParameters(spot=100, rate=0.03, volatility=0.2, maturity=1.0)
    option = OptionParameters(strike=100, option_type="call")
    sim = SimulationParameters(num_paths=250_000, num_steps=1, seed=77)
    pathwise = pathwise_delta(market, option, sim)
    rows = [
        {
            "greek": "delta",
            "method": "finite_difference",
            "monte_carlo_fd": finite_difference_delta(market, option, sim, spot_bump=1.0),
            "black_scholes": black_scholes_delta(market, option),
        },
        {
            "greek": "delta",
            "method": "pathwise",
            "monte_carlo_fd": pathwise.value,
            "black_scholes": black_scholes_delta(market, option),
        },
        {
            "greek": "gamma",
            "method": "finite_difference",
            "monte_carlo_fd": finite_difference_gamma(market, option, sim, spot_bump=1.0),
            "black_scholes": black_scholes_gamma(market, option),
        },
        {
            "greek": "vega",
            "method": "finite_difference",
            "monte_carlo_fd": finite_difference_vega(market, option, sim, volatility_bump=0.01),
            "black_scholes": black_scholes_vega(market, option),
        },
    ]
    frame = pd.DataFrame(rows)
    frame["abs_error"] = (frame["monte_carlo_fd"] - frame["black_scholes"]).abs()
    return frame


def markdown_table(frame: pd.DataFrame, index: bool = False) -> str:
    table = frame.reset_index() if index else frame.copy()
    formatted = table.astype(str)
    headers = list(formatted.columns)
    rows = [[str(value) for value in row] for row in formatted.values.tolist()]
    separator = ["---"] * len(headers)
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(separator) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(row) + " |")
    return "\n".join(lines)


def validation_summary(validation: pd.DataFrame) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {"metric": "total_cases", "value": len(validation)},
            {"metric": "ci_coverage", "value": validation["ci_contains_bs"].mean()},
            {"metric": "mean_abs_error", "value": validation["abs_error"].mean()},
            {"metric": "max_abs_error", "value": validation["abs_error"].max()},
            {"metric": "median_rel_error_pct", "value": validation["rel_error_pct"].median()},
        ]
    )


def extension_examples() -> pd.DataFrame:
    market = MarketParameters(spot=100, rate=0.03, volatility=0.2, maturity=1.0)
    rows = []
    digital = OptionParameters(strike=100, option_type="call", payoff_type="digital")
    barrier = OptionParameters(
        strike=100,
        option_type="call",
        payoff_type="barrier",
        barrier_type="up-and-out",
        barrier_level=130,
    )
    vanilla = OptionParameters(strike=100, option_type="call")
    digital_result = price_option(
        market,
        digital,
        SimulationParameters(num_paths=200_000, num_steps=1, seed=42),
    )
    barrier_result = price_option(
        market,
        barrier,
        SimulationParameters(num_paths=100_000, num_steps=252, seed=42),
    )
    barrier_benchmark = continuous_up_and_out_call(market, barrier)
    bridge_result = price_option(
        market,
        vanilla,
        SimulationParameters(
            num_paths=65_536,
            num_steps=16,
            seed=42,
            random_method="sobol",
            brownian_bridge=True,
        ),
    )
    rows.append({"feature": "digital_call", "value": digital_result.price})
    rows.append({"feature": "up_and_out_call", "value": barrier_result.price})
    rows.append({"feature": "continuous_up_and_out_call_benchmark", "value": barrier_benchmark})
    rows.append({"feature": "sobol_brownian_bridge_call", "value": bridge_result.price})
    rows.append(
        {
            "feature": "implied_volatility_recovered",
            "value": implied_volatility(market, vanilla, black_scholes_price(market, vanilla)),
        }
    )
    american_put = price_american_lsm(
        market,
        OptionParameters(strike=100, option_type="put"),
        SimulationParameters(num_paths=50_000, num_steps=50, seed=42),
    )
    rows.append({"feature": "american_put_lsm", "value": american_put})

    heston = HestonParameters(
        initial_variance=0.04,
        kappa=2.0,
        theta=0.04,
        vol_of_vol=0.3,
        rho=-0.5,
    )
    heston_prices, heston_variances = simulate_heston_paths(
        market,
        heston,
        SimulationParameters(num_paths=20_000, num_steps=52, seed=42),
    )
    rows.append({"feature": "heston_mean_terminal_price", "value": heston_prices[:, -1].mean()})
    rows.append(
        {"feature": "heston_mean_terminal_variance", "value": heston_variances[:, -1].mean()}
    )
    return pd.DataFrame(rows)


def main() -> None:
    market = MarketParameters(spot=100, rate=0.03, volatility=0.2, maturity=1.0)
    call = OptionParameters(strike=100, option_type="call")
    put = OptionParameters(strike=100, option_type="put")
    main_sim = SimulationParameters(num_paths=500_000, num_steps=1, seed=42)

    main_call = price_option(market, call, main_sim)
    main_put = price_option(market, put, main_sim)
    call_bs = black_scholes_price(market, call)
    put_bs = black_scholes_price(market, put)
    antithetic = compare_antithetic_sampling(market, call, main_sim)
    variance_methods = compare_variance_reduction_methods(market, call, main_sim)
    convergence = convergence_analysis()
    validation = black_scholes_validation()
    asian = asian_examples()
    greeks = greek_validation()
    extensions = extension_examples()
    sensitivity = bump_size_sensitivity(
        market,
        call,
        SimulationParameters(num_paths=100_000, num_steps=1, seed=77),
    )

    print("# Main European validation")
    print(
        markdown_table(
            pd.DataFrame(
                [
                    {
                        "option": "call",
                        **asdict(main_call),
                        "black_scholes": call_bs,
                        "abs_error": abs(main_call.price - call_bs),
                    },
                    {
                        "option": "put",
                        **asdict(main_put),
                        "black_scholes": put_bs,
                        "abs_error": abs(main_put.price - put_bs),
                    },
                ]
            ).round(6),
            index=False,
        )
    )

    print("\n# Convergence")
    print(markdown_table(convergence.round(6), index=False))

    print("\n# Antithetic")
    print(
        markdown_table(
            antithetic[
                [
                    "method",
                    "price",
                    "standard_error",
                    "estimator_variance",
                    "runtime_seconds",
                    "variance_reduction_pct",
                ]
            ].round(6),
            index=False,
        )
    )

    print("\n# Variance reduction methods")
    print(
        markdown_table(
            variance_methods[
                [
                    "method",
                    "price",
                    "standard_error",
                    "estimator_variance",
                    "variance_reduction_pct",
                ]
            ].round(6),
            index=False,
        )
    )

    print("\n# Validation summary")
    print(markdown_table(validation_summary(validation).round(6), index=False))

    print("\n# Asian sample")
    print(markdown_table(asian.query("sigma == 0.2 and maturity == 1.0").round(6), index=False))

    print("\n# Greeks")
    print(markdown_table(greeks.round(6), index=False))

    print("\n# Greek bump-size sensitivity")
    print(markdown_table(sensitivity.round(6), index=False))

    print("\n# Extension examples")
    print(markdown_table(extensions.round(6), index=False))

    slope = np.polyfit(
        np.log(convergence["num_paths"].to_numpy()),
        np.log(convergence["standard_error"].to_numpy()),
        1,
    )[0]
    print(f"\n# Standard-error log-log slope: {slope:.6f}")


if __name__ == "__main__":
    main()
