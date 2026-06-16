# Contributing

This is a portfolio project, but contributions and experiments should follow the same hygiene as a small production library.

## Local setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
pre-commit install
```

## Checks

Run these before opening a pull request:

```bash
python -m ruff check .
python -m ruff format --check .
python -m mypy src
python -m pytest
```

## Guidelines

- Keep numerical claims reproducible with fixed seeds.
- Add or update tests for new payoffs, estimators, and benchmarks.
- Keep notebooks as explanations; put reusable logic in `src/mc_options`.
- Avoid brittle tests that depend on a tiny Monte Carlo sample.
- Update `RESULTS.md` only after rerunning the experiment script.
