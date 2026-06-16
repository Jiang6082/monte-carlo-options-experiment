# Results

The detailed verified report lives in `RESULTS.md`.

Headline verified claims:

- `500,000` main paths.
- European call absolute error versus Black-Scholes: `0.000620`.
- Antithetic variance reduction: `44.292597%`.
- Control-variate variance reduction: `83.141813%`.
- Digital call example price: `0.503884`.
- Up-and-out barrier call example price: `3.430365`.
- Continuous up-and-out analytical benchmark: `3.202750`.
- Sobol Brownian-bridge call example price: `9.413459`.
- Implied volatility recovery: `0.200000`.
- American put Longstaff-Schwartz estimate: `6.676507`.
- Heston mean terminal price: `103.028807`.
- Test suite: `43` passing tests with `85%` coverage.
