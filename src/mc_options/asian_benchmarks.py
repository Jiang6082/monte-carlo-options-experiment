"""Analytical benchmark for discrete geometric-average Asian options."""

from __future__ import annotations

import math

from scipy.stats import norm

from mc_options.models import MarketParameters, OptionParameters


def geometric_asian_price(
    market: MarketParameters,
    option: OptionParameters,
    num_monitoring_dates: int,
) -> float:
    """Price a discrete geometric-average Asian option under GBM.

    Monitoring dates are equally spaced. By default they exclude time zero,
    matching the arithmetic Asian payoff convention used elsewhere in the
    project. Set ``include_initial_in_average=True`` on ``OptionParameters`` to
    include S0 as an additional monitoring date.
    """

    if option.payoff_type != "asian":
        raise ValueError("geometric Asian benchmark requires an Asian option")
    if num_monitoring_dates <= 0:
        raise ValueError("num_monitoring_dates must be positive")

    times = [market.maturity * i / num_monitoring_dates for i in range(1, num_monitoring_dates + 1)]
    if option.include_initial_in_average:
        times = [0.0, *times]

    count = len(times)
    average_time = sum(times) / count
    covariance_sum = sum(min(left, right) for left in times for right in times)
    variance = market.volatility**2 * covariance_sum / count**2
    mean = (
        math.log(market.spot)
        + (market.rate - market.dividend_yield - 0.5 * market.volatility**2) * average_time
    )

    if variance == 0:
        geometric_forward = math.exp(mean)
        intrinsic = (
            max(geometric_forward - option.strike, 0.0)
            if option.option_type == "call"
            else max(option.strike - geometric_forward, 0.0)
        )
        return math.exp(-market.rate * market.maturity) * intrinsic

    std = math.sqrt(variance)
    d1 = (mean - math.log(option.strike) + variance) / std
    d2 = d1 - std
    discounted = math.exp(-market.rate * market.maturity)
    expected_geometric_average = math.exp(mean + 0.5 * variance)

    if option.option_type == "call":
        return discounted * (
            expected_geometric_average * norm.cdf(d1) - option.strike * norm.cdf(d2)
        )
    return discounted * (option.strike * norm.cdf(-d2) - expected_geometric_average * norm.cdf(-d1))
