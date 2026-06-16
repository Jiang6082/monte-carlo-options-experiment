import pytest

from mc_options.black_scholes import (
    black_scholes_delta,
    black_scholes_gamma,
    black_scholes_vega,
)
from mc_options.greeks import (
    bump_size_sensitivity,
    finite_difference_delta,
    finite_difference_gamma,
    finite_difference_vega,
    pathwise_delta,
)
from mc_options.models import MarketParameters, OptionParameters, SimulationParameters


def test_finite_difference_greeks_near_analytical_benchmarks() -> None:
    market = MarketParameters(spot=100, rate=0.03, volatility=0.2, maturity=1.0)
    option = OptionParameters(strike=100, option_type="call")
    sim = SimulationParameters(num_paths=250_000, num_steps=1, seed=77)

    delta = finite_difference_delta(market, option, sim, spot_bump=1.0)
    gamma = finite_difference_gamma(market, option, sim, spot_bump=1.0)
    vega = finite_difference_vega(market, option, sim, volatility_bump=0.01)

    assert delta == pytest.approx(black_scholes_delta(market, option), abs=0.02)
    assert gamma == pytest.approx(black_scholes_gamma(market, option), abs=0.004)
    assert vega == pytest.approx(black_scholes_vega(market, option), abs=1.5)


def test_pathwise_delta_near_analytical_benchmark() -> None:
    market = MarketParameters(spot=100, rate=0.03, volatility=0.2, maturity=1.0)
    option = OptionParameters(strike=100, option_type="call")
    sim = SimulationParameters(num_paths=150_000, num_steps=1, seed=77)

    estimate = pathwise_delta(market, option, sim)

    assert estimate.value == pytest.approx(black_scholes_delta(market, option), abs=0.01)
    assert estimate.standard_error > 0


def test_bump_size_sensitivity_reports_errors() -> None:
    market = MarketParameters(spot=100, rate=0.03, volatility=0.2, maturity=1.0)
    option = OptionParameters(strike=100, option_type="call")
    sim = SimulationParameters(num_paths=20_000, num_steps=1, seed=77)

    sensitivity = bump_size_sensitivity(
        market,
        option,
        sim,
        spot_bumps=[1.0],
        volatility_bumps=[0.01],
    )

    assert set(sensitivity["greek"]) == {"delta", "gamma", "vega"}
    assert (sensitivity["abs_error"] >= 0).all()
