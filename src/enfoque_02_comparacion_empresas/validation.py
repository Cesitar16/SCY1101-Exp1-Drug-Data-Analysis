from __future__ import annotations

from typing import Any

import pandas as pd


REQUIRED_COLUMNS: list[str] = [
    "Medicine Name",
    "Composition",
    "Uses",
    "Side_effects",
    "Manufacturer",
    "Excellent Review %",
    "Average Review %",
    "Poor Review %",
]

REVIEW_COLUMNS: list[str] = [
    "Excellent Review %",
    "Average Review %",
    "Poor Review %",
]


def ensure_required_columns(df: pd.DataFrame) -> None:
    """Raise if the manufacturer focus cannot be built from the DataFrame."""
    missing = [column for column in REQUIRED_COLUMNS if column not in df.columns]
    if missing:
        raise KeyError(
            "Faltan columnas requeridas para el enfoque 2: "
            + ", ".join(missing)
        )


def validate_review_percentages(
    df: pd.DataFrame,
    *,
    tolerance: float = 1.0,
) -> pd.DataFrame:
    """Return rows whose review percentages do not sum close to 100."""
    ensure_required_columns(df)

    temp = df.copy()
    for column in REVIEW_COLUMNS:
        temp[column] = pd.to_numeric(temp[column], errors="coerce")

    temp["review_sum"] = temp[REVIEW_COLUMNS].sum(axis=1)
    mask = temp["review_sum"].sub(100.0).abs() > tolerance
    return temp.loc[mask, ["Medicine Name", "Manufacturer", *REVIEW_COLUMNS, "review_sum"]]


def full_quality_report(df: pd.DataFrame) -> dict[str, Any]:
    """Basic quality report used by the focus 2 notebooks."""
    ensure_required_columns(df)

    review_issues = validate_review_percentages(df)
    manufacturer_blank = (
        df["Manufacturer"]
        .fillna("")
        .astype(str)
        .str.strip()
        .eq("")
        .sum()
    )

    composition_blank = (
        df["Composition"]
        .fillna("")
        .astype(str)
        .str.strip()
        .eq("")
        .sum()
    )

    return {
        "shape": df.shape,
        "duplicates": int(df.duplicated().sum()),
        "manufacturer_blank": int(manufacturer_blank),
        "composition_blank": int(composition_blank),
        "review_inconsistencies": int(len(review_issues)),
        "manufacturer_unique": int(df["Manufacturer"].nunique(dropna=True)),
        "null_summary": df[REQUIRED_COLUMNS].isna().sum().to_dict(),
    }
