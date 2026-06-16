from mc_options.models import MarketParameters, OptionParameters, SimulationParameters
from mc_options.pricer import price_option
from mc_options.variance_reduction import (
    compare_antithetic_sampling,
    compare_variance_reduction_methods,
    price_option_control_variate,
)


def test_antithetic_sampling_reduces_estimator_variance_for_representative_call() -> None:
    market = MarketParameters(spot=100, rate=0.03, volatility=0.2, maturity=1.0)
    option = OptionParameters(strike=100, option_type="call")
    standard_sim = SimulationParameters(num_paths=100_000, num_steps=1, seed=123, antithetic=False)
    antithetic_sim = SimulationParameters(num_paths=100_000, num_steps=1, seed=123, antithetic=True)

    standard = price_option(market, option, standard_sim)
    antithetic = price_option(market, option, antithetic_sim)

    assert antithetic.estimator_variance < standard.estimator_variance
    assert antithetic.standard_error < standard.standard_error


def test_compare_antithetic_sampling_reports_percentage_reduction() -> None:
    market = MarketParameters(spot=100, rate=0.03, volatility=0.2, maturity=1.0)
    option = OptionParameters(strike=100, option_type="call")
    sim = SimulationParameters(num_paths=50_000, num_steps=1, seed=123)

    comparison = compare_antithetic_sampling(market, option, sim)

    assert list(comparison["method"]) == ["standard", "antithetic"]
    assert comparison.loc[1, "variance_reduction_pct"] > 0


def test_control_variate_reduces_estimator_variance_for_representative_call() -> None:
    market = MarketParameters(spot=100, rate=0.03, volatility=0.2, maturity=1.0)
    option = OptionParameters(strike=100, option_type="call")
    sim = SimulationParameters(num_paths=100_000, num_steps=1, seed=123)

    standard = price_option(market, option, sim)
    control = price_option_control_variate(market, option, sim)

    assert control.estimator_variance < standard.estimator_variance


def test_compare_variance_reduction_methods_includes_expected_methods() -> None:
    market = MarketParameters(spot=100, rate=0.03, volatility=0.2, maturity=1.0)
    option = OptionParameters(strike=100, option_type="call")
    sim = SimulationParameters(num_paths=16_384, num_steps=1, seed=123)

    comparison = compare_variance_reduction_methods(market, option, sim)

    assert set(comparison["method"]) == {
        "standard",
        "antithetic",
        "moment_matching",
        "sobol",
        "control_variate",
    }
