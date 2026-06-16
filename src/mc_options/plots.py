"""Plotting helpers for validation notebooks."""

from __future__ import annotations

import matplotlib.pyplot as plt
import pandas as pd


def plot_convergence(convergence: pd.DataFrame) -> tuple[plt.Figure, plt.Figure, plt.Figure]:
    fig_error, ax_error = plt.subplots(figsize=(7, 4))
    ax_error.loglog(convergence["num_paths"], convergence["abs_error"], marker="o")
    ax_error.set_xlabel("Number of paths")
    ax_error.set_ylabel("Absolute pricing error")
    ax_error.set_title("European Option Pricing Error")
    ax_error.grid(True, which="both", alpha=0.3)

    fig_ci, ax_ci = plt.subplots(figsize=(7, 4))
    ax_ci.loglog(convergence["num_paths"], convergence["ci_width"], marker="o", color="tab:green")
    ax_ci.set_xlabel("Number of paths")
    ax_ci.set_ylabel("95% confidence interval width")
    ax_ci.set_title("Monte Carlo Confidence Interval Width")
    ax_ci.grid(True, which="both", alpha=0.3)

    fig_runtime, ax_runtime = plt.subplots(figsize=(7, 4))
    ax_runtime.plot(
        convergence["num_paths"], convergence["runtime_seconds"], marker="o", color="tab:red"
    )
    ax_runtime.set_xlabel("Number of paths")
    ax_runtime.set_ylabel("Runtime (seconds)")
    ax_runtime.set_title("Runtime by Path Count")
    ax_runtime.grid(True, alpha=0.3)
    return fig_error, fig_ci, fig_runtime
