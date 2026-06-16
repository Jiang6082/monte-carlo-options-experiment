from dataclasses import replace

from mc_options.black_scholes import black_scholes_price
from mc_options.models import MarketParameters, OptionParameters, SimulationParameters
from mc_options.pricer import price_option


def test_european_monte_carlo_price_close_to_black_scholes() -> None:
    market = MarketParameters(spot=100, rate=0.03, volatility=0.2, maturity=1.0)
    option = OptionParameters(strike=100, option_type="call")
    sim = SimulationParameters(num_paths=200_000, num_steps=1, seed=42)

    result = price_option(market, option, sim)
    benchmark = black_scholes_price(market, option)

    assert abs(result.price - benchmark) < 3.0 * result.standard_error


def test_call_price_increases_as_spot_increases() -> None:
    low_market = MarketParameters(spot=95, rate=0.03, volatility=0.2, maturity=1.0)
    high_market = replace(low_market, spot=105)
    option = OptionParameters(strike=100, option_type="call")
    sim = SimulationParameters(num_paths=50_000, num_steps=1, seed=2024)

    assert (
        price_option(high_market, option, sim).price > price_option(low_market, option, sim).price
    )


def test_put_price_increases_as_strike_increases() -> None:
    market = MarketParameters(spot=100, rate=0.03, volatility=0.2, maturity=1.0)
    low_strike = OptionParameters(strike=95, option_type="put")
    high_strike = OptionParameters(strike=105, option_type="put")
    sim = SimulationParameters(num_paths=50_000, num_steps=1, seed=2024)

    assert (
        price_option(market, high_strike, sim).price > price_option(market, low_strike, sim).price
    )


def test_confidence_interval_width_narrows_with_more_paths() -> None:
    market = MarketParameters(spot=100, rate=0.03, volatility=0.2, maturity=1.0)
    option = OptionParameters(strike=100, option_type="call")
    small = SimulationParameters(num_paths=5_000, num_steps=1, seed=11)
    large = SimulationParameters(num_paths=80_000, num_steps=1, seed=11)

    small_result = price_option(market, option, small)
    large_result = price_option(market, option, large)

    small_width = small_result.ci_high - small_result.ci_low
    large_width = large_result.ci_high - large_result.ci_low
    assert large_width < small_width


def test_asian_option_pricing_returns_positive_structured_result() -> None:
    market = MarketParameters(spot=100, rate=0.03, volatility=0.2, maturity=1.0)
    option = OptionParameters(strike=100, option_type="call", payoff_type="asian")
    sim = SimulationParameters(num_paths=20_000, num_steps=52, seed=5)

    result = price_option(market, option, sim)

    assert result.price > 0
    assert result.standard_error > 0
    assert result.num_paths == 20_000
    assert result.effective_sample_size == 20_000


def test_digital_option_pricing_returns_discounted_probability() -> None:
    market = MarketParameters(spot=100, rate=0.03, volatility=0.2, maturity=1.0)
    option = OptionParameters(strike=100, option_type="call", payoff_type="digital")
    sim = SimulationParameters(num_paths=100_000, num_steps=1, seed=42)

    result = price_option(market, option, sim)

    assert 0 < result.price < 1


def test_barrier_option_price_below_vanilla_call() -> None:
    market = MarketParameters(spot=100, rate=0.03, volatility=0.2, maturity=1.0)
    vanilla = OptionParameters(strike=100, option_type="call")
    barrier = OptionParameters(
        strike=100,
        option_type="call",
        payoff_type="barrier",
        barrier_type="up-and-out",
        barrier_level=130,
    )
    sim = SimulationParameters(num_paths=50_000, num_steps=52, seed=42)

    assert price_option(market, barrier, sim).price < price_option(market, vanilla, sim).price
