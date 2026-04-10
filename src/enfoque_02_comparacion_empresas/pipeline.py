from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd

from src.load_data import load_medicine_data

from .analysis import (
    composition_company_comparison,
    composition_winners,
    manufacturer_consistency,
    manufacturer_reputation_ranking,
    manufacturer_side_effect_summary,
    manufacturer_specialization,
    market_share_proxy,
    plot_correlation_size_vs_good_reviews,
    plot_quality_vs_quantity,
    plot_reputation_ranking,
    plot_review_balance_boxplot,
    plot_specialization_heatmap,
    plot_top_manufacturers,
    quality_quantity_balance,
    top_medicines_by_manufacturer,
)
from .cleaning import COMPANY_COMPARISON_CLEAN_PATH, clean_company_comparison_data
from .transform import (
    build_manufacturer_composition_frame,
    explode_side_effects,
    explode_therapeutic_areas,
)
from .validation import full_quality_report


PROJECT_ROOT = Path(__file__).resolve().parents[2]
FOCUS2_FIGURES_DIR = PROJECT_ROOT / "outputs" / "figures" / "enfoque_02_comparacion_empresas"
FOCUS2_TABLES_DIR = PROJECT_ROOT / "outputs" / "tables" / "enfoque_02_comparacion_empresas"
FOCUS2_REPORTS_DIR = PROJECT_ROOT / "outputs" / "reports"
FOCUS2_PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

FOCUS2_SIDE_EFFECTS_PATH = FOCUS2_PROCESSED_DIR / "manufacturer_side_effects_exploded.csv"
FOCUS2_THERAPEUTIC_AREAS_PATH = FOCUS2_PROCESSED_DIR / "manufacturer_therapeutic_areas_exploded.csv"
FOCUS2_COMPOSITION_FRAME_PATH = FOCUS2_PROCESSED_DIR / "manufacturer_composition_summary.csv"
FOCUS2_REPORT_PATH = FOCUS2_REPORTS_DIR / "enfoque_02_comparacion_empresas_pipeline_report.json"


def _ensure_parent(path: str | Path) -> Path:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    return destination


def _export_table(df: pd.DataFrame, path: str | Path) -> Path:
    destination = _ensure_parent(path)
    df.to_csv(destination, index=False)
    return destination


def _export_report(report: dict[str, Any], path: str | Path = FOCUS2_REPORT_PATH) -> Path:
    destination = _ensure_parent(path)
    with destination.open("w", encoding="utf-8") as file:
        json.dump(report, file, ensure_ascii=False, indent=2)
    return destination


def run_company_transform_pipeline(
    df_clean: pd.DataFrame,
    *,
    min_manufacturers: int = 2,
    save: bool = True,
) -> dict[str, pd.DataFrame]:
    """Build and optionally export the focus-2 transformed datasets."""
    if df_clean.empty:
        raise ValueError("El DataFrame limpio está vacío.")

    print("=" * 55)
    print("INICIO DEL PIPELINE DE TRANSFORMACIONES")
    print("=" * 55)

    print("\n[1/3] Expandiendo medicamento × efecto secundario...")
    side_effects = explode_side_effects(df_clean)
    print(f"    Shape: {side_effects.shape}")

    print("\n[2/3] Expandiendo medicamento × área terapéutica...")
    therapeutic_areas = explode_therapeutic_areas(df_clean)
    print(f"    Shape: {therapeutic_areas.shape}")

    print("\n[3/3] Construyendo resumen composición × empresa...")
    composition_frame = build_manufacturer_composition_frame(
        df_clean,
        min_manufacturers=min_manufacturers,
    )
    print(f"    Shape: {composition_frame.shape}")

    if save:
        _export_table(side_effects, FOCUS2_SIDE_EFFECTS_PATH)
        _export_table(therapeutic_areas, FOCUS2_THERAPEUTIC_AREAS_PATH)
        _export_table(composition_frame, FOCUS2_COMPOSITION_FRAME_PATH)
        print(f"\n[run_company_transform_pipeline] Archivos guardados en: {FOCUS2_PROCESSED_DIR}")

    print("=" * 55)
    print("TRANSFORMACIONES COMPLETAS")
    print("=" * 55)

    return {
        "side_effects": side_effects,
        "therapeutic_areas": therapeutic_areas,
        "composition_frame": composition_frame,
    }


