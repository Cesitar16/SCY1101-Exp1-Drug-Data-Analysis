"""Analisis y visualizacion para el enfoque de comparacion entre empresas."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

import matplotlib.pyplot as plt
import pandas as pd
from IPython.display import display


PROJECT_ROOT = Path(__file__).resolve().parents[2]
FIGURES_DIR = PROJECT_ROOT / "outputs" / "figures"
TABLES_DIR = PROJECT_ROOT / "outputs" / "tables"

plt.rcParams.update(
    {
        "figure.dpi": 120,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "font.size": 11,
    }
)


def _save_figure(fig: plt.Figure, filename: str) -> None:
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    path = FIGURES_DIR / f"{filename}.png"
    fig.savefig(path, bbox_inches="tight")
    display(fig)
    plt.close(fig)
    print(f"[analysis] saved_figure={path}")


def _save_table(df: pd.DataFrame, filename: str) -> None:
    TABLES_DIR.mkdir(parents=True, exist_ok=True)
    path = TABLES_DIR / f"{filename}.csv"
    df.to_csv(path, index=False)
    print(f"[analysis] saved_table={path}")


def _sort_by_strength(df: pd.DataFrame) -> pd.DataFrame:
    strength_order = {"fuerte": 2, "media": 1, "debil": 0}
    return (
        df.assign(_strength_rank=df["comparison_strength"].map(strength_order))
        .sort_values(
            ["_strength_rank", "n_empresas", "n_registros"],
            ascending=[False, False, False],
        )
        .drop(columns="_strength_rank")
    )


def plot_top_shared_compositions(
    variation_summary: pd.DataFrame,
    top_n: int = 15,
) -> pd.DataFrame:
    """Plot compositions sold by the largest number of companies."""
    ranking = (
        _sort_by_strength(variation_summary)
        .head(top_n)
        .reset_index(drop=True)
    )

    fig, ax = plt.subplots(figsize=(11, 8))
    ax.barh(
        ranking["composition_key"][::-1],
        ranking["n_empresas"][::-1],
        color="#4C78A8",
        edgecolor="white",
    )
    ax.set_title("Composiciones compartidas con mayor cobertura", fontweight="bold")
    ax.set_xlabel("Numero de empresas")
    ax.set_ylabel("")

    _save_figure(fig, "company_comparison_top_shared_compositions")
    _save_table(ranking, "company_comparison_top_shared_compositions")
    return ranking


def plot_comparison_strength_distribution(
    variation_summary: pd.DataFrame,
) -> pd.DataFrame:
    """Summarize coverage strength across shared compositions."""
    summary = (
        variation_summary["comparison_strength"]
        .value_counts()
        .rename_axis("comparison_strength")
        .reset_index(name="n_composiciones")
    )
    order = pd.Categorical(summary["comparison_strength"], ["debil", "media", "fuerte"], ordered=True)
    summary = summary.assign(comparison_strength=order).sort_values("comparison_strength")
    summary["comparison_strength"] = summary["comparison_strength"].astype(str)

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(
        summary["comparison_strength"],
        summary["n_composiciones"],
        color=["#E45756", "#ECAE3C", "#54A24B"],
        edgecolor="white",
    )
    ax.set_title("Distribucion de fortaleza de comparacion", fontweight="bold")
    ax.set_xlabel("comparison_strength")
    ax.set_ylabel("Numero de composiciones")

    _save_figure(fig, "company_comparison_strength_distribution")
    _save_table(summary, "company_comparison_strength_distribution")
    return summary.reset_index(drop=True)


def plot_review_variation(
    variation_summary: pd.DataFrame,
    top_n: int = 12,
    allowed_strengths: Iterable[str] = ("media", "fuerte"),
) -> pd.DataFrame:
    """Plot shared compositions with the largest review variation."""
    allowed = set(allowed_strengths)
    ranking = (
        variation_summary[variation_summary["comparison_strength"].isin(allowed)]
        .sort_values(
            ["max_review_range", "n_empresas", "n_registros"],
            ascending=[False, False, False],
        )
        .head(top_n)
        .reset_index(drop=True)
    )

    fig, ax = plt.subplots(figsize=(12, 8))
    plot_df = ranking.set_index("composition_key")[
        ["excellent_range", "average_range", "poor_range"]
    ]
    plot_df.iloc[::-1].plot(
        kind="barh",
        ax=ax,
        color=["#54A24B", "#ECAE3C", "#E45756"],
        edgecolor="white",
    )
    ax.set_title("Variacion de reviews dentro de composiciones comparables", fontweight="bold")
    ax.set_xlabel("Rango entre empresas")
    ax.set_ylabel("")
    ax.legend(title="Metricas")

    _save_figure(fig, "company_comparison_review_variation")
    _save_table(ranking, "company_comparison_review_variation")
    return ranking


def plot_side_effect_variation(
    variation_summary: pd.DataFrame,
    top_n: int = 15,
    allowed_strengths: Iterable[str] = ("media", "fuerte"),
) -> pd.DataFrame:
    """Plot compositions with the largest side-effect variation across companies."""
    allowed = set(allowed_strengths)
    ranking = (
        variation_summary[variation_summary["comparison_strength"].isin(allowed)]
        .sort_values(
            ["effect_range", "n_empresas", "n_registros"],
            ascending=[False, False, False],
        )
        .head(top_n)
        .reset_index(drop=True)
    )

    fig, ax = plt.subplots(figsize=(11, 8))
    ax.barh(
        ranking["composition_key"][::-1],
        ranking["effect_range"][::-1],
        color="#F58518",
        edgecolor="white",
    )
    ax.set_title("Variacion de efectos estimados en composiciones comparables", fontweight="bold")
    ax.set_xlabel("Rango de efectos promedio")
    ax.set_ylabel("")

    _save_figure(fig, "company_comparison_side_effect_variation")
    _save_table(ranking, "company_comparison_side_effect_variation")
    return ranking


def build_representative_overview(
    company_stats: pd.DataFrame,
    representative_comparisons: pd.DataFrame,
    variation_summary: pd.DataFrame,
) -> pd.DataFrame:
    """Summarize how much of the shared data remains after coverage filtering."""
    summary = pd.DataFrame(
        {
            "metric": [
                "shared_compositions_total",
                "shared_company_rows_total",
                "representative_compositions",
                "representative_company_rows",
                "strong_compositions",
                "medium_compositions",
            ],
            "value": [
                int(variation_summary["composition_key"].nunique()),
                int(len(company_stats)),
                int(representative_comparisons["composition_key"].nunique()),
                int(len(representative_comparisons)),
                int((variation_summary["comparison_strength"] == "fuerte").sum()),
                int((variation_summary["comparison_strength"] == "media").sum()),
            ],
        }
    )
    _save_table(summary, "company_comparison_representative_overview")
    return summary


def extract_case_studies(
    representative_comparisons: pd.DataFrame,
    variation_summary: pd.DataFrame,
    top_n: int = 5,
) -> pd.DataFrame:
    """Return case studies from comparisons with better coverage."""
    target_compositions = (
        variation_summary[variation_summary["comparison_strength"].isin(["media", "fuerte"])]
        .sort_values(
            ["max_review_range", "effect_range", "n_empresas", "n_registros"],
            ascending=[False, False, False, False],
        )
        .head(top_n)["composition_key"]
        .tolist()
    )

    case_studies = (
        representative_comparisons[
            representative_comparisons["composition_key"].isin(target_compositions)
        ]
        .sort_values(["composition_key", "excellent_mean", "poor_mean"], ascending=[True, False, True])
        .reset_index(drop=True)
    )
    _save_table(case_studies, "company_comparison_case_studies")
    return case_studies


def run_analysis_pipeline(
    company_stats: pd.DataFrame,
    variation_summary: pd.DataFrame,
    representative_comparisons: pd.DataFrame,
) -> dict[str, pd.DataFrame]:
    """Run the analysis pipeline for the company comparison focus."""
    if company_stats.empty or variation_summary.empty or representative_comparisons.empty:
        raise ValueError(
            "company_stats, variation_summary and representative_comparisons must not be empty."
        )

    print("=" * 60)
    print("START COMPANY COMPARISON ANALYSIS PIPELINE")
    print("=" * 60)

    top_shared = plot_top_shared_compositions(variation_summary, top_n=15)
    strength_distribution = plot_comparison_strength_distribution(variation_summary)
    review_variation = plot_review_variation(variation_summary, top_n=12)
    effect_variation = plot_side_effect_variation(variation_summary, top_n=15)
    representative_overview = build_representative_overview(
        company_stats,
        representative_comparisons,
        variation_summary,
    )
    case_studies = extract_case_studies(
        representative_comparisons,
        variation_summary,
        top_n=5,
    )

    print("=" * 60)
    print("COMPANY COMPARISON ANALYSIS COMPLETE")
    print("=" * 60)

    return {
        "top_shared": top_shared,
        "strength_distribution": strength_distribution,
        "review_variation": review_variation,
        "effect_variation": effect_variation,
        "representative_overview": representative_overview,
        "representative_comparisons": representative_comparisons,
        "case_studies": case_studies,
    }
