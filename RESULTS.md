# Results

Generated with:

```bash
python scripts/run_experiments.py
python scripts/generate_figures.py
python scripts/benchmark_performance.py
python -m ruff check .
python -m ruff format --check .
python -m mypy src
python -m pytest
python -m mkdocs build --strict
```

Runtime values are local machine measurements and will vary by hardware. Prices, errors, standard errors, and variance-reduction percentages are reproducible under the stated seeds and dependency versions.

## Main parameters

- `S0 = 100`
- `K = 100`
- `r = 0.03`
- `q = 0.00`
- `sigma = 0.20`
- `T = 1.0`
- `seed = 42`
- Main European experiment paths: `500,000`

## Monte Carlo vs Black-Scholes

| option | mc_price | standard_error | 95% CI low | 95% CI high | Black-Scholes | abs_error |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| call | 9.414024 | 0.019996 | 9.374832 | 9.453215 | 9.413403 | 0.000620 |
| put | 6.464930 | 0.013229 | 6.439002 | 6.490859 | 6.457957 | 0.006974 |

Both analytical values fall inside their Monte Carlo 95% confidence intervals.

## Parameter-grid validation

Grid:

- `K in {80, 90, 100, 110, 120}`
- `sigma in {0.10, 0.20, 0.40}`
- `T in {0.25, 0.5, 1.0, 2.0}`
- calls and puts
- `S0 = 100`, `r = 0.03`
- `100,000` paths per scenario

| metric | value |
| --- | ---: |
| total_cases | 120 |
| CI coverage | 0.991667 |
| mean_abs_error | 0.037365 |
| max_abs_error | 0.166968 |
| median_rel_error_pct | 0.524467 |

## Convergence analysis

European at-the-money call, same main parameters.

| num_paths | price | Black-Scholes | abs_error | standard_error | 95% CI width |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 1,000 | 8.881144 | 9.413403 | 0.532259 | 0.429280 | 1.682778 |
| 5,000 | 9.133390 | 9.413403 | 0.280013 | 0.197388 | 0.773761 |
| 10,000 | 9.313033 | 9.413403 | 0.100370 | 0.141626 | 0.555175 |
| 50,000 | 9.421739 | 9.413403 | 0.008335 | 0.063430 | 0.248644 |
| 100,000 | 9.387501 | 9.413403 | 0.025903 | 0.044852 | 0.175818 |
| 500,000 | 9.414024 | 9.413403 | 0.000620 | 0.019996 | 0.078383 |

The fitted log-log slope of standard error versus path count was `-0.493953`, close to the theoretical Monte Carlo rate of `-0.5`.

![Convergence error](figures/convergence_error.png)

The convergence plot shows absolute pricing error declining as path count increases, with the usual random fluctuation around the theoretical Monte Carlo rate.

## Variance reduction

Equal path budget: `500,000` simulated paths.

| method | price | standard_error | estimator_variance | variance_reduction_pct |
| --- | ---: | ---: | ---: | ---: |
| standard | 9.414024 | 0.019996 | 0.000400 | 0.000000 |
| antithetic | 9.418259 | 0.014924 | 0.000223 | 44.292597 |
| moment_matching | 9.411992 | 0.019984 | 0.000399 | 0.122448 |
| sobol | 9.413402 | 0.019956 | 0.000398 | 0.401530 |
| control_variate | 9.418073 | 0.008210 | 0.000067 | 83.141813 |

The terminal-stock control variate produced the strongest measured variance reduction in this setting. Sobol sampling is implemented, but powers of two are preferred for best quasi-Monte Carlo balance.

## Asian option examples

Arithmetic-average Asian calls average simulated monitoring dates after time zero by default. The project also includes a discrete geometric-average Asian analytical benchmark.

For `sigma = 0.20`, `T = 1.0`, `S0 = 100`, `K = 100`, `r = 0.03`, `50,000` paths:

| monitoring_steps | European call | arithmetic Asian call | geometric Asian call |
| ---: | ---: | ---: | ---: |
| 12 | 9.421739 | 5.631835 | 5.435333 |
| 52 | 9.421739 | 5.351171 | 5.166873 |
| 252 | 9.421739 | 5.293007 | 5.103063 |

Asian options require full simulated paths because the payoff depends on an average over monitoring dates. European payoffs only require terminal prices.

![Asian monitoring frequency](figures/asian_monitoring_frequency.png)

The Asian plot shows arithmetic and geometric average calls moving lower than the European call because averaging reduces payoff volatility.

## Greek validation

Finite-difference Monte Carlo Greeks reuse random numbers across bumped scenarios. The pathwise Delta estimator is included for European options.

Parameters: `250,000` paths, `seed = 77`, central spot bump `1.0`, central volatility bump `0.01`.

| greek | method | Monte Carlo | Black-Scholes | abs_error |
| --- | --- | ---: | ---: | ---: |
| delta | finite_difference | 0.598410 | 0.598706 | 0.000296 |
| delta | pathwise | 0.598649 | 0.598706 | 0.000057 |
| gamma | finite_difference | 0.019453 | 0.019333 | 0.000119 |
| vega | finite_difference | 38.711259 | 38.666812 | 0.044447 |

Greek estimates are sensitive to bump size. Very small bumps can amplify Monte Carlo noise; very large bumps can introduce finite-difference bias.

## Extension examples

