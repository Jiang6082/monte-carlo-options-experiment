"""Longstaff-Schwartz American option pricing."""

from __future__ import annotations

import math

import numpy as np

from mc_options.models import MarketParameters, OptionParameters, SimulationParameters
from mc_options.payoffs import european_call, european_put
from mc_options.simulation import simulate_gbm_paths


def price_american_lsm(
    market: MarketParameters,
    option: OptionParameters,
    sim: SimulationParameters,
    polynomial_degree: int = 2,
) -> float:
    """Price an American option with Longstaff-Schwartz regression."""

    if option.payoff_type != "european":
        raise ValueError("American LSM uses vanilla call/put payoff parameters")
    if polynomial_degree < 1:
        raise ValueError("polynomial_degree must be positive")

    paths = simulate_gbm_paths(market, sim)
    dt = market.maturity / sim.num_steps
    discount = math.exp(-market.rate * dt)

    payoff_fn = european_call if option.option_type == "call" else european_put
    exercise_values = payoff_fn(paths, option.strike)
    cashflows = exercise_values[:, -1].copy()

    for step in range(sim.num_steps - 1, 0, -1):
        in_the_money = exercise_values[:, step] > 0.0
        if not np.any(in_the_money):
            cashflows *= discount
            continue

        x = paths[in_the_money, step]
        y = cashflows[in_the_money] * discount
        degree = min(polynomial_degree, max(1, x.size - 1))
        coefficients = np.polyfit(x, y, degree)
        continuation_values = np.polyval(coefficients, x)
        exercise_now = exercise_values[in_the_money, step] > continuation_values

        discounted_cashflows = cashflows * discount
        indices = np.flatnonzero(in_the_money)
        exercise_indices = indices[exercise_now]
        discounted_cashflows[exercise_indices] = exercise_values[exercise_indices, step]
        cashflows = discounted_cashflows

    return float(cashflows.mean() * discount)
