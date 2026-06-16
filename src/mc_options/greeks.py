"""Finite-difference and analytical Greeks."""

from __future__ import annotations

import math
from dataclasses import dataclass, replace

import pandas as pd

from mc_options.black_scholes import (
    black_scholes_delta,
    black_scholes_gamma,
    black_scholes_vega,
)
from mc_options.models import MarketParameters, OptionParameters, SimulationParameters
from mc_options.pricer import price_option
from mc_options.simulation import simulate_terminal_prices


@dataclass(frozen=True)
class GreekEstimate:
    value: float
    standard_error: float
    ci_low: float
    ci_high: float


def finite_difference_delta(
    market: MarketParameters,
    option: OptionParameters,
    sim: SimulationParameters,
    spot_bump: float = 1.0,
) -> float:
    up = replace(market, spot=market.spot + spot_bump)
    down = replace(market, spot=market.spot - spot_bump)
    return (price_option(up, option, sim).price - price_option(down, option, sim).price) / (
        2.0 * spot_bump
    )


def finite_difference_gamma(
    market: MarketParameters,
    option: OptionParameters,
    sim: SimulationParameters,
    spot_bump: float = 1.0,
) -> float:
    up = replace(market, spot=market.spot + spot_bump)
    down = replace(market, spot=market.spot - spot_bump)
    base = price_option(market, option, sim).price
    return (
        price_option(up, option, sim).price - 2.0 * base + price_option(down, option, sim).price
    ) / (spot_bump**2)


def finite_difference_vega(
    market: MarketParameters,
    option: OptionParameters,
    sim: SimulationParameters,
    volatility_bump: float = 0.01,
) -> float:
    if market.volatility <= volatility_bump:
        raise ValueError("volatility must be greater than the volatility bump")
    up = replace(market, volatility=market.volatility + volatility_bump)
    down = replace(market, volatility=market.volatility - volatility_bump)
    return (price_option(up, option, sim).price - price_option(down, option, sim).price) / (
        2.0 * volatility_bump
    )


def analytical_greeks(
    market: MarketParameters,
    option: OptionParameters,
) -> dict[str, float]:
    return {
        "delta": black_scholes_delta(market, option),
        "gamma": black_scholes_gamma(market, option),
        "vega": black_scholes_vega(market, option),
    }


def pathwise_delta(
    market: MarketParameters,
    option: OptionParameters,
    sim: SimulationParameters,
) -> GreekEstimate:
    """Estimate European option Delta with the pathwise derivative method."""

    if option.payoff_type != "european":
        raise ValueError("pathwise Delta is implemented for European options only")

    terminal_prices = simulate_terminal_prices(market, sim)
    discount = math.exp(-market.rate * market.maturity)
    if option.option_type == "call":
        samples = discount * (terminal_prices > option.strike) * terminal_prices / market.spot
    else:
        samples = -discount * (terminal_prices < option.strike) * terminal_prices / market.spot

    value = float(samples.mean())
    standard_error = float(samples.std(ddof=1) / math.sqrt(samples.size))
    ci_width = 1.96 * standard_error
    return GreekEstimate(
        value=value,
        standard_error=standard_error,
        ci_low=value - ci_width,
        ci_high=value + ci_width,
    )


def bump_size_sensitivity(
    market: MarketParameters,
    option: OptionParameters,
    sim: SimulationParameters,
    spot_bumps: list[float] | None = None,
    volatility_bumps: list[float] | None = None,
) -> pd.DataFrame:
    """Evaluate finite-difference Greeks across bump sizes."""

    spot_bumps = spot_bumps or [0.25, 0.5, 1.0, 2.0]
    volatility_bumps = volatility_bumps or [0.005, 0.01, 0.02]
    rows: list[dict[str, float | str]] = []

    for bump in spot_bumps:
        rows.append(
            {
                "greek": "delta",
                "bump": bump,
                "estimate": finite_difference_delta(market, option, sim, spot_bump=bump),
                "black_scholes": black_scholes_delta(market, option),
            }
        )
        rows.append(
            {
                "greek": "gamma",
                "bump": bump,
                "estimate": finite_difference_gamma(market, option, sim, spot_bump=bump),
                "black_scholes": black_scholes_gamma(market, option),
            }
        )

    for bump in volatility_bumps:
        rows.append(
            {
                "greek": "vega",
                "bump": bump,
                "estimate": finite_difference_vega(market, option, sim, volatility_bump=bump),
                "black_scholes": black_scholes_vega(market, option),
            }
        )

    frame = pd.DataFrame(rows)
    frame["abs_error"] = (frame["estimate"] - frame["black_scholes"]).abs()
    return frame
