"""Utilities for the manufacturer comparison focus."""

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
from .cleaning import (
    COMPANY_COMPARISON_CLEAN_PATH,
    clean_company_comparison_data,
    load_company_comparison_clean_data,
)
from .transform import (
    build_manufacturer_composition_frame,
    explode_side_effects,
    explode_therapeutic_areas,
)
from .validation import full_quality_report, validate_review_percentages
from .pipeline import (
    run_company_analysis_pipeline,
    run_company_comparison_pipeline,
    run_company_transform_pipeline,
)

__all__ = [
    "COMPANY_COMPARISON_CLEAN_PATH",
    "build_manufacturer_composition_frame",
    "clean_company_comparison_data",
    "load_company_comparison_clean_data",
    "composition_company_comparison",
    "composition_winners",
    "explode_side_effects",
    "explode_therapeutic_areas",
    "full_quality_report",
    "manufacturer_consistency",
    "manufacturer_reputation_ranking",
    "manufacturer_side_effect_summary",
    "manufacturer_specialization",
    "market_share_proxy",
    "plot_correlation_size_vs_good_reviews",
    "plot_quality_vs_quantity",
    "plot_reputation_ranking",
    "plot_review_balance_boxplot",
    "plot_specialization_heatmap",
    "plot_top_manufacturers",
    "quality_quantity_balance",
    "run_company_analysis_pipeline",
    "run_company_comparison_pipeline",
    "run_company_transform_pipeline",
    "top_medicines_by_manufacturer",
    "validate_review_percentages",
]
