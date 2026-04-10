import re
import pandas as pd

def _normalize_text(value: str) -> str:
    """Normaliza un string: minúsculas y espacios compactos.

    Parameters
    ----------
    value : str
        Texto a normalizar.

    Returns
    -------
    str
        Texto en minúsculas sin espacios múltiples.
    """
    return re.sub(r"\s+", " ", value.strip().lower())


def split_side_effects(value: object) -> list[str]:
    """Extrae y normaliza los efectos secundarios desde texto sin comas.

    La columna Side_effects concatena efectos usando mayúscula inicial
    como delimitador implícito. Se usa regex para capturar cada efecto.

    Parameters
    ----------
    value : object
        Valor crudo de la columna Side_effects.

    Returns
    -------
    list[str]
        Lista de efectos secundarios normalizados.
        Retorna lista vacía si el valor es nulo.

    Examples
    --------
    >>> split_side_effects("Vomiting Nausea High blood pressure")
    ['vomiting', 'nausea', 'high blood pressure']
    """
    try:
        if pd.isna(value) or not isinstance(value, str):
            return []
        parts = re.findall(r"[A-Z][^A-Z]*", str(value))
        return [_normalize_text(p) for p in parts if _normalize_text(p)]
    except Exception as exc:
        print(f"[split_side_effects] Error procesando valor '{value}': {exc}")
        return []


def split_components(value: object) -> list[str]:
    """Limpia y separa los componentes activos desde la columna Composition.

    Pasos:
    1. Elimina dosificaciones entre paréntesis (ej: "(500mg)").
    2. Divide por el separador "+".
    3. Normaliza a minúsculas sin espacios extra.

    Parameters
    ----------
    value : object
        Valor crudo de la columna Composition.

    Returns
    -------
    list[str]
        Lista de componentes activos normalizados.

    Examples
    --------
    >>> split_components("Amoxycillin (500mg) + Clavulanic Acid (125mg)")
    ['amoxycillin', 'clavulanic acid']
    """
    try:
        if pd.isna(value) or not isinstance(value, str):
            return []
        text = re.sub(r"\(.*?\)", "", str(value))
        parts = re.split(r"\s*\+\s*", text)
        return [_normalize_text(p) for p in parts if _normalize_text(p)]
    except Exception as exc:
        print(f"[split_components] Error procesando valor '{value}': {exc}")
        return []


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Aplica el pipeline completo de limpieza al dataset de medicamentos.

    Crea columnas derivadas normalizadas sin modificar las originales:
    - componentes         : lista de componentes activos limpios
    - efectos_secundarios : lista de efectos secundarios limpios
    - manufacturer        : nombre del fabricante normalizado
    - n_efectos           : cantidad de efectos secundarios por medicamento
    - n_componentes       : cantidad de componentes por medicamento

    Parameters
    ----------
    df : pd.DataFrame
        Dataset raw con columnas Composition, Side_effects y Manufacturer.

    Returns
    -------
    pd.DataFrame
        Copia del DataFrame con columnas adicionales limpias.

    Raises
    ------
    KeyError
        Si faltan columnas requeridas en el DataFrame.
    """
    required = ["Composition", "Side_effects", "Manufacturer"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise KeyError(f"Columnas faltantes en el DataFrame: {missing}")

    cleaned = df.copy()

    cleaned["componentes"] = cleaned["Composition"].apply(split_components)
    cleaned["efectos_secundarios"] = cleaned["Side_effects"].apply(split_side_effects)

    cleaned["manufacturer"] = (
        cleaned["Manufacturer"]
        .fillna("")
        .astype(str)
        .map(_normalize_text)
    )

    cleaned["n_efectos"] = cleaned["efectos_secundarios"].map(len)
    cleaned["n_componentes"] = cleaned["componentes"].map(len)

    return cleaned