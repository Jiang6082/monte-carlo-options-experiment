"""Black-Scholes prices and Greeks for European options with dividends."""

from __future__ import annotations

import math

from scipy.stats import norm

from mc_options.models import MarketParameters, OptionParameters


def _d1_d2(market: MarketParameters, strike: float) -> tuple[float, float]:
    if market.volatility == 0:
        raise ValueError("Black-Scholes d1/d2 are undefined for zero volatility")
    numerator = (
        math.log(market.spot / strike)
        + (market.rate - market.dividend_yield + 0.5 * market.volatility**2) * market.maturity
    )
    denominator = market.volatility * math.sqrt(market.maturity)
    d1 = numerator / denominator
    d2 = d1 - denominator
    return d1, d2


def black_scholes_price(market: MarketParameters, option: OptionParameters) -> float:
    if option.payoff_type != "european":
        raise ValueError("Black-Scholes benchmark is only available for European options")

    if market.volatility == 0:
        forward_intrinsic = _zero_volatility_price(market, option)
        return forward_intrinsic

    d1, d2 = _d1_d2(market, option.strike)
    discounted_spot = market.spot * math.exp(-market.dividend_yield * market.maturity)
    discounted_strike = option.strike * math.exp(-market.rate * market.maturity)

    if option.option_type == "call":
        return discounted_spot * norm.cdf(d1) - discounted_strike * norm.cdf(d2)
    return discounted_strike * norm.cdf(-d2) - discounted_spot * norm.cdf(-d1)


def put_call_parity_residual(
    market: MarketParameters,
    call: OptionParameters,
    put: OptionParameters,
) -> float:
    call_price = black_scholes_price(market, call)
    put_price = black_scholes_price(market, put)
    discounted_spot = market.spot * math.exp(-market.dividend_yield * market.maturity)
    discounted_strike = call.strike * math.exp(-market.rate * market.maturity)
    return call_price - put_price - discounted_spot + discounted_strike


def black_scholes_delta(market: MarketParameters, option: OptionParameters) -> float:
    if market.volatility == 0:
        raise ValueError("Analytical delta is discontinuous at zero volatility")
    d1, _ = _d1_d2(market, option.strike)
    dividend_discount = math.exp(-market.dividend_yield * market.maturity)
    if option.option_type == "call":
        return dividend_discount * norm.cdf(d1)
    return dividend_discount * (norm.cdf(d1) - 1.0)


def black_scholes_gamma(market: MarketParameters, option: OptionParameters) -> float:
    if market.volatility == 0:
        raise ValueError("Analytical gamma is undefined at zero volatility")
    d1, _ = _d1_d2(market, option.strike)
    numerator = math.exp(-market.dividend_yield * market.maturity) * norm.pdf(d1)
    denominator = market.spot * market.volatility * math.sqrt(market.maturity)
    return numerator / denominator


def black_scholes_vega(market: MarketParameters, option: OptionParameters) -> float:
    if market.volatility == 0:
        raise ValueError("Analytical vega is undefined at zero volatility")
    d1, _ = _d1_d2(market, option.strike)
    return (
        market.spot
        * math.exp(-market.dividend_yield * market.maturity)
        * norm.pdf(d1)
        * math.sqrt(market.maturity)
    )


def _zero_volatility_price(market: MarketParameters, option: OptionParameters) -> float:
    forward = market.spot * math.exp((market.rate - market.dividend_yield) * market.maturity)
    if option.option_type == "call":
        payoff = max(forward - option.strike, 0.0)
    else:
        payoff = max(option.strike - forward, 0.0)
    return math.exp(-market.rate * market.maturity) * payoff
