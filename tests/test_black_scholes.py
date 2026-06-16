from math import exp, isclose

import pytest

from mc_options.black_scholes import black_scholes_price, put_call_parity_residual
from mc_options.models import MarketParameters, OptionParameters


def test_black_scholes_known_call_and_put_values() -> None:
    market = MarketParameters(spot=100, rate=0.05, volatility=0.2, maturity=1.0)
    call = OptionParameters(strike=100, option_type="call")
    put = OptionParameters(strike=100, option_type="put")

    assert black_scholes_price(market, call) == pytest.approx(10.4506, abs=1e-4)
    assert black_scholes_price(market, put) == pytest.approx(5.5735, abs=1e-4)


def test_put_call_parity_with_dividends() -> None:
    market = MarketParameters(
        spot=100,
        rate=0.03,
        volatility=0.25,
        maturity=1.5,
        dividend_yield=0.01,
    )
    call = OptionParameters(strike=105, option_type="call")
    put = OptionParameters(strike=105, option_type="put")

    assert put_call_parity_residual(market, call, put) == pytest.approx(0.0, abs=1e-12)


def test_zero_volatility_price_matches_discounted_forward_intrinsic() -> None:
    market = MarketParameters(spot=100, rate=0.05, volatility=0.0, maturity=1.0)
    call = OptionParameters(strike=95, option_type="call")

    expected = exp(-0.05) * max(100 * exp(0.05) - 95, 0)
    assert isclose(black_scholes_price(market, call), expected)


def test_black_scholes_rejects_asian_option() -> None:
    market = MarketParameters(spot=100, rate=0.03, volatility=0.2, maturity=1.0)
    asian = OptionParameters(strike=100, option_type="call", payoff_type="asian")

    with pytest.raises(ValueError):
        black_scholes_price(market, asian)
