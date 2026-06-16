import pytest

from mc_options.models import MarketParameters, OptionParameters, SimulationParameters


def test_market_parameters_validate_positive_inputs() -> None:
    with pytest.raises(ValueError):
        MarketParameters(spot=0, rate=0.03, volatility=0.2, maturity=1.0)

    with pytest.raises(ValueError):
        MarketParameters(spot=100, rate=0.03, volatility=-0.2, maturity=1.0)

    with pytest.raises(ValueError):
        MarketParameters(spot=100, rate=0.03, volatility=0.2, maturity=0)


def test_option_parameters_validate_contract_fields() -> None:
    with pytest.raises(ValueError):
        OptionParameters(strike=0)

    with pytest.raises(ValueError):
        OptionParameters(strike=100, option_type="invalid")  # type: ignore[arg-type]

    with pytest.raises(ValueError):
        OptionParameters(strike=100, payoff_type="invalid")  # type: ignore[arg-type]

    with pytest.raises(ValueError):
        OptionParameters(strike=100, payoff_type="digital", digital_cash=0)

    with pytest.raises(ValueError):
        OptionParameters(strike=100, payoff_type="barrier")


def test_simulation_parameters_validate_counts_seed_and_antithetic_paths() -> None:
    with pytest.raises(ValueError):
        SimulationParameters(num_paths=1, num_steps=10)

    with pytest.raises(ValueError):
        SimulationParameters(num_paths=1_000, num_steps=0)

    with pytest.raises(ValueError):
        SimulationParameters(num_paths=999, num_steps=10, antithetic=True)

    with pytest.raises(ValueError):
        SimulationParameters(num_paths=1_000, num_steps=10, random_method="invalid")  # type: ignore[arg-type]

    with pytest.raises(ValueError):
        SimulationParameters(num_paths=1_000, num_steps=1, brownian_bridge=True)
