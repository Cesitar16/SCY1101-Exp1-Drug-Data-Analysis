from collections.abc import Sequence

import pandas as pd


REQUIRED_COLUMNS: tuple[str, ...] = (
    "Medicine Name",
    "Composition",
    "Side_effects",
    "Manufacturer",
    "Excellent Review %",
    "Average Review %",
    "Poor Review %",
)


def get_missing_columns(
    df: pd.DataFrame,
    required_columns: Sequence[str] = REQUIRED_COLUMNS,
) -> list[str]:
    """Retorna las columnas requeridas que faltan en el DataFrame."""
    return [col for col in required_columns if col not in df.columns]


def validate_schema(
    df: pd.DataFrame,
    required_columns: Sequence[str] = REQUIRED_COLUMNS,
) -> None:
    """Valida que el DataFrame tenga el esquema mínimo requerido.

    Raises
    ------
    TypeError
        Si la entrada no es un DataFrame.
    ValueError
        Si falta alguna columna requerida.
    """
    if not isinstance(df, pd.DataFrame):
        raise TypeError(
            f"Se esperaba un pandas.DataFrame, se recibió: {type(df).__name__}"
        )
    missing = get_missing_columns(df, required_columns=required_columns)
    if missing:
        raise ValueError(f"Faltan {len(missing)} columna(s) requeridas: {missing}")


def validate_data(
    df: pd.DataFrame,
    required_columns: Sequence[str] = REQUIRED_COLUMNS,
) -> None:
    """Alias compatible con notebooks previos.

    Mantiene la API `validate_data(df)` usando la validación de esquema actual.
    """
    validate_schema(df, required_columns=required_columns)


def get_null_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Genera un resumen de valores nulos por columna.

    Returns
    -------
    pd.DataFrame
        Tabla con columnas: nulos, porcentaje.
        Solo incluye columnas que tienen al menos un nulo.
    """
    try:
        null_counts = df.isnull().sum()
        null_pct = (null_counts / len(df) * 100).round(2)
        summary = pd.DataFrame({"nulos": null_counts, "porcentaje": null_pct})
        return summary[summary["nulos"] > 0].sort_values("nulos", ascending=False)
    except Exception as exc:
        raise RuntimeError(f"[get_null_summary] Error: {exc}") from exc


def get_duplicate_count(df: pd.DataFrame, subset: list[str] | None = None) -> int:
    """Cuenta filas duplicadas en el DataFrame."""
    try:
        return int(df.duplicated(subset=subset).sum())
    except Exception as exc:
        raise RuntimeError(f"[get_duplicate_count] Error: {exc}") from exc


def validate_review_percentages(df: pd.DataFrame) -> pd.DataFrame:
    """Detecta filas donde los porcentajes de reseñas no suman ~100."""
    review_cols = ["Excellent Review %", "Average Review %", "Poor Review %"]
    try:
        temp = df[review_cols].apply(pd.to_numeric, errors="coerce")
        row_sums = temp.sum(axis=1)
        inconsistent_mask = (row_sums - 100).abs() > 1
        return df[inconsistent_mask].copy()
    except Exception as exc:
        raise RuntimeError(f"[validate_review_percentages] Error: {exc}") from exc


def full_quality_report(df: pd.DataFrame) -> dict:
    """Ejecuta todas las validaciones y retorna un reporte consolidado.

    Returns
    -------
    dict
        Claves: shape, null_summary, duplicates, review_inconsistencies.
    """
    try:
        validate_schema(df)
        return {
            "shape": df.shape,
            "null_summary": get_null_summary(df),
            "duplicates": get_duplicate_count(df),
            "review_inconsistencies": len(validate_review_percentages(df)),
        }
    except Exception as exc:
        raise RuntimeError(f"[full_quality_report] Error: {exc}") from exc