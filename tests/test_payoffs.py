import numpy as np

from mc_options.models import OptionParameters
from mc_options.payoffs import (
    asian_call,
    asian_put,
    barrier_payoff,
    digital_call,
    digital_put,
    european_call,
    european_put,
    payoff,
)


def test_european_call_and_put_payoffs() -> None:
    terminal = np.array([80.0, 100.0, 120.0])

    np.testing.assert_allclose(european_call(terminal, 100), [0, 0, 20])
    np.testing.assert_allclose(european_put(terminal, 100), [20, 0, 0])


def test_asian_payoffs_exclude_initial_by_default() -> None:
    paths = np.array(
        [
            [100.0, 100.0, 110.0],
            [100.0, 90.0, 95.0],
        ]
    )

    np.testing.assert_allclose(asian_call(paths, 100, include_initial=False), [5.0, 0.0])
    np.testing.assert_allclose(asian_put(paths, 100, include_initial=False), [0.0, 7.5])


def test_payoff_dispatch_for_asian_option() -> None:
    paths = np.array([[100.0, 105.0, 115.0]])
    option = OptionParameters(strike=100, option_type="call", payoff_type="asian")

    np.testing.assert_allclose(payoff(paths, option), [10.0])


def test_digital_payoffs() -> None:
    terminal = np.array([90.0, 100.0, 110.0])

    np.testing.assert_allclose(digital_call(terminal, 100, cash=2.0), [0.0, 0.0, 2.0])
    np.testing.assert_allclose(digital_put(terminal, 100, cash=3.0), [3.0, 0.0, 0.0])


def test_barrier_payoff_knocks_out_paths() -> None:
    paths = np.array(
        [
            [100.0, 110.0, 120.0],
            [100.0, 135.0, 125.0],
        ]
    )
    option = OptionParameters(
        strike=100,
        option_type="call",
        payoff_type="barrier",
        barrier_type="up-and-out",
        barrier_level=130,
    )

    np.testing.assert_allclose(barrier_payoff(paths, option), [20.0, 0.0])
