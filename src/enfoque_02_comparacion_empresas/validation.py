"""Validaciones para el enfoque de comparacion entre empresas."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
REPORTS_DIR = PROJECT_ROOT / "outputs" / "reports"

REQUIRED_RAW_COLUMNS = {
    "Medicine Name",
    "Composition",
    "Uses",
    "Side_effects",
    "Image URL",
    "Manufacturer",
    "Excellent Review %",
    "Average Review %",
    "Poor Review %",
}

REQUIRED_CLEAN_COLUMNS = {
    "empresa",
    "composition_key",
    "num_componentes",
    "num_effects",
    "review_sum",
    "review_sum_valid",
    "shared_company_count",
    "shared_company_composition",
}


def validate_raw_columns(df_raw: pd.DataFrame) -> dict:
    """Validate that the raw dataset contains the expected columns."""
    missing = sorted(REQUIRED_RAW_COLUMNS - set(df_raw.columns))
    extra = sorted(set(df_raw.columns) - REQUIRED_RAW_COLUMNS)
    result = {
        "missing_columns": missing,
        "extra_columns": extra,
        "is_valid": len(missing) == 0,
    }
    print(f"[validate_raw_columns] is_valid={result['is_valid']}")
    return result


def validate_clean_columns(df_clean: pd.DataFrame) -> dict:
    """Validate that derived columns exist after cleaning."""
    missing = sorted(REQUIRED_CLEAN_COLUMNS - set(df_clean.columns))
    result = {
        "missing_columns": missing,
        "is_valid": len(missing) == 0,
    }
    print(f"[validate_clean_columns] is_valid={result['is_valid']}")
    return result


def validate_review_sums(df_clean: pd.DataFrame) -> dict:
    """Validate whether review percentages sum to 100."""
    invalid_rows = int(df_clean["review_sum_valid"].eq(False).sum())
    result = {
        "invalid_rows": invalid_rows,
        "valid_ratio": round(float(df_clean["review_sum_valid"].mean()), 4),
    }
    print(
        "[validate_review_sums] "
        f"invalid_rows={invalid_rows:,} valid_ratio={result['valid_ratio']}"
    )
    return result


def validate_shared_compositions(df_clean: pd.DataFrame) -> dict:
    """Measure how much comparable cross-company data exists."""
    shared_mask = df_clean["shared_company_composition"]
    shared_rows = int(shared_mask.sum())
    shared_frame = df_clean.loc[shared_mask].copy()

    group_sizes = shared_frame.groupby(["composition_key", "empresa"]).size()
    composition_company_counts = shared_frame.groupby("composition_key")["empresa"].nunique()

    result = {
        "shared_rows": shared_rows,
        "shared_compositions": int(shared_frame["composition_key"].nunique()),
        "compositions_shared_by_3_or_more_companies": int((composition_company_counts >= 3).sum()),
        "compositions_shared_by_5_or_more_companies": int((composition_company_counts >= 5).sum()),
        "company_composition_groups": int(len(group_sizes)),
        "groups_with_1_row": int((group_sizes == 1).sum()),
        "groups_with_2_or_more_rows": int((group_sizes >= 2).sum()),
        "groups_with_4_or_more_rows": int((group_sizes >= 4).sum()),
    }
    print(
        "[validate_shared_compositions] "
        f"shared_rows={shared_rows:,} "
        f"shared_compositions={result['shared_compositions']:,}"
    )
    return result


def build_method_limits() -> dict:
    """Document key interpretation limits for this focus."""
    return {
        "n_reviews_available": False,
        "interpretation": (
            "Los porcentajes de reviews describen tendencia del dataset, "
            "pero no permiten inferencia estadistica porque no incluyen el "
            "numero de resenas originales."
        ),
        "recommended_scope": (
            "Comparar empresas solo dentro de la misma composicion y "
            "reportar siempre cobertura por composicion y por empresa."
        ),
    }


def export_report(report: dict, filename: str = "company_comparison_validation_report.json") -> Path:
    """Export the validation report as JSON."""
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    path = REPORTS_DIR / filename
    with path.open("w", encoding="utf-8") as file:
        json.dump(report, file, ensure_ascii=False, indent=2)
    print(f"[export_report] saved_report={path}")
    return path


def run_validation_pipeline(df_raw: pd.DataFrame, df_clean: pd.DataFrame) -> dict:
    """Run all validations and export a report."""
    if df_raw.empty or df_clean.empty:
        raise ValueError("df_raw and df_clean must not be empty.")

    report = {
        "timestamp": datetime.now().isoformat(),
        "raw_columns": validate_raw_columns(df_raw),
        "clean_columns": validate_clean_columns(df_clean),
        "review_sums": validate_review_sums(df_clean),
        "shared_compositions": validate_shared_compositions(df_clean),
        "method_limits": build_method_limits(),
    }
    export_report(report)
    return report
