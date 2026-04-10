from __future__ import annotations

import pandas as pd


def explode_list_column(
    df: pd.DataFrame,
    *,
    source_column: str,
    target_column: str,
) -> pd.DataFrame:
    """Explode a list-like column into one row per item."""
    if source_column not in df.columns:
        raise KeyError(f"La columna '{source_column}' no existe.")

    exploded = df.copy()
    exploded[source_column] = exploded[source_column].apply(
        lambda value: value if isinstance(value, list) else []
    )
    exploded = exploded.explode(source_column).reset_index(drop=True)
    exploded = exploded.rename(columns={source_column: target_column})
    return exploded.dropna(subset=[target_column])


def explode_side_effects(df: pd.DataFrame) -> pd.DataFrame:
    """One row per medicine x side effect."""
    return explode_list_column(
        df,
        source_column="side_effects_list",
        target_column="side_effect",
    )


def explode_therapeutic_areas(df: pd.DataFrame) -> pd.DataFrame:
    """One row per medicine x therapeutic area."""
    return explode_list_column(
        df,
        source_column="therapeutic_areas",
        target_column="therapeutic_area",
    )


def build_manufacturer_composition_frame(
    df: pd.DataFrame,
    *,
    min_manufacturers: int = 2,
) -> pd.DataFrame:
    """Aggregate review metrics for each composition-manufacturer pair."""
    required = {
        "composition_key",
        "manufacturer_clean",
        "Medicine Name",
        "Excellent Review %",
        "Average Review %",
        "Poor Review %",
        "review_balance",
    }
    missing = required.difference(df.columns)
    if missing:
        raise KeyError(
            "Faltan columnas para comparar composiciones: "
            + ", ".join(sorted(missing))
        )

    temp = df.dropna(subset=["composition_key", "manufacturer_clean"]).copy()
    pairs = (
        temp.groupby(["composition_key", "manufacturer_clean"], as_index=False)
        .agg(
            n_medicines=("Medicine Name", "count"),
            excellent_mean=("Excellent Review %", "mean"),
            average_mean=("Average Review %", "mean"),
            poor_mean=("Poor Review %", "mean"),
            review_balance_mean=("review_balance", "mean"),
        )
    )

    manufacturer_counts = (
        pairs.groupby("composition_key")["manufacturer_clean"]
        .nunique()
        .rename("n_manufacturers")
    )
    pairs = pairs.merge(
        manufacturer_counts,
        left_on="composition_key",
        right_index=True,
        how="left",
    )
    return pairs[pairs["n_manufacturers"] >= min_manufacturers].copy()
