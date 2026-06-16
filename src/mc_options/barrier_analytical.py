"""Analytical continuous-monitoring barrier benchmarks."""

from __future__ import annotations

import math

from scipy.integrate import quad
from scipy.stats import norm

from mc_options.models import MarketParameters, OptionParameters


def continuous_up_and_out_call(
    market: MarketParameters,
    option: OptionParameters,
) -> float:
    """Price a continuously monitored up-and-out call with no rebate.

    The implementation integrates the reflection-principle density for GBM
    killed at the upper log barrier. It is intentionally written as a numerical
    benchmark because it is easier to audit than memorized closed-form cases.
    """

    if option.payoff_type != "barrier" or option.option_type != "call":
        raise ValueError("benchmark requires a barrier call option")
    if option.barrier_type != "up-and-out" or option.barrier_level is None:
        raise ValueError("benchmark requires an up-and-out barrier_level")
    if option.barrier_level <= max(market.spot, option.strike):
        return 0.0
    if market.volatility == 0:
        terminal = market.spot * math.exp((market.rate - market.dividend_yield) * market.maturity)
        knocked_out = max(market.spot, terminal) >= option.barrier_level
        payoff = 0.0 if knocked_out else max(terminal - option.strike, 0.0)
        return math.exp(-market.rate * market.maturity) * payoff

    variance = market.volatility**2 * market.maturity
    std = math.sqrt(variance)
    drift = (market.rate - market.dividend_yield - 0.5 * market.volatility**2) * market.maturity
    barrier_log = math.log(option.barrier_level / market.spot)
    lower_log = math.log(option.strike / market.spot)
    reflection_multiplier = math.exp(2.0 * drift * barrier_log / variance)

    def killed_density(log_return: float) -> float:
        direct = norm.pdf((log_return - drift) / std) / std
        reflected = norm.pdf((log_return - (2.0 * barrier_log + drift)) / std) / std
        return direct - reflection_multiplier * reflected

    def integrand(log_return: float) -> float:
        terminal = market.spot * math.exp(log_return)
        return (terminal - option.strike) * killed_density(log_return)

    value, _ = quad(integrand, lower_log, barrier_log, epsabs=1e-10, epsrel=1e-10)
    return math.exp(-market.rate * market.maturity) * max(float(value), 0.0)
