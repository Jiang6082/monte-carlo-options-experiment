# Methodology

The stock follows risk-neutral geometric Brownian motion:

```text
dS_t = (r - q) S_t dt + sigma S_t dW_t
```

The simulator uses the exact lognormal update. European and digital options only need terminal prices. Asian and barrier options require full simulated paths.

Variance reduction methods include antithetic variates, moment matching, Sobol quasi-random draws, Brownian bridge path construction, and a terminal-stock control variate.

Additional numerical methods include a reflection-principle continuous barrier benchmark, Longstaff-Schwartz regression for American exercise, Heston full-truncation Euler simulation, and Black-Scholes implied-volatility inversion.
