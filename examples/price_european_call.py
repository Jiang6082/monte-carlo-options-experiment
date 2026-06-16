"""Price a European call and compare against Black-Scholes."""

from mc_options.black_scholes import black_scholes_price
from mc_options.models import MarketParameters, OptionParameters, SimulationParameters
from mc_options.pricer import price_option


def main() -> None:
    market = MarketParameters(spot=100, rate=0.03, volatility=0.20, maturity=1.0)
    option = OptionParameters(strike=100, option_type="call")
    sim = SimulationParameters(num_paths=100_000, num_steps=1, seed=42)

    result = price_option(market, option, sim)
    benchmark = black_scholes_price(market, option)

    print(f"Monte Carlo price: {result.price:.6f}")
    print(f"Black-Scholes price: {benchmark:.6f}")
    print(f"Absolute error: {abs(result.price - benchmark):.6f}")
    print(f"95% CI: [{result.ci_low:.6f}, {result.ci_high:.6f}]")


if __name__ == "__main__":
    main()
