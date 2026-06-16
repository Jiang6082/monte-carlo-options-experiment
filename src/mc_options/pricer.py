"""Monte Carlo option pricing."""

from __future__ import annotations

import math
import time
from dataclasses import dataclass

import numpy as np

from mc_options.models import MarketParameters, OptionParameters, SimulationParameters
from mc_options.payoffs import payoff
from mc_options.simulation import simulate_gbm_paths, simulate_terminal_prices


@dataclass(frozen=True)
class PricingResult:
    price: float
    standard_error: float
    ci_low: float
    ci_high: float
    runtime_seconds: float
    num_paths: int
    effective_sample_size: int
    payoff_variance: float
    estimator_variance: float


def price_option(
    market: MarketParameters,
    option: OptionParameters,
    sim: SimulationParameters,
) -> PricingResult:
    start = time.perf_counter()

    simulated_values = (
        simulate_terminal_prices(market, sim)
        if option.payoff_type in {"european", "digital"}
        else simulate_gbm_paths(market, sim)
    )
    raw_payoffs = payoff(simulated_values, option)
    discount = math.exp(-market.rate * market.maturity)

    sample = _estimator_sample(raw_payoffs, sim)
    discounted_sample = discount * sample

    price = float(discounted_sample.mean())
    standard_error = float(discounted_sample.std(ddof=1) / math.sqrt(sample.size))
    ci_width = 1.96 * standard_error
    payoff_variance = float(discounted_sample.var(ddof=1))
    runtime_seconds = time.perf_counter() - start

    return PricingResult(
        price=price,
        standard_error=standard_error,
        ci_low=price - ci_width,
        ci_high=price + ci_width,
        runtime_seconds=runtime_seconds,
        num_paths=sim.num_paths,
        effective_sample_size=int(sample.size),
        payoff_variance=payoff_variance,
        estimator_variance=standard_error**2,
    )


def _estimator_sample(
    raw_payoffs: np.ndarray,
    sim: SimulationParameters,
) -> np.ndarray:
    if not sim.antithetic:
        return raw_payoffs
    half_paths = sim.num_paths // 2
    return 0.5 * (raw_payoffs[:half_paths] + raw_payoffs[half_paths:])