def run_company_analysis_pipeline(
    df_clean: pd.DataFrame,
    *,
    min_medicines: int = 10,
    min_manufacturers: int = 2,
    top_n: int = 15,
    save: bool = True,
) -> dict[str, pd.DataFrame]:
    """Compute and optionally export the main focus-2 tables and figures."""
    if df_clean.empty:
        raise ValueError("El DataFrame limpio está vacío.")

    print("=" * 55)
    print("INICIO DEL PIPELINE DE ANÁLISIS")
    print("=" * 55)

    print("\n[1/9] Calculando share proxy por empresa...")
    market_share = market_share_proxy(df_clean, top_n=top_n)

    print("[2/9] Calculando ranking de reputación...")
    ranking = manufacturer_reputation_ranking(df_clean, min_medicines=min_medicines)

    print("[3/9] Calculando consistencia interna...")
    consistency = manufacturer_consistency(df_clean, min_medicines=min_medicines)

    print("[4/9] Comparando misma composición entre empresas...")
    composition_comparison = composition_company_comparison(
        df_clean,
        min_manufacturers=min_manufacturers,
    )

    print("[5/9] Identificando ganadores por composición...")
    winners = composition_winners(df_clean, min_manufacturers=min_manufacturers)

    print("[6/9] Resumiendo seguridad por empresa...")
    side_effect_summary = manufacturer_side_effect_summary(
        df_clean,
        min_medicines=min_medicines,
    )

    print("[7/9] Calculando especialización terapéutica...")
    specialization = manufacturer_specialization(
        df_clean,
        min_medicines=min_medicines,
    )

    print("[8/9] Calculando balance calidad vs cantidad...")
    quality_balance = quality_quantity_balance(
        df_clean,
        min_medicines=min_medicines,
    )

    print("[9/9] Identificando top medicamentos por empresa...")
    top_medicines = top_medicines_by_manufacturer(
        df_clean,
        min_company_size=min_medicines,
        top_n=3,
    )

    if save:
        tables = {
            "market_share_proxy.csv": market_share,
            "manufacturer_reputation_ranking.csv": ranking,
            "manufacturer_consistency.csv": consistency,
            "composition_company_comparison.csv": composition_comparison,
            "composition_winners.csv": winners,
            "manufacturer_side_effect_summary.csv": side_effect_summary,
            "manufacturer_specialization.csv": specialization,
            "quality_quantity_balance.csv": quality_balance,
            "top_medicines_by_manufacturer.csv": top_medicines,
        }
        for filename, table in tables.items():
            _export_table(table, FOCUS2_TABLES_DIR / filename)

        plot_top_manufacturers(
            df_clean,
            top_n=top_n,
            save_path=FOCUS2_FIGURES_DIR / "top_manufacturers.png",
        )
        plot_reputation_ranking(
            df_clean,
            top_n=top_n,
            min_medicines=min_medicines,
            save_path=FOCUS2_FIGURES_DIR / "reputation_ranking.png",
        )
        plot_review_balance_boxplot(
            df_clean,
            top_n=min(top_n, 12),
            save_path=FOCUS2_FIGURES_DIR / "review_balance_boxplot.png",
        )
        plot_quality_vs_quantity(
            df_clean,
            min_medicines=min_medicines,
            save_path=FOCUS2_FIGURES_DIR / "quality_vs_quantity.png",
        )
        plot_correlation_size_vs_good_reviews(
            df_clean,
            min_medicines=min_medicines,
            save_path=FOCUS2_FIGURES_DIR / "correlation_size_vs_good_reviews.png",
        )
        plot_specialization_heatmap(
            df_clean,
            top_n_manufacturers=min(top_n, 10),
            save_path=FOCUS2_FIGURES_DIR / "specialization_heatmap.png",
        )
        print(f"\n[run_company_analysis_pipeline] Tablas guardadas en: {FOCUS2_TABLES_DIR}")
        print(f"[run_company_analysis_pipeline] Figuras guardadas en: {FOCUS2_FIGURES_DIR}")

    print("=" * 55)
    print("ANÁLISIS COMPLETO")
    print("=" * 55)

    return {
        "market_share": market_share,
        "ranking": ranking,
        "consistency": consistency,
        "composition_comparison": composition_comparison,
        "winners": winners,
        "side_effect_summary": side_effect_summary,
        "specialization": specialization,
        "quality_balance": quality_balance,
        "top_medicines": top_medicines,
    }


