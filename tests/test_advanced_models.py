import pandas as pd
import pytest

from mc_options.american import price_american_lsm
from mc_options.barrier_analytical import continuous_up_and_out_call
from mc_options.black_scholes import black_scholes_price
from mc_options.calibration import implied_vol_smile
from mc_options.models import MarketParameters, OptionParameters, SimulationParameters
from mc_options.pricer import price_option
from mc_options.stochastic_vol import HestonParameters, simulate_heston_paths


def test_continuous_up_and_out_call_benchmark_below_discrete_monitoring_price() -> None:
    market = MarketParameters(spot=100, rate=0.03, volatility=0.2, maturity=1.0)
    option = OptionParameters(
        strike=100,
        option_type="call",
        payoff_type="barrier",
        barrier_type="up-and-out",
        barrier_level=130,
    )
    sim = SimulationParameters(num_paths=100_000, num_steps=252, seed=42)

    continuous = continuous_up_and_out_call(market, option)
    discrete = price_option(market, option, sim).price

    assert 0 < continuous < discrete


def test_longstaff_schwartz_american_put_is_at_least_european_put() -> None:
    market = MarketParameters(spot=100, rate=0.03, volatility=0.2, maturity=1.0)
    option = OptionParameters(strike=100, option_type="put")
    sim = SimulationParameters(num_paths=50_000, num_steps=50, seed=42)

    american = price_american_lsm(market, option, sim)
    european = black_scholes_price(market, option)

    assert american >= european


def test_heston_simulation_shapes_and_positive_paths() -> None:
    market = MarketParameters(spot=100, rate=0.03, volatility=0.2, maturity=1.0)
    heston = HestonParameters(
        initial_variance=0.04,
        kappa=2.0,
        theta=0.04,
        vol_of_vol=0.3,
        rho=-0.5,
    )
    sim = SimulationParameters(num_paths=2_000, num_steps=20, seed=42)

    prices, variances = simulate_heston_paths(market, heston, sim)

    assert prices.shape == (2_000, 21)
    assert variances.shape == (2_000, 21)
    assert (prices > 0).all()
    assert (variances >= 0).all()


def test_implied_vol_smile_recovers_flat_volatility() -> None:
    market = MarketParameters(spot=100, rate=0.03, volatility=0.2, maturity=1.0)
    strikes = [90, 100, 110]
    quotes = pd.DataFrame(
        {
            "strike": strikes,
            "maturity": [1.0, 1.0, 1.0],
            "price": [
                black_scholes_price(market, OptionParameters(strike=strike, option_type="call"))
                for strike in strikes
            ],
        }
    )

    smile = implied_vol_smile(market, "call", quotes)

    assert smile["implied_volatility"].tolist() == pytest.approx([0.2, 0.2, 0.2], abs=1e-6)
