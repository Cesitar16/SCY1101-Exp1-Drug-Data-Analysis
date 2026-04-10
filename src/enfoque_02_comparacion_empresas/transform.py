"""Transformaciones para comparar la misma composicion entre empresas."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
SHARED_ROWS_PATH = PROCESSED_DIR / "company_comparison_shared_rows.csv"
COMPANY_STATS_PATH = PROCESSED_DIR / "company_comparison_company_stats.csv"
VARIATION_SUMMARY_PATH = PROCESSED_DIR / "company_comparison_variation_summary.csv"
REPRESENTATIVE_COMPARISONS_PATH = (
    PROCESSED_DIR / "company_comparison_representative_comparisons.csv"
)


def _categorize_company_record_coverage(record_count: int) -> str:
    """Label how much row-level support a company has within one composition."""
    if record_count >= 4:
        return "alta"
    if record_count >= 2:
        return "media"
    return "baja"


def _categorize_comparison_strength(n_empresas: int, n_registros: int) -> str:
    """Label composition coverage strength.

    These labels describe dataset coverage only. They do not imply statistical
    significance because the dataset does not provide the number of user reviews.
    """
    if n_empresas >= 5 and n_registros >= 10:
        return "fuerte"
    if n_empresas >= 3 and n_registros >= 5:
        return "media"
    return "debil"


def build_shared_composition_dataset(df_clean: pd.DataFrame) -> pd.DataFrame:
    """Keep only rows where the same composition appears in multiple companies."""
    required_columns = {"composition_key", "shared_company_composition", "empresa"}
    missing = required_columns - set(df_clean.columns)
    if missing:
        raise KeyError(f"Missing required columns: {sorted(missing)}")

    df_shared = (
        df_clean[df_clean["shared_company_composition"]]
        .copy()
        .sort_values(["composition_key", "empresa", "Medicine Name"])
        .reset_index(drop=True)
    )

    print(
        "[build_shared_composition_dataset] "
        f"rows={len(df_shared):,} "
        f"compositions={df_shared['composition_key'].nunique():,}"
    )
    return df_shared


def build_composition_company_stats(df_shared: pd.DataFrame) -> pd.DataFrame:
    """Aggregate comparable rows by shared composition and company."""
    if df_shared.empty:
        raise ValueError("df_shared is empty.")

    company_stats = (
        df_shared.groupby(["composition_key", "empresa"], as_index=False)
        .agg(
            n_medicamentos=("Medicine Name", "count"),
            medicine_names=("Medicine Name", lambda values: " | ".join(sorted(set(values))[:5])),
            composition_example=("Composition", lambda values: sorted(set(values))[0]),
            excellent_mean=("Excellent Review %", "mean"),
            average_mean=("Average Review %", "mean"),
            poor_mean=("Poor Review %", "mean"),
            num_effects_mean=("num_effects", "mean"),
            num_componentes=("num_componentes", "max"),
            review_sum_valid_rate=("review_sum_valid", "mean"),
        )
        .round(2)
    )

    company_stats["num_componentes"] = company_stats["num_componentes"].astype(int)
    company_stats["company_record_coverage"] = company_stats["n_medicamentos"].apply(
        _categorize_company_record_coverage
    )

    composition_sizes = (
        company_stats.groupby("composition_key", as_index=False)
        .agg(
            n_empresas=("empresa", "nunique"),
            n_registros=("n_medicamentos", "sum"),
            min_registros_empresa=("n_medicamentos", "min"),
            max_registros_empresa=("n_medicamentos", "max"),
            empresas_con_un_registro=("n_medicamentos", lambda values: int((values == 1).sum())),
        )
    )
    composition_sizes["comparison_strength"] = composition_sizes.apply(
        lambda row: _categorize_comparison_strength(
            int(row["n_empresas"]),
            int(row["n_registros"]),
        ),
        axis=1,
    )

    company_stats = company_stats.merge(
        composition_sizes,
        on="composition_key",
        how="left",
    )
    company_stats["is_representative_comparison"] = (
        company_stats["comparison_strength"].isin(["media", "fuerte"])
        & company_stats["n_medicamentos"].ge(2)
    )

    print(
        "[build_composition_company_stats] "
        f"company_rows={len(company_stats):,}"
    )
    return company_stats


def build_variation_summary(company_stats: pd.DataFrame) -> pd.DataFrame:
    """Summarize cross-company variation for each shared composition."""
    if company_stats.empty:
        raise ValueError("company_stats is empty.")

    variation = (
        company_stats.groupby("composition_key", as_index=False)
        .agg(
            n_empresas=("empresa", "nunique"),
            n_registros=("n_medicamentos", "sum"),
            min_registros_empresa=("n_medicamentos", "min"),
            max_registros_empresa=("n_medicamentos", "max"),
            empresas_con_un_registro=("n_medicamentos", lambda values: int((values == 1).sum())),
            excellent_min=("excellent_mean", "min"),
            excellent_max=("excellent_mean", "max"),
            excellent_std=("excellent_mean", "std"),
            average_min=("average_mean", "min"),
            average_max=("average_mean", "max"),
            average_std=("average_mean", "std"),
            poor_min=("poor_mean", "min"),
            poor_max=("poor_mean", "max"),
            poor_std=("poor_mean", "std"),
            effect_min=("num_effects_mean", "min"),
            effect_max=("num_effects_mean", "max"),
            effect_std=("num_effects_mean", "std"),
        )
        .round(2)
    )

    variation["excellent_range"] = (
        variation["excellent_max"] - variation["excellent_min"]
    ).round(2)
    variation["average_range"] = (
        variation["average_max"] - variation["average_min"]
    ).round(2)
    variation["poor_range"] = (
        variation["poor_max"] - variation["poor_min"]
    ).round(2)
    variation["effect_range"] = (
        variation["effect_max"] - variation["effect_min"]
    ).round(2)
    variation["max_review_range"] = (
        variation[["excellent_range", "average_range", "poor_range"]].max(axis=1)
    ).round(2)
    variation["comparison_strength"] = variation.apply(
        lambda row: _categorize_comparison_strength(
            int(row["n_empresas"]),
            int(row["n_registros"]),
        ),
        axis=1,
    )

    strength_rank = {"fuerte": 2, "media": 1, "debil": 0}
    variation = variation.assign(
        _strength_rank=variation["comparison_strength"].map(strength_rank)
    )
    variation = variation.sort_values(
        ["_strength_rank", "n_empresas", "n_registros", "max_review_range", "effect_range"],
        ascending=[False, False, False, False, False],
    ).drop(columns="_strength_rank")
    variation = variation.reset_index(drop=True)

    print(
        "[build_variation_summary] "
        f"rows={len(variation):,}"
    )
    return variation


def build_representative_comparisons(
    company_stats: pd.DataFrame,
    allowed_strengths: Iterable[str] = ("media", "fuerte"),
    min_company_records: int = 2,
) -> pd.DataFrame:
    """Filter company-composition comparisons with better dataset coverage."""
    allowed = set(allowed_strengths)
    representative = (
        company_stats[
            company_stats["comparison_strength"].isin(allowed)
            & company_stats["n_medicamentos"].ge(min_company_records)
        ]
        .copy()
        .sort_values(
            ["comparison_strength", "n_empresas", "n_registros", "n_medicamentos"],
            ascending=[False, False, False, False],
        )
        .reset_index(drop=True)
    )

    print(
        "[build_representative_comparisons] "
        f"rows={len(representative):,} "
        f"compositions={representative['composition_key'].nunique():,}"
    )
    return representative


def run_transform_pipeline(
    df_clean: pd.DataFrame,
    save: bool = True,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Run the transformation pipeline for company comparison."""
    if df_clean.empty:
        raise ValueError("The input DataFrame is empty.")

    print("=" * 60)
    print("START COMPANY COMPARISON TRANSFORM PIPELINE")
    print("=" * 60)

    df_shared = build_shared_composition_dataset(df_clean)
    company_stats = build_composition_company_stats(df_shared)
    variation_summary = build_variation_summary(company_stats)
    representative_comparisons = build_representative_comparisons(company_stats)

    print("-" * 60)
    print(f"shared_rows_shape={df_shared.shape}")
    print(f"company_stats_shape={company_stats.shape}")
    print(f"variation_summary_shape={variation_summary.shape}")
    print(f"representative_comparisons_shape={representative_comparisons.shape}")
    print("=" * 60)

    if save:
        PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

        export_shared = df_shared.copy()
        export_shared["composition_parts"] = export_shared["composition_parts"].astype(str)
        export_shared.to_csv(SHARED_ROWS_PATH, index=False)
        company_stats.to_csv(COMPANY_STATS_PATH, index=False)
        variation_summary.to_csv(VARIATION_SUMMARY_PATH, index=False)
        representative_comparisons.to_csv(REPRESENTATIVE_COMPARISONS_PATH, index=False)

        print(f"[run_transform_pipeline] saved_csv={SHARED_ROWS_PATH}")
        print(f"[run_transform_pipeline] saved_csv={COMPANY_STATS_PATH}")
        print(f"[run_transform_pipeline] saved_csv={VARIATION_SUMMARY_PATH}")
        print(f"[run_transform_pipeline] saved_csv={REPRESENTATIVE_COMPARISONS_PATH}")

    return df_shared, company_stats, variation_summary, representative_comparisons
