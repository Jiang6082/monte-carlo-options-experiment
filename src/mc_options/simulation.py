"""Vectorized geometric Brownian motion simulation."""

from __future__ import annotations

import math

import numpy as np
from numpy.typing import NDArray
from scipy.stats import norm, qmc

from mc_options.models import MarketParameters, SimulationParameters


def _standard_normal_draws(
    sim: SimulationParameters,
    shape: tuple[int, ...],
) -> NDArray[np.float64]:
    if sim.random_method == "sobol":
        return _sobol_normal_draws(sim, shape)
    rng = np.random.default_rng(sim.seed)
    return rng.standard_normal(shape)


def _sobol_normal_draws(
    sim: SimulationParameters,
    shape: tuple[int, ...],
) -> NDArray[np.float64]:
    if len(shape) != 2:
        raise ValueError("Sobol draws require a 2-D shape")
    num_paths, num_steps = shape
    sampler = qmc.Sobol(d=num_steps, scramble=True, seed=sim.seed)
    exponent = math.ceil(math.log2(num_paths))
    uniforms = sampler.random_base2(m=exponent)[:num_paths]
    clipped = np.clip(uniforms, 1e-12, 1.0 - 1e-12)
    return norm.ppf(clipped)


def _apply_moment_matching(draws: NDArray[np.float64]) -> NDArray[np.float64]:
    means = draws.mean(axis=0, keepdims=True)
    stds = draws.std(axis=0, ddof=1, keepdims=True)
    return (draws - means) / stds


def _draws_with_antithetic(
    sim: SimulationParameters,
    num_steps: int,
) -> NDArray[np.float64]:
    if sim.antithetic:
        half_paths = sim.num_paths // 2
        draws = _standard_normal_draws(sim, (half_paths, num_steps))
        paired = np.vstack((draws, -draws))
        return _apply_moment_matching(paired) if sim.moment_matching else paired
    draws = _standard_normal_draws(sim, (sim.num_paths, num_steps))
    return _apply_moment_matching(draws) if sim.moment_matching else draws


def simulate_gbm_paths(
    market: MarketParameters,
    sim: SimulationParameters,
) -> NDArray[np.float64]:
    """Simulate full GBM paths with S0 included in the first column."""

    dt = market.maturity / sim.num_steps
    if sim.brownian_bridge:
        brownian_paths = _brownian_bridge_paths(market, sim)
        brownian_increments = np.diff(brownian_paths, axis=1)
        diffusion = market.volatility * brownian_increments
    else:
        z = _draws_with_antithetic(sim, sim.num_steps)
        diffusion = market.volatility * np.sqrt(dt) * z
    drift = (market.rate - market.dividend_yield - 0.5 * market.volatility**2) * dt
    log_returns = drift + diffusion
    cumulative_returns = np.cumsum(log_returns, axis=1)

    paths = np.empty((sim.num_paths, sim.num_steps + 1), dtype=float)
    paths[:, 0] = market.spot
    paths[:, 1:] = market.spot * np.exp(cumulative_returns)
    return paths


def _brownian_bridge_paths(
    market: MarketParameters,
    sim: SimulationParameters,
) -> NDArray[np.float64]:
    """Construct Brownian paths from independent normals using a bridge order."""

    times = np.linspace(0.0, market.maturity, sim.num_steps + 1)
    draws = _draws_with_antithetic(sim, sim.num_steps)
    brownian = np.empty((sim.num_paths, sim.num_steps + 1), dtype=float)
    brownian[:, 0] = 0.0
    brownian[:, -1] = math.sqrt(market.maturity) * draws[:, 0]

    intervals = [(0, sim.num_steps)]
    column = 1
    while intervals and column < sim.num_steps:
        left, right = intervals.pop(0)
        midpoint = (left + right) // 2
        if midpoint in (left, right):
            continue

        left_time = times[left]
        midpoint_time = times[midpoint]
        right_time = times[right]
        weight_left = (right_time - midpoint_time) / (right_time - left_time)
        weight_right = (midpoint_time - left_time) / (right_time - left_time)
        conditional_mean = weight_left * brownian[:, left] + weight_right * brownian[:, right]
        conditional_variance = (
            (midpoint_time - left_time) * (right_time - midpoint_time) / (right_time - left_time)
        )
        brownian[:, midpoint] = (
            conditional_mean + math.sqrt(conditional_variance) * draws[:, column]
        )
        column += 1
        intervals.extend([(left, midpoint), (midpoint, right)])

    return brownian


def simulate_terminal_prices(
    market: MarketParameters,
    sim: SimulationParameters,
) -> NDArray[np.float64]:
    """Simulate terminal GBM prices using a one-step exact update."""

    z = _draws_with_antithetic(sim, 1).reshape(sim.num_paths)
    drift = (market.rate - market.dividend_yield - 0.5 * market.volatility**2) * market.maturity
    diffusion = market.volatility * np.sqrt(market.maturity) * z
    return market.spot * np.exp(drift + diffusion)
