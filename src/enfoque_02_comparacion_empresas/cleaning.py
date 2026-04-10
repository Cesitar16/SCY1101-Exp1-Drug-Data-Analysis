from __future__ import annotations

import ast
import re
from pathlib import Path

import pandas as pd

from .validation import REVIEW_COLUMNS, ensure_required_columns


PROJECT_ROOT = Path(__file__).resolve().parents[2]
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
COMPANY_COMPARISON_CLEAN_PATH = PROCESSED_DIR / "manufacturer_comparison_clean.csv"

THERAPEUTIC_AREA_PATTERNS: dict[str, tuple[str, ...]] = {
    "Infections": (
        r"\bbacterial\b",
        r"\bfungal\b",
        r"\binfection",
        r"\bantibiotic",
        r"\bviral\b",
    ),
    "Pain / Inflammation": (
        r"\bpain\b",
        r"\binflammation",
        r"\barthritis\b",
        r"\bmigraine\b",
        r"\bfever\b",
        r"\bmuscle spasm\b",
    ),
    "Cardiovascular": (
        r"\bhypertension\b",
        r"\bblood pressure\b",
        r"\bheart\b",
        r"\bcardiac\b",
        r"\bcholesterol\b",
        r"\bangina\b",
    ),
    "Respiratory / Allergy": (
        r"\bcough\b",
        r"\basthma\b",
        r"\ballerg",
        r"\bsneezing\b",
        r"\brunny nose\b",
        r"\brespiratory\b",
        r"\bmucus\b",
        r"\bnasal\b",
    ),
    "Gastrointestinal": (
        r"\bgastro",
        r"\bulcer\b",
        r"\bacid reflux\b",
        r"\bstomach\b",
        r"\bconstipation\b",
        r"\bdiarrh",
        r"\bnausea\b",
        r"\bvomiting\b",
    ),
    "Neurology / Mental Health": (
        r"\banxiety\b",
        r"\bdepression\b",
        r"\bschizophrenia\b",
        r"\balzheimer",
        r"\bepilepsy\b",
        r"\bseizure\b",
        r"\bneuropathic\b",
        r"\bparkinson\b",
    ),
    "Diabetes / Endocrine": (
        r"\bdiabetes\b",
        r"\bthyroid\b",
        r"\bhormone\b",
        r"\binsulin\b",
    ),
    "Dermatology": (
        r"\bskin\b",
        r"\bacne\b",
        r"\bitching\b",
        r"\bpsoriasis\b",
        r"\bdandruff\b",
    ),
    "Oncology": (
        r"\bcancer\b",
        r"\btumou?r\b",
        r"\bchemotherapy\b",
    ),
    "Women's Health": (
        r"\bcontrace",
        r"\bovarian\b",
        r"\bcervical\b",
        r"\bmenstrual\b",
        r"\bmenopause\b",
        r"\bpregnan",
    ),
    "Eye / ENT": (
        r"\beye\b",
        r"\bglaucoma\b",
        r"\bear\b",
        r"\bnose\b",
        r"\bthroat\b",
    ),
    "Urology / Sexual Health": (
        r"\burinary\b",
        r"\berectile\b",
        r"\bprostate\b",
        r"\bkidney\b",
    ),
}


def _is_missing(value: object) -> bool:
    if value is None:
        return True
    try:
        return bool(pd.isna(value))
    except TypeError:
        return False


def normalize_whitespace(value: object) -> str | None:
    """Collapse repeated whitespace and trim outer spaces."""
    if _is_missing(value):
        return None
    text = str(value)
    text = re.sub(r"\s+", " ", text).strip()
    return text or None


def normalize_manufacturer(value: object) -> str | None:
    """Normalize manufacturer names without forcing title case."""
    return normalize_whitespace(value)


def normalize_composition(value: object) -> str | None:
    """Normalize separators and spaces inside the raw composition text."""
    text = normalize_whitespace(value)
    if text is None:
        return None
    text = re.sub(r"\s*\+\s*", " + ", text)
    text = re.sub(r"\s*,\s*", ", ", text)
    return text


