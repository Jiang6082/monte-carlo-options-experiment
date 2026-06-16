"""Simulate Heston stochastic-volatility paths."""

from mc_options.models import MarketParameters, SimulationParameters
from mc_options.stochastic_vol import HestonParameters, simulate_heston_paths


def main() -> None:
    market = MarketParameters(spot=100, rate=0.03, volatility=0.20, maturity=1.0)
    heston = HestonParameters(
        initial_variance=0.04,
        kappa=2.0,
        theta=0.04,
        vol_of_vol=0.3,
        rho=-0.5,
    )
    sim = SimulationParameters(num_paths=5_000, num_steps=52, seed=42)
    prices, variances = simulate_heston_paths(market, heston, sim)

    print(f"Mean terminal price: {prices[:, -1].mean():.6f}")
    print(f"Mean terminal variance: {variances[:, -1].mean():.6f}")


if __name__ == "__main__":
    main()
