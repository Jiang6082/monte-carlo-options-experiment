"""Configuration objects for markets, options, and simulations."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

OptionType = Literal["call", "put"]
PayoffType = Literal["european", "asian", "digital", "barrier"]
RandomMethod = Literal["pseudo", "sobol"]
BarrierType = Literal["up-and-out", "down-and-out"]


@dataclass(frozen=True)
class MarketParameters:
    """Risk-neutral market inputs for geometric Brownian motion."""

    spot: float
    rate: float
    volatility: float
    maturity: float
    dividend_yield: float = 0.0

    def __post_init__(self) -> None:
        if not all(
            isinstance(value, (int, float))
            for value in (
                self.spot,
                self.rate,
                self.volatility,
                self.maturity,
                self.dividend_yield,
            )
        ):
            raise TypeError("market parameters must be numeric")
        if self.spot <= 0:
            raise ValueError("spot must be positive")
        if self.volatility < 0:
            raise ValueError("volatility must be non-negative")
        if self.maturity <= 0:
            raise ValueError("maturity must be positive")


@dataclass(frozen=True)
class OptionParameters:
    """Option contract inputs.

    For arithmetic Asian options, ``include_initial_in_average`` controls whether
    S0 is included in the arithmetic average. The project default is False, so
    Asian payoffs average simulated monitoring dates after time zero.
    """

    strike: float
    option_type: OptionType = "call"
    payoff_type: PayoffType = "european"
    include_initial_in_average: bool = False
    digital_cash: float = 1.0
    barrier_level: float | None = None
    barrier_type: BarrierType | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.strike, (int, float)):
            raise TypeError("strike must be numeric")
        if self.strike <= 0:
            raise ValueError("strike must be positive")
        if self.option_type not in {"call", "put"}:
            raise ValueError("option_type must be 'call' or 'put'")
        if self.payoff_type not in {"european", "asian", "digital", "barrier"}:
            raise ValueError("payoff_type must be 'european', 'asian', 'digital', or 'barrier'")
        if self.digital_cash <= 0:
            raise ValueError("digital_cash must be positive")
        if self.payoff_type == "barrier":
            if self.barrier_level is None or self.barrier_level <= 0:
                raise ValueError("barrier options require a positive barrier_level")
            if self.barrier_type not in {"up-and-out", "down-and-out"}:
                raise ValueError("barrier_type must be 'up-and-out' or 'down-and-out'")


@dataclass(frozen=True)
class SimulationParameters:
    """Monte Carlo simulation controls."""

    num_paths: int
    num_steps: int
    seed: int | None = 42
    antithetic: bool = False
    moment_matching: bool = False
    random_method: RandomMethod = "pseudo"
    brownian_bridge: bool = False

    def __post_init__(self) -> None:
        if not isinstance(self.num_paths, int) or not isinstance(self.num_steps, int):
            raise TypeError("num_paths and num_steps must be integers")
        if self.num_paths <= 1:
            raise ValueError("num_paths must be greater than 1")
        if self.num_steps <= 0:
            raise ValueError("num_steps must be positive")
        if self.seed is not None and not isinstance(self.seed, int):
            raise TypeError("seed must be an integer or None")
        if self.antithetic and self.num_paths % 2 != 0:
            raise ValueError("num_paths must be even when antithetic sampling is enabled")
        if self.random_method not in {"pseudo", "sobol"}:
            raise ValueError("random_method must be 'pseudo' or 'sobol'")
        if self.brownian_bridge and self.num_steps < 2:
            raise ValueError("brownian_bridge requires at least two time steps")
