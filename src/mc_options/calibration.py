"""Small implied-volatility calibration helpers."""

from __future__ import annotations

from dataclasses import replace
from typing import cast

import pandas as pd

from mc_options.implied_vol import implied_volatility
from mc_options.models import MarketParameters, OptionParameters, OptionType


def implied_vol_smile(
    market: MarketParameters,
    option_type: str,
    quotes: pd.DataFrame,
) -> pd.DataFrame:
    """Recover implied volatility for rows with strike, maturity, and price."""

    if option_type not in {"call", "put"}:
        raise ValueError("option_type must be 'call' or 'put'")
    typed_option_type = cast(OptionType, option_type)
    required = {"strike", "maturity", "price"}
    missing = required - set(quotes.columns)
    if missing:
        raise ValueError(f"quotes are missing required columns: {sorted(missing)}")

    rows = []
    for quote in quotes.itertuples(index=False):
        shifted_market = replace(market, maturity=float(quote.maturity))
        option = OptionParameters(strike=float(quote.strike), option_type=typed_option_type)
        rows.append(
            {
                "strike": float(quote.strike),
                "maturity": float(quote.maturity),
                "price": float(quote.price),
                "implied_volatility": implied_volatility(
                    shifted_market,
                    option,
                    float(quote.price),
                ),
            }
        )
    return pd.DataFrame(rows)
