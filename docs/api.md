# API

Core modules:

- `mc_options.models`: dataclasses for market, option, and simulation parameters.
- `mc_options.simulation`: terminal and full-path GBM simulation.
- `mc_options.payoffs`: payoff functions and dispatch.
- `mc_options.pricer`: discounted Monte Carlo pricing result.
- `mc_options.black_scholes`: analytical European prices and Greeks.
- `mc_options.implied_vol`: Black-Scholes implied-volatility solver.
- `mc_options.variance_reduction`: antithetic, control-variate, moment-matching, and Sobol comparisons.
- `mc_options.asian_benchmarks`: geometric Asian benchmark.
- `mc_options.greeks`: finite-difference and pathwise Greek estimators.

## Generated Reference

::: mc_options.models

::: mc_options.pricer

::: mc_options.black_scholes

::: mc_options.implied_vol

::: mc_options.barrier_analytical

::: mc_options.american

::: mc_options.stochastic_vol

::: mc_options.calibration
