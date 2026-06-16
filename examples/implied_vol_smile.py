"""Recover a small implied-volatility smile from synthetic option quotes."""

import pandas as pd

from mc_options.black_scholes import black_scholes_price
from mc_options.calibration import implied_vol_smile
from mc_options.models import MarketParameters, OptionParameters


def main() -> None:
    market = MarketParameters(spot=100, rate=0.03, volatility=0.20, maturity=1.0)
    quotes = pd.DataFrame(
        {
            "strike": [90, 100, 110],
            "maturity": [1.0, 1.0, 1.0],
            "price": [
                black_scholes_price(market, OptionParameters(strike=strike, option_type="call"))
                for strike in [90, 100, 110]
            ],
        }
    )
    print(implied_vol_smile(market, "call", quotes).round(6).to_string(index=False))


if __name__ == "__main__":
    main()
