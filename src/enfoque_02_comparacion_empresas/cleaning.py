"""Limpieza y preparacion para el enfoque de comparacion entre empresas."""

from __future__ import annotations

import re
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
CLEAN_PATH = PROCESSED_DIR / "company_comparison_cleaned.csv"

REVIEW_COLUMNS = [
    "Excellent Review %",
    "Average Review %",
    "Poor Review %",
]


def remove_complete_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    """Remove exact duplicate rows."""
    if not isinstance(df, pd.DataFrame):
        raise TypeError(f"Expected DataFrame, received {type(df)}")

    before = len(df)
    result = df.drop_duplicates(keep="first").reset_index(drop=True)
    removed = before - len(result)
    print(
        f"[remove_complete_duplicates] rows_before={before:,} "
        f"removed={removed:,} rows_after={len(result):,}"
    )
    return result


def normalize_company_name(name: str) -> str:
    """Normalize company names without forcing a new casing style."""
    value = re.sub(r"\s+", " ", str(name)).strip()
    return value


def normalize_component_with_dose(component: str) -> str:
    """Normalize spaces while preserving the active ingredient and dose."""
    value = re.sub(r"\s+", " ", str(component)).strip()
    value = re.sub(r"\s*\(\s*", " (", value)
    value = re.sub(r"\s*\)\s*", ")", value)
    value = re.sub(r"\s+", " ", value).strip()
    return value


def split_composition_with_dose(composition: str) -> list[str]:
    """Split a composition into normalized components, keeping doses."""
    if pd.isna(composition):
        return []

    parts = [
        normalize_component_with_dose(part)
        for part in str(composition).split("+")
    ]
    return [part for part in parts if part]


def canonicalize_composition(composition: str) -> str:
    """Create a canonical composition key so A + B == B + A."""
    parts = split_composition_with_dose(composition)
    ordered_parts = sorted(parts, key=lambda item: item.lower())
    return " + ".join(ordered_parts)


def count_side_effects(text: str) -> int:
    """Approximate the number of side effects listed in the raw text."""
    words = str(text).split()
    return sum(1 for word in words if word and word[0].isupper())


def prepare_review_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Convert review percentages to numeric values."""
    df = df.copy()
    for column in REVIEW_COLUMNS:
        if column not in df.columns:
            raise KeyError(f"Missing required column: {column}")
        df[column] = pd.to_numeric(df[column], errors="coerce")
    return df


def add_company_comparison_features(df: pd.DataFrame) -> pd.DataFrame:
    """Create derived columns used for shared-composition comparisons."""
    required_columns = {"Manufacturer", "Composition", "Side_effects", *REVIEW_COLUMNS}
    missing = required_columns - set(df.columns)
    if missing:
        raise KeyError(f"Missing required columns: {sorted(missing)}")

    df = prepare_review_columns(df)
    df = df.copy()

    df["empresa"] = df["Manufacturer"].apply(normalize_company_name)
    df["composition_parts"] = df["Composition"].apply(split_composition_with_dose)
    df["composition_key"] = df["Composition"].apply(canonicalize_composition)
    df["num_componentes"] = df["composition_parts"].apply(len)
    df["num_effects"] = df["Side_effects"].apply(count_side_effects)
    df["review_sum"] = df[REVIEW_COLUMNS].sum(axis=1)
    df["review_sum_valid"] = df["review_sum"].round(6).eq(100)

    shared_company_count = (
        df.groupby("composition_key")["empresa"]
        .nunique()
        .rename("shared_company_count")
    )
    shared_product_count = (
        df.groupby("composition_key")["Medicine Name"]
        .count()
        .rename("shared_product_count")
    )

    df = df.merge(
        shared_company_count,
        how="left",
        left_on="composition_key",
        right_index=True,
    )
    df = df.merge(
        shared_product_count,
        how="left",
        left_on="composition_key",
        right_index=True,
    )

    df["shared_company_count"] = df["shared_company_count"].fillna(0).astype(int)
    df["shared_product_count"] = df["shared_product_count"].fillna(0).astype(int)
    df["shared_company_composition"] = df["shared_company_count"] >= 2

    print(
        "[add_company_comparison_features] "
        f"unique_companies={df['empresa'].nunique():,} "
        f"shared_compositions={df['composition_key'].nunique():,}"
    )
    print(
        "[add_company_comparison_features] "
        f"compositions_shared_by_2_or_more_companies="
        f"{df.loc[df['shared_company_composition'], 'composition_key'].nunique():,}"
    )

    return df


def run_cleaning_pipeline(
    df: pd.DataFrame,
    save: bool = True,
    output_path: str | Path = CLEAN_PATH,
) -> pd.DataFrame:
    """Run the cleaning pipeline for the company comparison focus."""
    if df.empty:
        raise ValueError("The input DataFrame is empty.")

    print("=" * 60)
    print("START COMPANY COMPARISON CLEANING PIPELINE")
    print("=" * 60)

    df_clean = remove_complete_duplicates(df)
    df_clean = add_company_comparison_features(df_clean)

    print("-" * 60)
    print(f"final_shape={df_clean.shape}")
    print("=" * 60)

    if save:
        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        export_df = df_clean.copy()
        export_df["composition_parts"] = export_df["composition_parts"].astype(str)
        export_df.to_csv(output, index=False)
        print(f"[run_cleaning_pipeline] saved_csv={output}")

    return df_clean
