"""Compare several Monte Carlo variance-reduction methods."""

from mc_options.models import MarketParameters, OptionParameters, SimulationParameters
from mc_options.variance_reduction import compare_variance_reduction_methods


def main() -> None:
    market = MarketParameters(spot=100, rate=0.03, volatility=0.20, maturity=1.0)
    option = OptionParameters(strike=100, option_type="call")
    sim = SimulationParameters(num_paths=100_000, num_steps=1, seed=42)

    comparison = compare_variance_reduction_methods(market, option, sim)
    print(
        comparison[["method", "price", "standard_error", "variance_reduction_pct"]].to_string(
            index=False
        )
    )


if __name__ == "__main__":
    main()