These additional examples verify the expanded payoff and solver coverage:

| feature | value |
| --- | ---: |
| digital_call | 0.503884 |
| up_and_out_call | 3.430365 |
| continuous_up_and_out_call_benchmark | 3.202750 |
| sobol_brownian_bridge_call | 9.413459 |
| implied_volatility_recovered | 0.200000 |
| american_put_lsm | 6.676507 |
| heston_mean_terminal_price | 103.028807 |
| heston_mean_terminal_variance | 0.040178 |

The up-and-out barrier option requires full path simulation. The Brownian bridge example uses Sobol quasi-random draws with path construction ordered through the terminal Brownian value and conditional midpoints.
The continuous up-and-out benchmark is lower than the discretely monitored Monte Carlo barrier price because continuous monitoring detects barrier crossings between simulated dates.

## Implied-volatility smile

The project includes a synthetic implied-volatility calibration helper that recovers Black-Scholes implied volatility from option quotes.

![Implied volatility smile](figures/implied_vol_smile.png)

## Performance artifacts

`scripts/benchmark_performance.py` writes:

- `benchmarks/performance.csv`
- `benchmarks/performance.md`

These files separate local runtime benchmarking from statistical validation. Runtime values should be compared on the same machine and Python environment.

## Tooling verification

- `ruff`: all checks passed
- `mypy`: no issues in `16` source files
- `ruff format --check`: passed
- `pytest`: `43 passed`
- coverage: `85%`
- `mkdocs build --strict`: passed
- notebooks: executed in place with outputs
- notebooks: executed in CI
- figures: generated under `figures/`
- benchmark artifacts: generated under `benchmarks/`
- CLI: smoke-tested by pytest

## Fully implemented features

- Real package layout: `src/mc_options`, not a flat `src` import package.
- Validated dataclasses for market, option, and simulation parameters.
- Vectorized geometric Brownian motion terminal and full-path simulation.
- Pseudo-random, antithetic, moment-matched, and Sobol draws.
- Brownian bridge full-path construction for quasi-Monte Carlo path generation.
- European call and put payoffs.
- Arithmetic-average Asian call and put payoffs.
- Digital cash-or-nothing call and put payoffs.
- Up-and-out and down-and-out barrier call and put payoffs.
- Continuous-monitoring up-and-out analytical barrier benchmark.
- Longstaff-Schwartz American option pricing example.
- Heston stochastic-volatility path simulation.
- Synthetic implied-volatility smile calibration.
- Discrete geometric-average Asian analytical benchmark.
- Black-Scholes implied-volatility solver.
- Discounted Monte Carlo pricing with uncertainty and runtime metadata.
- Black-Scholes European call and put prices with dividend yield support.
- Put-call parity utility and zero-volatility pricing edge case.
- Convergence experiments over `1,000` to `500,000` paths.
- Variance-reduction comparison table including antithetic and control variates.
- Finite-difference Delta, Gamma, Vega; pathwise European Delta; bump-size sensitivity.
- CLI entry point.
- Runnable examples under `examples/`.
- Performance benchmark script.
- Benchmark CSV and Markdown artifacts.
- MkDocs documentation site skeleton.
- Generated API documentation through mkdocstrings.
- Pre-commit configuration.
- Changelog and contribution guide.
- Direct dev dependency lock-style file.
- Executed notebooks and saved figures.
- GitHub Actions CI for Python 3.11 and 3.12.
- Ruff, mypy, and pytest checks.

## Limitations

- GBM assumes constant volatility and lognormal returns.
- The model does not include stochastic volatility, jumps, transaction costs, discrete dividends, early exercise, or calibration to market option surfaces.
- Monte Carlo Gamma and Vega are finite-difference estimates rather than pathwise or likelihood-ratio estimators.
- Arithmetic Asian options are benchmarked qualitatively against geometric Asian options, not against a closed-form arithmetic Asian solution.

## Final verified claims

1. Verified number of simulated paths used for the main experiment: `500,000`.
2. Verified European call pricing error relative to Black-Scholes: absolute error `0.000620`, relative error about `0.0066%`.
3. Verified antithetic variance reduction: `44.292597%`.
4. Verified control-variate variance reduction: `83.141813%`.
5. Verified digital call example price: `0.503884`.
6. Verified up-and-out barrier call example price: `3.430365`.
7. Verified continuous up-and-out analytical benchmark: `3.202750`.
8. Verified Sobol Brownian-bridge call example price: `9.413459`.
9. Verified implied-volatility recovery: `0.200000`.
10. Verified American put Longstaff-Schwartz estimate: `6.676507`.
11. Verified Heston mean terminal price: `103.028807`.
12. Fully implemented features are listed above and covered by `43` passing tests with `85%` coverage.
13. Resume description:
   - Built a vectorized Python package for European, Asian, digital, barrier, and American-style option pricing under GBM, with validated dataclass inputs, reproducible seeds, a CLI, executed notebooks, and CI-ready tests.
   - Validated a `500,000`-path European call estimate against Black-Scholes with `0.000620` absolute error and empirical standard-error scaling near `1 / sqrt(N)`.
   - Implemented implied volatility, Brownian bridge paths, Heston simulation, Longstaff-Schwartz American pricing, analytical barrier benchmarking, and variance-reduction methods, with a verified control-variate run reducing estimator variance by `83.141813%`.
