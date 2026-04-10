import pandas as pd
from sklearn.preprocessing import MultiLabelBinarizer


def explode_effects(
    df: pd.DataFrame,
    *,
    drop_empty: bool = True,
) -> pd.DataFrame:
    """Expande la columna efectos_secundarios a una fila por efecto.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame limpio con columna efectos_secundarios (lista).
    drop_empty : bool, default True
        Si es True, elimina filas donde el efecto es nulo o vacío.

    Returns
    -------
    pd.DataFrame
        Una fila por (medicamento, efecto).

    Raises
    ------
    KeyError
        Si la columna efectos_secundarios no existe.
    """
    if "efectos_secundarios" not in df.columns:
        raise KeyError("Columna 'efectos_secundarios' no encontrada. Ejecuta clean_data() primero.")

    expanded = df.explode("efectos_secundarios", ignore_index=True)

    if drop_empty:
        mask = (
            expanded["efectos_secundarios"].notna()
            & (expanded["efectos_secundarios"].astype(str).str.strip() != "")
        )
        expanded = expanded[mask].reset_index(drop=True)

    return expanded


def explode_components(
    df: pd.DataFrame,
    *,
    drop_empty: bool = True,
) -> pd.DataFrame:
    """Expande la columna componentes a una fila por componente.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame limpio con columna componentes (lista).
    drop_empty : bool, default True
        Si es True, elimina filas con componente nulo o vacío.

    Returns
    -------
    pd.DataFrame
        Una fila por (medicamento, componente).

    Raises
    ------
    KeyError
        Si la columna componentes no existe.
    """
    if "componentes" not in df.columns:
        raise KeyError("Columna 'componentes' no encontrada. Ejecuta clean_data() primero.")

    expanded = df.explode("componentes", ignore_index=True)

    if drop_empty:
        mask = (
            expanded["componentes"].notna()
            & (expanded["componentes"].astype(str).str.strip() != "")
        )
        expanded = expanded[mask].reset_index(drop=True)

    return expanded


def explode_all(
    df: pd.DataFrame,
    *,
    drop_empty: bool = True,
) -> pd.DataFrame:
    """Expande AMBAS columnas: componentes y efectos_secundarios.

    Genera el producto cartesiano componentes × efectos por medicamento.
    Permite análisis de co-ocurrencia componente-efecto.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame limpio con columnas componentes y efectos_secundarios.
    drop_empty : bool, default True
        Elimina filas con valores vacíos tras el explode.

    Returns
    -------
    pd.DataFrame
        Una fila por combinación (medicamento, componente, efecto).
    """
    required = ["componentes", "efectos_secundarios"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise KeyError(f"Columnas faltantes: {missing}. Ejecuta clean_data() primero.")

    transformed = (
        df
        .explode("componentes", ignore_index=True)
        .explode("efectos_secundarios", ignore_index=True)
    )

    if drop_empty:
        mask = (
            transformed["componentes"].notna()
            & transformed["efectos_secundarios"].notna()
            & (transformed["componentes"].astype(str).str.strip() != "")
            & (transformed["efectos_secundarios"].astype(str).str.strip() != "")
        )
        transformed = transformed[mask].reset_index(drop=True)

    return transformed


def build_effects_matrix(
    df: pd.DataFrame,
    *,
    top_n_effects: int = 30,
) -> pd.DataFrame:
    """Construye una matriz binaria medicamento × efecto_secundario.

    Usa MultiLabelBinarizer para codificar presencia/ausencia de cada efecto.
    Solo incluye los top_n_effects más frecuentes.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame limpio con columna efectos_secundarios (lista).
    top_n_effects : int, default 30
        Número máximo de efectos a incluir (los más frecuentes).

    Returns
    -------
    pd.DataFrame
        Matriz binaria: 1 si el medicamento tiene ese efecto, 0 si no.
    """
    if "efectos_secundarios" not in df.columns:
        raise KeyError("Columna 'efectos_secundarios' no encontrada.")

    try:
        top_effects = (
            df["efectos_secundarios"]
            .explode()
            .dropna()
            .value_counts()
            .head(top_n_effects)
            .index.tolist()
        )

        filtered_lists = df["efectos_secundarios"].map(
            lambda lst: [e for e in lst if e in top_effects]
        )

        mlb = MultiLabelBinarizer(classes=top_effects)
        matrix = mlb.fit_transform(filtered_lists)

        return pd.DataFrame(matrix, columns=mlb.classes_, index=df.index)

    except Exception as exc:
        raise RuntimeError(f"[build_effects_matrix] Error: {exc}") from exc


def build_component_effect_crosstab(
    df_exploded: pd.DataFrame,
    *,
    min_observations: int = 5,
) -> pd.DataFrame:
    """Construye tabla de contingencia componente × efecto_secundario.

    Parameters
    ----------
    df_exploded : pd.DataFrame
        DataFrame ya expandido (resultado de explode_all).
    min_observations : int, default 5
        Filtra componentes con menos de esta cantidad de registros.

    Returns
    -------
    pd.DataFrame
        Crosstab: filas = componentes, columnas = efectos, valores = frecuencias.
    """
    try:
        counts = df_exploded["componentes"].value_counts()
        valid_components = counts[counts >= min_observations].index
        filtered = df_exploded[df_exploded["componentes"].isin(valid_components)]

        return pd.crosstab(
            filtered["componentes"],
            filtered["efectos_secundarios"],
        )
    except Exception as exc:
        raise RuntimeError(f"[build_component_effect_crosstab] Error: {exc}") from exc