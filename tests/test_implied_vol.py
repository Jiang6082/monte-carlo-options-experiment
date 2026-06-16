import pytest

from mc_options.black_scholes import black_scholes_price
from mc_options.implied_vol import implied_volatility
from mc_options.models import MarketParameters, OptionParameters


def test_implied_volatility_recovers_known_volatility() -> None:
    market = MarketParameters(spot=100, rate=0.03, volatility=0.2, maturity=1.0)
    option = OptionParameters(strike=100, option_type="call")
    price = black_scholes_price(market, option)

    recovered = implied_volatility(market, option, price)

    assert recovered == pytest.approx(0.2, abs=1e-6)


def test_implied_volatility_rejects_non_european_option() -> None:
    market = MarketParameters(spot=100, rate=0.03, volatility=0.2, maturity=1.0)
    option = OptionParameters(strike=100, option_type="call", payoff_type="asian")

    with pytest.raises(ValueError):
        implied_volatility(market, option, target_price=5.0)
