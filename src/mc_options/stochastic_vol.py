"""Heston stochastic-volatility simulation."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray

from mc_options.models import MarketParameters, SimulationParameters


@dataclass(frozen=True)
class HestonParameters:
    initial_variance: float
    kappa: float
    theta: float
    vol_of_vol: float
    rho: float

    def __post_init__(self) -> None:
        if self.initial_variance < 0 or self.theta < 0:
            raise ValueError("variances must be non-negative")
        if self.kappa <= 0:
            raise ValueError("kappa must be positive")
        if self.vol_of_vol < 0:
            raise ValueError("vol_of_vol must be non-negative")
        if not -1 <= self.rho <= 1:
            raise ValueError("rho must be between -1 and 1")


def simulate_heston_paths(
    market: MarketParameters,
    heston: HestonParameters,
    sim: SimulationParameters,
) -> tuple[NDArray[np.float64], NDArray[np.float64]]:
    """Simulate Heston price and variance paths with full-truncation Euler."""

    rng = np.random.default_rng(sim.seed)
    dt = market.maturity / sim.num_steps
    sqrt_dt = np.sqrt(dt)

    prices = np.empty((sim.num_paths, sim.num_steps + 1), dtype=float)
    variances = np.empty_like(prices)
    prices[:, 0] = market.spot
    variances[:, 0] = heston.initial_variance

    for step in range(sim.num_steps):
        z_variance = rng.standard_normal(sim.num_paths)
        z_independent = rng.standard_normal(sim.num_paths)
        z_price = heston.rho * z_variance + np.sqrt(1.0 - heston.rho**2) * z_independent
        variance = np.maximum(variances[:, step], 0.0)
        next_variance = (
            variances[:, step]
            + heston.kappa * (heston.theta - variance) * dt
            + heston.vol_of_vol * np.sqrt(variance) * sqrt_dt * z_variance
        )
        variances[:, step + 1] = np.maximum(next_variance, 0.0)
        prices[:, step + 1] = prices[:, step] * np.exp(
            (market.rate - market.dividend_yield - 0.5 * variance) * dt
            + np.sqrt(variance) * sqrt_dt * z_price
        )

    return prices, variances
