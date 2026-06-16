# Examples

Run a European call from the command line:

```bash
mc-options price --spot 100 --strike 100 --rate 0.03 --volatility 0.20 --maturity 1 --paths 100000
```

Recover implied volatility:

```bash
mc-options implied-vol --spot 100 --strike 100 --rate 0.03 --maturity 1 --target-price 9.413403
```

Compare variance reduction:

```bash
python examples/compare_variance_reduction.py
```

Price an American put:

```bash
python examples/price_american_put.py
```

Recover a synthetic implied-volatility smile:

```bash
python examples/implied_vol_smile.py
```

Launch the visual dashboard:

```bash
python scripts/generate_dashboard_data.py
python scripts/serve_dashboard.py
```

Open `http://127.0.0.1:8877`.