def extract_components(composition: object) -> list[str]:
    """Extract active ingredients from Composition, ignoring dose strings."""
    text = normalize_composition(composition)
    if text is None:
        return []

    cleaned = re.sub(r"\([^)]*\)", "", text)
    components = []
    for part in cleaned.split("+"):
        token = normalize_whitespace(part)
        if token:
            components.append(token.title())
    return components


def build_composition_key(composition: object) -> str | None:
    """Canonical key for same-ingredient comparisons across manufacturers."""
    components = extract_components(composition)
    if not components:
        return None
    unique_components = sorted(dict.fromkeys(components))
    return " + ".join(unique_components)


def split_side_effects(value: object) -> list[str]:
    """Split concatenated side effects using capital letters as boundaries."""
    text = normalize_whitespace(value)
    if text is None:
        return []
    parts = [item.strip() for item in re.findall(r"[A-Z][^A-Z]*", text)]
    return [item for item in parts if item]


def infer_therapeutic_areas(value: object) -> list[str]:
    """Map free-text Uses into broad therapeutic areas."""
    text = normalize_whitespace(value)
    if text is None:
        return []

    lowered = text.lower()
    matches: list[str] = []
    for label, patterns in THERAPEUTIC_AREA_PATTERNS.items():
        if any(re.search(pattern, lowered) for pattern in patterns):
            matches.append(label)

    if not matches:
        matches.append("Other")
    return matches


def clean_company_comparison_data(
    df: pd.DataFrame,
    *,
    save: bool = True,
    output_path: str | Path = COMPANY_COMPARISON_CLEAN_PATH,
) -> pd.DataFrame:
    """Prepare a manufacturer-comparison dataset from the raw medicine table."""
    if df.empty:
        raise ValueError("El DataFrame de entrada esta vacio.")

    ensure_required_columns(df)

    clean = df.copy().drop_duplicates().reset_index(drop=True)
    clean["Medicine Name"] = clean["Medicine Name"].map(normalize_whitespace)
    clean["Manufacturer"] = clean["Manufacturer"].map(normalize_manufacturer)
    clean["Uses"] = clean["Uses"].map(normalize_whitespace)
    clean["Side_effects"] = clean["Side_effects"].map(normalize_whitespace)
    clean["Composition"] = clean["Composition"].map(normalize_composition)

    for column in REVIEW_COLUMNS:
        clean[column] = pd.to_numeric(clean[column], errors="coerce")

    clean["manufacturer_clean"] = clean["Manufacturer"]
    clean["composition_clean"] = clean["Composition"]
    clean["components_list"] = clean["Composition"].map(extract_components)
    clean["composition_key"] = clean["Composition"].map(build_composition_key)
    clean["side_effects_list"] = clean["Side_effects"].map(split_side_effects)
    clean["therapeutic_areas"] = clean["Uses"].map(infer_therapeutic_areas)
    clean["n_components"] = clean["components_list"].map(len)
    clean["n_side_effects"] = clean["side_effects_list"].map(len)
    clean["review_sum"] = clean[REVIEW_COLUMNS].sum(axis=1)
    clean["review_balance"] = (
        clean["Excellent Review %"] - clean["Poor Review %"]
    )

    if save:
        destination = Path(output_path)
        destination.parent.mkdir(parents=True, exist_ok=True)
        clean.to_csv(destination, index=False)

    return clean


def load_company_comparison_clean_data(
    path: str | Path = COMPANY_COMPARISON_CLEAN_PATH,
) -> pd.DataFrame:
    """Load the processed focus-2 CSV and restore list-based columns."""
    csv_path = Path(path)
    if not csv_path.exists():
        raise FileNotFoundError(f"No existe el archivo procesado: {csv_path}")

    df = pd.read_csv(csv_path)
    list_columns = ["components_list", "side_effects_list", "therapeutic_areas"]
    for column in list_columns:
        if column not in df.columns:
            continue
        df[column] = df[column].apply(
            lambda value: ast.literal_eval(value)
            if isinstance(value, str) and value.startswith("[")
            else []
        )
    return df