def run_company_comparison_pipeline(
    df_raw: pd.DataFrame | None = None,
    *,
    download_if_missing: bool = False,
    min_medicines: int = 10,
    min_manufacturers: int = 2,
    top_n: int = 15,
    save_outputs: bool = True,
) -> dict[str, Any]:
    """Run the full focus-2 pipeline from raw data to exported outputs."""
    if df_raw is None:
        df_raw = load_medicine_data(download_if_missing=download_if_missing)

    if df_raw.empty:
        raise ValueError("El DataFrame raw está vacío.")

    print("=" * 55)
    print("INICIO DEL PIPELINE COMPLETO - ENFOQUE 2")
    print("=" * 55)

    print("\n[1/4] Generando reporte de calidad del raw...")
    raw_quality_report = full_quality_report(df_raw)
    print(f"    Shape raw: {raw_quality_report['shape']}")
    print(f"    Duplicados: {raw_quality_report['duplicates']}")
    print(f"    Reviews inconsistentes: {raw_quality_report['review_inconsistencies']}")

    print("\n[2/4] Ejecutando limpieza...")
    df_clean = clean_company_comparison_data(
        df_raw,
        save=save_outputs,
        output_path=COMPANY_COMPARISON_CLEAN_PATH,
    )
    print(f"    Shape limpio: {df_clean.shape}")

    print("\n[3/4] Ejecutando transformaciones...")
    transform_outputs = run_company_transform_pipeline(
        df_clean,
        min_manufacturers=min_manufacturers,
        save=save_outputs,
    )

    print("\n[4/4] Ejecutando análisis...")
    analysis_outputs = run_company_analysis_pipeline(
        df_clean,
        min_medicines=min_medicines,
        min_manufacturers=min_manufacturers,
        top_n=top_n,
        save=save_outputs,
    )

    report = {
        "timestamp": datetime.now().isoformat(),
        "parameters": {
            "min_medicines": min_medicines,
            "min_manufacturers": min_manufacturers,
            "top_n": top_n,
            "save_outputs": save_outputs,
        },
        "raw_quality_report": raw_quality_report,
        "clean_shape": list(df_clean.shape),
        "transform_shapes": {
            name: list(frame.shape) for name, frame in transform_outputs.items()
        },
        "analysis_shapes": {
            name: list(frame.shape) for name, frame in analysis_outputs.items()
        },
        "paths": {
            "clean_csv": str(COMPANY_COMPARISON_CLEAN_PATH),
            "side_effects_csv": str(FOCUS2_SIDE_EFFECTS_PATH),
            "therapeutic_areas_csv": str(FOCUS2_THERAPEUTIC_AREAS_PATH),
            "composition_summary_csv": str(FOCUS2_COMPOSITION_FRAME_PATH),
            "tables_dir": str(FOCUS2_TABLES_DIR),
            "figures_dir": str(FOCUS2_FIGURES_DIR),
        },
    }
    report_path = _export_report(report)

    print("\n" + "=" * 55)
    print("PIPELINE COMPLETO FINALIZADO")
    print(f"Reporte guardado en : {report_path}")
    print("=" * 55)

    return {
        "raw_quality_report": raw_quality_report,
        "df_clean": df_clean,
        "transform_outputs": transform_outputs,
        "analysis_outputs": analysis_outputs,
        "report_path": report_path,
    }


def main() -> None:
    run_company_comparison_pipeline(download_if_missing=True)


if __name__ == "__main__":
    main()
