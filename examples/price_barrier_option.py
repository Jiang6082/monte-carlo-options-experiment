"""Price an up-and-out barrier call using full-path simulation."""

from mc_options.models import MarketParameters, OptionParameters, SimulationParameters
from mc_options.pricer import price_option


def main() -> None:
    market = MarketParameters(spot=100, rate=0.03, volatility=0.20, maturity=1.0)
    option = OptionParameters(
        strike=100,
        option_type="call",
        payoff_type="barrier",
        barrier_type="up-and-out",
        barrier_level=130,
    )
    sim = SimulationParameters(num_paths=100_000, num_steps=252, seed=42)

    result = price_option(market, option, sim)
    print(f"Up-and-out call price: {result.price:.6f}")
    print(f"Standard error: {result.standard_error:.6f}")


if __name__ == "__main__":
    main()
