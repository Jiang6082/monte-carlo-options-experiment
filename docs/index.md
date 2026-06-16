# Monte Carlo Options Pricing Engine

`mc_options` is a compact quantitative finance package for Monte Carlo option pricing under geometric Brownian motion.

It includes European, Asian, digital, and barrier payoffs; Black-Scholes validation; variance reduction; Greeks; implied volatility; and reproducible experiments.

## Quick start

```bash
python -m pip install -e ".[dev]"
python scripts/run_experiments.py
python -m pytest
```
