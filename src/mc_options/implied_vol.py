"""Black-Scholes implied-volatility solver."""

from __future__ import annotations

from dataclasses import replace

from scipy.optimize import brentq

from mc_options.black_scholes import black_scholes_price
from mc_options.models import MarketParameters, OptionParameters


def implied_volatility(
    market: MarketParameters,
    option: OptionParameters,
    target_price: float,
    lower: float = 1e-6,
    upper: float = 5.0,
    tolerance: float = 1e-8,
) -> float:
    """Recover Black-Scholes implied volatility from a European option price."""

    if option.payoff_type != "european":
        raise ValueError("implied volatility is implemented for European options only")
    if target_price <= 0:
        raise ValueError("target_price must be positive")
    if lower <= 0 or upper <= lower:
        raise ValueError("volatility bounds must satisfy 0 < lower < upper")

    def objective(volatility: float) -> float:
        shifted = replace(market, volatility=volatility)
        return black_scholes_price(shifted, option) - target_price

    low_value = objective(lower)
    high_value = objective(upper)
    if low_value * high_value > 0:
        raise ValueError("target_price is outside the price range implied by the volatility bounds")

    return float(brentq(objective, lower, upper, xtol=tolerance, rtol=tolerance))
