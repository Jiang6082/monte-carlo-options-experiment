"""Command-line interface for the options pricing engine."""

from __future__ import annotations

import argparse
from dataclasses import asdict

from mc_options.black_scholes import black_scholes_price
from mc_options.implied_vol import implied_volatility
from mc_options.models import MarketParameters, OptionParameters, SimulationParameters
from mc_options.pricer import price_option


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Price options with Monte Carlo simulation.")
    subparsers = parser.add_subparsers(dest="command")

    price_parser = subparsers.add_parser("price", help="Price an option with Monte Carlo.")
    _add_common_option_arguments(price_parser)
    price_parser.add_argument("--paths", type=int, default=100_000)
    price_parser.add_argument("--steps", type=int, default=1)
    price_parser.add_argument("--seed", type=int, default=42)
    price_parser.add_argument("--antithetic", action="store_true")
    price_parser.add_argument("--moment-matching", action="store_true")
    price_parser.add_argument("--brownian-bridge", action="store_true")
    price_parser.add_argument("--random-method", choices=["pseudo", "sobol"], default="pseudo")

    iv_parser = subparsers.add_parser(
        "implied-vol", help="Recover Black-Scholes implied volatility."
    )
    _add_common_option_arguments(iv_parser)
    iv_parser.add_argument("--target-price", type=float, required=True)

    _add_common_option_arguments(parser)
    parser.add_argument("--paths", type=int, default=100_000)
    parser.add_argument("--steps", type=int, default=1)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--antithetic", action="store_true")
    parser.add_argument("--moment-matching", action="store_true")
    parser.add_argument("--brownian-bridge", action="store_true")
    parser.add_argument("--random-method", choices=["pseudo", "sobol"], default="pseudo")
    return parser


def _add_common_option_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--spot", type=float, default=100.0)
    parser.add_argument("--strike", type=float, default=100.0)
    parser.add_argument("--rate", type=float, default=0.03)
    parser.add_argument("--volatility", type=float, default=0.20)
    parser.add_argument("--maturity", type=float, default=1.0)
    parser.add_argument("--dividend-yield", type=float, default=0.0)
    parser.add_argument("--option-type", choices=["call", "put"], default="call")
    parser.add_argument(
        "--payoff-type",
        choices=["european", "asian", "digital", "barrier"],
        default="european",
    )
    parser.add_argument("--digital-cash", type=float, default=1.0)
    parser.add_argument("--barrier-level", type=float, default=None)
    parser.add_argument("--barrier-type", choices=["up-and-out", "down-and-out"], default=None)


def main() -> None:
    args = build_parser().parse_args()
    command = args.command or "price"
    market = MarketParameters(
        spot=args.spot,
        rate=args.rate,
        volatility=args.volatility,
        maturity=args.maturity,
        dividend_yield=args.dividend_yield,
    )
    option = OptionParameters(
        strike=args.strike,
        option_type=args.option_type,
        payoff_type=args.payoff_type,
        digital_cash=args.digital_cash,
        barrier_level=args.barrier_level,
        barrier_type=args.barrier_type,
    )
    if command == "implied-vol":
        print(f"implied_volatility: {implied_volatility(market, option, args.target_price):.6f}")
        return

    sim = SimulationParameters(
        num_paths=args.paths,
        num_steps=args.steps,
        seed=args.seed,
        antithetic=args.antithetic,
        moment_matching=args.moment_matching,
        random_method=args.random_method,
        brownian_bridge=args.brownian_bridge,
    )

    result = price_option(market, option, sim)
    print("Monte Carlo result")
    for key, value in asdict(result).items():
        print(f"{key}: {value:.6f}" if isinstance(value, float) else f"{key}: {value}")

    if option.payoff_type == "european":
        print(f"black_scholes: {black_scholes_price(market, option):.6f}")


if __name__ == "__main__":
    main()
