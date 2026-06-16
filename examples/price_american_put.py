"""Price an American put with Longstaff-Schwartz regression."""

from mc_options.american import price_american_lsm
from mc_options.black_scholes import black_scholes_price
from mc_options.models import MarketParameters, OptionParameters, SimulationParameters


def main() -> None:
    market = MarketParameters(spot=100, rate=0.03, volatility=0.20, maturity=1.0)
    option = OptionParameters(strike=100, option_type="put")
    sim = SimulationParameters(num_paths=50_000, num_steps=50, seed=42)

    american = price_american_lsm(market, option, sim)
    european = black_scholes_price(market, option)
    print(f"American put LSM: {american:.6f}")
    print(f"European put Black-Scholes: {european:.6f}")


if __name__ == "__main__":
    main()
