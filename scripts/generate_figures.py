"""Generate static figures used by the README and RESULTS report."""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
import pandas as pd

matplotlib.use("Agg")

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.run_experiments import asian_examples, convergence_analysis  # noqa: E402

from mc_options.black_scholes import black_scholes_price  # noqa: E402
from mc_options.calibration import implied_vol_smile  # noqa: E402
from mc_options.models import MarketParameters, OptionParameters, SimulationParameters  # noqa: E402
from mc_options.plots import plot_convergence  # noqa: E402
from mc_options.pricer import price_option  # noqa: E402


def main() -> None:
    figures_dir = REPO_ROOT / "figures"
    figures_dir.mkdir(exist_ok=True)

    convergence = convergence_analysis()
    fig_error, fig_ci, fig_runtime = plot_convergence(convergence)
    fig_error.savefig(figures_dir / "convergence_error.png", dpi=160, bbox_inches="tight")
    fig_ci.savefig(figures_dir / "confidence_interval_width.png", dpi=160, bbox_inches="tight")
    fig_runtime.savefig(figures_dir / "runtime_by_paths.png", dpi=160, bbox_inches="tight")
    plt.close(fig_error)
    plt.close(fig_ci)
    plt.close(fig_runtime)

    asian = asian_examples().query("sigma == 0.2 and maturity == 1.0")
    fig_asian, ax_asian = plt.subplots(figsize=(7, 4))
    ax_asian.plot(
        asian["monitoring_steps"], asian["asian_call"], marker="o", label="Arithmetic Asian"
    )
    ax_asian.plot(
        asian["monitoring_steps"],
        asian["geometric_asian_call"],
        marker="s",
        label="Geometric Asian benchmark",
    )
    ax_asian.set_xlabel("Monitoring steps")
    ax_asian.set_ylabel("Call price")
    ax_asian.set_title("Asian Call Price by Averaging Frequency")
    ax_asian.grid(True, alpha=0.3)
    ax_asian.legend()
    fig_asian.savefig(figures_dir / "asian_monitoring_frequency.png", dpi=160, bbox_inches="tight")
    plt.close(fig_asian)

    market = MarketParameters(spot=100, rate=0.03, volatility=0.2, maturity=1.0)
    option = OptionParameters(strike=100, option_type="call")
    rows = []
    for spot in [80, 90, 100, 110, 120]:
        shifted = MarketParameters(spot=spot, rate=0.03, volatility=0.2, maturity=1.0)
        result = price_option(
            shifted,
            option,
            SimulationParameters(num_paths=100_000, num_steps=1, seed=42),
        )
        rows.append((spot, result.price))

    fig_prices, ax_prices = plt.subplots(figsize=(7, 4))
    ax_prices.plot([row[0] for row in rows], [row[1] for row in rows], marker="o")
    ax_prices.axvline(market.spot, color="black", linewidth=1, alpha=0.5)
    ax_prices.set_xlabel("Spot price")
    ax_prices.set_ylabel("European call price")
    ax_prices.set_title("Call Price Monotonicity")
    ax_prices.grid(True, alpha=0.3)
    fig_prices.savefig(figures_dir / "call_price_by_spot.png", dpi=160, bbox_inches="tight")
    plt.close(fig_prices)

    smile_quotes = []
    for strike in [80, 90, 100, 110, 120]:
        quoted_vol = 0.18 + 0.00008 * (strike - 100) ** 2
        quote_market = MarketParameters(spot=100, rate=0.03, volatility=quoted_vol, maturity=1.0)
        smile_quotes.append(
            {
                "strike": strike,
                "maturity": 1.0,
                "price": black_scholes_price(
                    quote_market,
                    OptionParameters(strike=strike, option_type="call"),
                ),
            }
        )
    smile = implied_vol_smile(market, "call", pd.DataFrame(smile_quotes))
    fig_smile, ax_smile = plt.subplots(figsize=(7, 4))
    ax_smile.plot(smile["strike"], smile["implied_volatility"], marker="o")
    ax_smile.set_xlabel("Strike")
    ax_smile.set_ylabel("Implied volatility")
    ax_smile.set_title("Synthetic Implied-Volatility Smile")
    ax_smile.grid(True, alpha=0.3)
    fig_smile.savefig(figures_dir / "implied_vol_smile.png", dpi=160, bbox_inches="tight")
    plt.close(fig_smile)

    print(f"Saved figures to {figures_dir}")


if __name__ == "__main__":
    main()
