import numpy as np
import pytest

from mc_options.models import MarketParameters, SimulationParameters
from mc_options.simulation import simulate_gbm_paths, simulate_terminal_prices


def test_terminal_simulation_is_deterministic_under_fixed_seed() -> None:
    market = MarketParameters(spot=100, rate=0.03, volatility=0.2, maturity=1.0)
    sim = SimulationParameters(num_paths=10_000, num_steps=50, seed=123)

    first = simulate_terminal_prices(market, sim)
    second = simulate_terminal_prices(market, sim)

    np.testing.assert_allclose(first, second)


def test_full_paths_have_expected_shape_and_positive_prices() -> None:
    market = MarketParameters(spot=100, rate=0.03, volatility=0.2, maturity=1.0)
    sim = SimulationParameters(num_paths=1_000, num_steps=12, seed=7)

    paths = simulate_gbm_paths(market, sim)

    assert paths.shape == (1_000, 13)
    assert np.all(paths > 0)
    assert np.all(paths[:, 0] == 100)


def test_antithetic_terminal_shapes_and_repeatability() -> None:
    market = MarketParameters(spot=100, rate=0.03, volatility=0.2, maturity=1.0)
    sim = SimulationParameters(num_paths=2_000, num_steps=50, seed=99, antithetic=True)

    first = simulate_terminal_prices(market, sim)
    second = simulate_terminal_prices(market, sim)

    assert first.shape == (2_000,)
    np.testing.assert_allclose(first, second)


def test_antithetic_requires_even_path_count() -> None:
    with pytest.raises(ValueError):
        SimulationParameters(num_paths=999, num_steps=10, seed=1, antithetic=True)


def test_moment_matching_standardizes_draws_in_terminal_simulation() -> None:
    market = MarketParameters(spot=100, rate=0.0, volatility=0.2, maturity=1.0)
    sim = SimulationParameters(num_paths=10_000, num_steps=1, seed=123, moment_matching=True)

    terminal = simulate_terminal_prices(market, sim)
    implied_z = (np.log(terminal / market.spot) + 0.5 * market.volatility**2) / market.volatility

    assert implied_z.mean() == pytest.approx(0.0, abs=1e-12)
    assert implied_z.std(ddof=1) == pytest.approx(1.0, abs=1e-12)


def test_sobol_terminal_simulation_is_deterministic() -> None:
    market = MarketParameters(spot=100, rate=0.03, volatility=0.2, maturity=1.0)
    sim = SimulationParameters(num_paths=4_096, num_steps=1, seed=123, random_method="sobol")

    first = simulate_terminal_prices(market, sim)
    second = simulate_terminal_prices(market, sim)

    np.testing.assert_allclose(first, second)


def test_brownian_bridge_full_paths_are_positive_and_repeatable() -> None:
    market = MarketParameters(spot=100, rate=0.03, volatility=0.2, maturity=1.0)
    sim = SimulationParameters(
        num_paths=2_048,
        num_steps=16,
        seed=123,
        random_method="sobol",
        brownian_bridge=True,
    )

    first = simulate_gbm_paths(market, sim)
    second = simulate_gbm_paths(market, sim)

    assert first.shape == (2_048, 17)
    assert np.all(first > 0)
    np.testing.assert_allclose(first, second)
