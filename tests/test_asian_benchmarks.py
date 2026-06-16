import pytest

from mc_options.asian_benchmarks import geometric_asian_price
from mc_options.models import MarketParameters, OptionParameters, SimulationParameters
from mc_options.pricer import price_option


def test_geometric_asian_price_is_below_arithmetic_asian_call() -> None:
    market = MarketParameters(spot=100, rate=0.03, volatility=0.2, maturity=1.0)
    arithmetic = OptionParameters(strike=100, option_type="call", payoff_type="asian")
    sim = SimulationParameters(num_paths=200_000, num_steps=52, seed=42)

    arithmetic_price = price_option(market, arithmetic, sim).price
    geometric_price = geometric_asian_price(market, arithmetic, num_monitoring_dates=52)

    assert geometric_price < arithmetic_price
    assert geometric_price == pytest.approx(5.158, abs=0.05)


def test_geometric_asian_rejects_non_asian_options() -> None:
    market = MarketParameters(spot=100, rate=0.03, volatility=0.2, maturity=1.0)
    european = OptionParameters(strike=100, option_type="call", payoff_type="european")

    with pytest.raises(ValueError):
        geometric_asian_price(market, european, num_monitoring_dates=52)
