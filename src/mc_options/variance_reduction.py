"""Utilities for measuring antithetic variance reduction."""

from __future__ import annotations

import math
from dataclasses import asdict

import numpy as np
import pandas as pd

from mc_options.models import MarketParameters, OptionParameters, SimulationParameters
from mc_options.payoffs import payoff
from mc_options.pricer import PricingResult, price_option
from mc_options.simulation import simulate_gbm_paths, simulate_terminal_prices


def compare_antithetic_sampling(
    market: MarketParameters,
    option: OptionParameters,
    base_simulation: SimulationParameters,
) -> pd.DataFrame:
    """Compare standard Monte Carlo and antithetic variates using equal path counts."""

    standard_sim = SimulationParameters(
        num_paths=base_simulation.num_paths,
        num_steps=base_simulation.num_steps,
        seed=base_simulation.seed,
        antithetic=False,
    )
    antithetic_sim = SimulationParameters(
        num_paths=base_simulation.num_paths,
        num_steps=base_simulation.num_steps,
        seed=base_simulation.seed,
        antithetic=True,
    )
    standard = price_option(market, option, standard_sim)
    antithetic = price_option(market, option, antithetic_sim)
    variance_reduction = 100.0 * (1.0 - antithetic.estimator_variance / standard.estimator_variance)

    rows = [
        {"method": "standard", **asdict(standard), "variance_reduction_pct": 0.0},
        {
            "method": "antithetic",
            **asdict(antithetic),
            "variance_reduction_pct": variance_reduction,
        },
    ]
    return pd.DataFrame(rows)


def price_option_control_variate(
    market: MarketParameters,
    option: OptionParameters,
    sim: SimulationParameters,
) -> PricingResult:
    """Price with discounted terminal stock value as a control variate."""

    import time

    start = time.perf_counter()
    simulated_values = (
        simulate_terminal_prices(market, sim)
        if option.payoff_type == "european"
        else simulate_gbm_paths(market, sim)
    )
    terminal_prices = (
        simulated_values if option.payoff_type == "european" else simulated_values[:, -1]
    )
    raw_payoffs = payoff(simulated_values, option)

    discount = math.exp(-market.rate * market.maturity)
    discounted_payoffs = discount * raw_payoffs
    discounted_terminal = discount * terminal_prices
    expected_discounted_terminal = market.spot * math.exp(-market.dividend_yield * market.maturity)

    covariance = np.cov(discounted_payoffs, discounted_terminal, ddof=1)
    beta = covariance[0, 1] / covariance[1, 1]
    adjusted = discounted_payoffs - beta * (discounted_terminal - expected_discounted_terminal)

    price = float(adjusted.mean())
    standard_error = float(adjusted.std(ddof=1) / math.sqrt(adjusted.size))
    ci_width = 1.96 * standard_error
    runtime_seconds = time.perf_counter() - start

    return PricingResult(
        price=price,
        standard_error=standard_error,
        ci_low=price - ci_width,
        ci_high=price + ci_width,
        runtime_seconds=runtime_seconds,
        num_paths=sim.num_paths,
        effective_sample_size=sim.num_paths,
        payoff_variance=float(adjusted.var(ddof=1)),
        estimator_variance=standard_error**2,
    )


def compare_variance_reduction_methods(
    market: MarketParameters,
    option: OptionParameters,
    base_simulation: SimulationParameters,
) -> pd.DataFrame:
    """Compare standard MC, antithetic, moment matching, Sobol, and control variates."""

    configs = {
        "standard": SimulationParameters(
            base_simulation.num_paths,
            base_simulation.num_steps,
            base_simulation.seed,
        ),
        "antithetic": SimulationParameters(
            base_simulation.num_paths,
            base_simulation.num_steps,
            base_simulation.seed,
            antithetic=True,
        ),
        "moment_matching": SimulationParameters(
            base_simulation.num_paths,
            base_simulation.num_steps,
            base_simulation.seed,
            moment_matching=True,
        ),
        "sobol": SimulationParameters(
            base_simulation.num_paths,
            base_simulation.num_steps,
            base_simulation.seed,
            random_method="sobol",
        ),
    }
    standard = price_option(market, option, configs["standard"])
    rows = [{"method": "standard", **asdict(standard), "variance_reduction_pct": 0.0}]

    for method, sim in configs.items():
        if method == "standard":
            continue
        result = price_option(market, option, sim)
        rows.append(
            {
                "method": method,
                **asdict(result),
                "variance_reduction_pct": 100.0
                * (1.0 - result.estimator_variance / standard.estimator_variance),
            }
        )

    control = price_option_control_variate(market, option, configs["standard"])
    rows.append(
        {
            "method": "control_variate",
            **asdict(control),
            "variance_reduction_pct": 100.0
            * (1.0 - control.estimator_variance / standard.estimator_variance),
        }
    )
    return pd.DataFrame(rows)
