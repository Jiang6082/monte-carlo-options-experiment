"""Payoff functions for European and arithmetic-average Asian options."""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray

from mc_options.models import OptionParameters


def european_call(terminal_prices: NDArray[np.float64], strike: float) -> NDArray[np.float64]:
    return np.maximum(terminal_prices - strike, 0.0)


def european_put(terminal_prices: NDArray[np.float64], strike: float) -> NDArray[np.float64]:
    return np.maximum(strike - terminal_prices, 0.0)


def asian_call(
    paths: NDArray[np.float64],
    strike: float,
    include_initial: bool = False,
) -> NDArray[np.float64]:
    averages = _arithmetic_average(paths, include_initial)
    return np.maximum(averages - strike, 0.0)


def asian_put(
    paths: NDArray[np.float64],
    strike: float,
    include_initial: bool = False,
) -> NDArray[np.float64]:
    averages = _arithmetic_average(paths, include_initial)
    return np.maximum(strike - averages, 0.0)


def digital_call(
    terminal_prices: NDArray[np.float64],
    strike: float,
    cash: float = 1.0,
) -> NDArray[np.float64]:
    return cash * (terminal_prices > strike).astype(float)


def digital_put(
    terminal_prices: NDArray[np.float64],
    strike: float,
    cash: float = 1.0,
) -> NDArray[np.float64]:
    return cash * (terminal_prices < strike).astype(float)


def barrier_payoff(
    paths: NDArray[np.float64],
    option: OptionParameters,
) -> NDArray[np.float64]:
    if option.barrier_level is None or option.barrier_type is None:
        raise ValueError("barrier options require barrier_level and barrier_type")
    terminal = paths[:, -1]
    vanilla = (
        european_call(terminal, option.strike)
        if option.option_type == "call"
        else european_put(terminal, option.strike)
    )
    if option.barrier_type == "up-and-out":
        active = paths.max(axis=1) < option.barrier_level
    else:
        active = paths.min(axis=1) > option.barrier_level
    return vanilla * active.astype(float)


def payoff(values: NDArray[np.float64], option: OptionParameters) -> NDArray[np.float64]:
    """Dispatch to the correct payoff.

    European options expect a 1-D terminal price array. Asian options expect a
    2-D path array with the initial spot in column zero.
    """

    if option.payoff_type == "european":
        terminal_prices = np.asarray(values)
        if terminal_prices.ndim != 1:
            terminal_prices = terminal_prices[:, -1]
        if option.option_type == "call":
            return european_call(terminal_prices, option.strike)
        return european_put(terminal_prices, option.strike)

    if option.payoff_type == "digital":
        terminal_prices = np.asarray(values)
        if terminal_prices.ndim != 1:
            terminal_prices = terminal_prices[:, -1]
        if option.option_type == "call":
            return digital_call(terminal_prices, option.strike, option.digital_cash)
        return digital_put(terminal_prices, option.strike, option.digital_cash)

    paths = np.asarray(values)
    if paths.ndim != 2:
        raise ValueError("Asian and barrier payoffs require full simulated paths")
    if option.payoff_type == "barrier":
        return barrier_payoff(paths, option)
    if option.option_type == "call":
        return asian_call(paths, option.strike, option.include_initial_in_average)
    return asian_put(paths, option.strike, option.include_initial_in_average)


def _arithmetic_average(
    paths: NDArray[np.float64],
    include_initial: bool,
) -> NDArray[np.float64]:
    if paths.ndim != 2:
        raise ValueError("paths must be a 2-D array")
    monitored = paths if include_initial else paths[:, 1:]
    return monitored.mean(axis=1)
