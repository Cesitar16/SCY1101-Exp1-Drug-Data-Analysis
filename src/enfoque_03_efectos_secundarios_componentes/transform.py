"""
Módulo de transformaciones avanzadas para el foco: Efectos Secundarios por Componentes.

Responsabilidades:
    - Expandir componentes a filas individuales (explode por componente).
    - Expandir efectos secundarios a filas individuales (explode por efecto).
    - Generar el producto cartesiano componente × efecto por medicamento (explode_all).
    - Construir la tabla de contingencia componente → efecto (crosstab).
    - Normalizar el crosstab por fila para comparación justa entre componentes.
    - Exportar los DataFrames transformados a data/processed/.

Uso desde notebook:
    from src.enfoque_03_efectos_secundarios_componentes.transform import run_transform_pipeline
    df_long, crosstab, crosstab_norm = run_transform_pipeline(df_clean)
"""

from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.preprocessing import MultiLabelBinarizer

RUTA_PROYECTO = Path(__file__).resolve().parents[2]
DIR_PROCESADO = RUTA_PROYECTO / "data" / "processed"
RUTA_LONG = DIR_PROCESADO / "e03_medicine_long.csv"
RUTA_CROSSTAB = DIR_PROCESADO / "e03_crosstab_componente_efecto.csv"
RUTA_CROSSTAB_NORM = DIR_PROCESADO / "e03_crosstab_componente_efecto_norm.csv"


# ---------------------------------------------------------------------------
# Transformación 1: Explode por efecto secundario
# ---------------------------------------------------------------------------

def explotar_efectos(
    df: pd.DataFrame,
    drop_empty: bool = True,
) -> pd.DataFrame:
    """
    Expande la columna `efectos_secundarios` para tener una fila por efecto.

    Transforma el DataFrame de formato wide (una fila por medicamento con
    lista de efectos) a formato long (una fila por efecto), lo que permite
    calcular frecuencias individuales y agrupar por efecto secundario.

    Esta operación aumenta el número de filas: un medicamento con 5 efectos
    genera 5 filas. Las columnas restantes se repiten en cada fila. Esto es
    esperado y necesario para el análisis posterior.

    Args:
        df: DataFrame limpio con la columna `efectos_secundarios` (list[str]).
        drop_empty: Si True, elimina filas donde el efecto es nulo o vacío.

    Returns:
        DataFrame expandido: una fila por (medicamento, efecto_secundario).
        Incluye todas las columnas originales.

    Raises:
        KeyError: Si `efectos_secundarios` no existe en el DataFrame.
    """
    if "efectos_secundarios" not in df.columns:
        raise KeyError(
            "La columna 'efectos_secundarios' no existe. "
            "Ejecuta run_cleaning_pipeline primero."
        )

    antes = len(df)

    expanded = df.explode("efectos_secundarios", ignore_index=True)

    if drop_empty:
        mask = (
            expanded["efectos_secundarios"].notna()
            & (expanded["efectos_secundarios"].astype(str).str.strip() != "")
        )
        expanded = expanded[mask].reset_index(drop=True)

    despues = len(expanded)
    print(f"[explotar_efectos] Filas antes: {antes} -> después: {despues}")
    print(f"[explotar_efectos] Efectos únicos: {expanded['efectos_secundarios'].nunique()}")

    return expanded


# ---------------------------------------------------------------------------
# Transformación 2: Explode por componente
# ---------------------------------------------------------------------------

def explotar_componentes(
    df: pd.DataFrame,
    drop_empty: bool = True,
) -> pd.DataFrame:
    """
    Expande la columna `componentes` para tener una fila por componente.

    Permite calcular en cuántos medicamentos aparece cada componente y
    hacer agrupaciones individuales por componente.

    Args:
        df: DataFrame limpio con la columna `componentes` (list[str]).
        drop_empty: Si True, elimina filas con componente nulo o vacío.

    Returns:
        DataFrame expandido: una fila por (medicamento, componente).
        Incluye todas las columnas originales.

    Raises:
        KeyError: Si `componentes` no existe en el DataFrame.
    """
    if "componentes" not in df.columns:
        raise KeyError(
            "La columna 'componentes' no existe. "
            "Ejecuta run_cleaning_pipeline primero."
        )

    antes = len(df)

    expanded = df.explode("componentes", ignore_index=True)

    if drop_empty:
        mask = (
            expanded["componentes"].notna()
            & (expanded["componentes"].astype(str).str.strip() != "")
        )
        expanded = expanded[mask].reset_index(drop=True)

    despues = len(expanded)
    print(f"[explotar_componentes] Filas antes: {antes} -> después: {despues}")
    print(f"[explotar_componentes] Componentes únicos: {expanded['componentes'].nunique()}")

    return expanded


# ---------------------------------------------------------------------------
# Transformación 3: Explode cartesiano componente × efecto
# ---------------------------------------------------------------------------

def explotar_todo(
    df: pd.DataFrame,
    drop_empty: bool = True,
) -> pd.DataFrame:
    """
    Expande AMBAS columnas generando el producto cartesiano componente × efecto.

    Para cada medicamento con N componentes y M efectos, genera N × M filas.
    Este es el DataFrame base para construir la tabla componente → efecto.

    Ejemplo:
        Med1 con componentes [A, B] y efectos [náusea, mareo]
        genera 4 filas: (A, náusea), (A, mareo), (B, náusea), (B, mareo).

    Args:
        df: DataFrame limpio con columnas `componentes` y `efectos_secundarios`.
        drop_empty: Si True, elimina filas con componente o efecto nulo/vacío.

    Returns:
        DataFrame con una fila por combinación (medicamento, componente, efecto).
        Columnas relevantes: `componentes` (str), `efectos_secundarios` (str).

    Raises:
        KeyError: Si alguna de las columnas requeridas no existe.
    """
    requeridas = ["componentes", "efectos_secundarios"]
    faltantes = [c for c in requeridas if c not in df.columns]
    if faltantes:
        raise KeyError(
            f"Columnas faltantes: {faltantes}. "
            "Ejecuta run_cleaning_pipeline primero."
        )

    antes = len(df)

    # Doble explode: primero por componentes, luego por efectos.
    # El orden importa para mantener la trazabilidad del medicamento original.
    transformado = (
        df
        .explode("componentes", ignore_index=True)
        .explode("efectos_secundarios", ignore_index=True)
    )

    if drop_empty:
        mask = (
            transformado["componentes"].notna()
            & transformado["efectos_secundarios"].notna()
            & (transformado["componentes"].astype(str).str.strip() != "")
            & (transformado["efectos_secundarios"].astype(str).str.strip() != "")
        )
        transformado = transformado[mask].reset_index(drop=True)

    despues = len(transformado)
    pares_unicos = transformado[["componentes", "efectos_secundarios"]].drop_duplicates().shape[0]
    print(f"[explotar_todo] Filas antes: {antes} -> después: {despues}")
    print(f"[explotar_todo] Pares únicos (componente, efecto): {pares_unicos}")

    return transformado


# ---------------------------------------------------------------------------
# Transformación 4: Tabla de contingencia componente → efecto
# ---------------------------------------------------------------------------

def construir_crosstab(
    df_long: pd.DataFrame,
    min_observaciones: int = 5,
) -> pd.DataFrame:
    """
    Construye una tabla de contingencia componente × efecto_secundario.

    Usa `pd.crosstab` para contar cuántas veces cada par (componente, efecto)
    aparece en el dataset. El resultado es una matriz donde el valor [i][j]
    indica cuántos medicamentos tienen el componente i y el efecto j.

    Se filtran componentes con menos de `min_observaciones` para evitar que
    componentes raros distorsionen el análisis de asociación.

    Args:
        df_long: DataFrame expandido (resultado de `explotar_todo`), con
            columnas `componentes` y `efectos_secundarios`.
        min_observaciones: Número mínimo de registros que debe tener un
            componente para ser incluido en la tabla. Por defecto 5.

    Returns:
        DataFrame con la tabla de contingencia.
        Filas = componentes, columnas = efectos secundarios, valores = frecuencias.

    Raises:
        KeyError: Si `componentes` o `efectos_secundarios` no existen.
        ValueError: Si df_long está vacío.
    """
    if df_long.empty:
        raise ValueError("df_long está vacío. Ejecuta explotar_todo primero.")

    for col in ["componentes", "efectos_secundarios"]:
        if col not in df_long.columns:
            raise KeyError(f"La columna '{col}' no existe en df_long.")

    # Filtrar componentes con pocas observaciones para análisis confiable
    conteos = df_long["componentes"].value_counts()
    componentes_validos = conteos[conteos >= min_observaciones].index
    df_filtrado = df_long[df_long["componentes"].isin(componentes_validos)]

    crosstab = pd.crosstab(
        df_filtrado["componentes"],
        df_filtrado["efectos_secundarios"],
    )

    print(f"[construir_crosstab] Componentes incluidos: {crosstab.shape[0]} (min_obs={min_observaciones})")
    print(f"[construir_crosstab] Efectos incluidos   : {crosstab.shape[1]}")
    print(f"[construir_crosstab] Forma de la tabla   : {crosstab.shape[0]}×{crosstab.shape[1]}")

    return crosstab


# ---------------------------------------------------------------------------
# Transformación 5: Normalización del crosstab por fila
# ---------------------------------------------------------------------------

def normalizar_crosstab(tabla: pd.DataFrame) -> pd.DataFrame:
    """
    Normaliza la tabla de contingencia por filas (proporciones por componente).

    Sin normalizar, un componente que aparece en 1000 medicamentos siempre
    tendrá frecuencias mayores que uno que aparece en 10, lo que genera un
    sesgo falso. La normalización por fila convierte frecuencias absolutas en
    proporciones relativas, permitiendo comparar componentes con equidad.

    Cada celda [i][j] normalizada indica la proporción de registros del
    componente i que tienen el efecto j.

    Args:
        tabla: Tabla de contingencia generada por `construir_crosstab`.

    Returns:
        Tabla normalizada en rango [0, 1] por fila. Filas sin datos quedan en 0.

    Raises:
        ValueError: Si la tabla está vacía.
    """
    if tabla.empty:
        raise ValueError("La tabla de contingencia está vacía.")

    # replace(0, nan) evita división por cero para filas con suma cero
    sumas_fila = tabla.sum(axis=1).replace(0, float("nan"))
    tabla_norm = tabla.div(sumas_fila, axis=0).fillna(0.0)

    print(f"[normalizar_crosstab] Tabla normalizada por fila: {tabla_norm.shape[0]}×{tabla_norm.shape[1]}")

    return tabla_norm


# ---------------------------------------------------------------------------
# Transformación 6: Matriz binaria medicamento × efecto (MultiLabelBinarizer)
# ---------------------------------------------------------------------------

def construir_matriz_efectos(
    df: pd.DataFrame,
    top_n_efectos: int = 30,
) -> pd.DataFrame:
    """
    Construye una matriz binaria medicamento × efecto_secundario.

    Usa `MultiLabelBinarizer` para codificar presencia/ausencia de cada efecto.
    Solo incluye los `top_n_efectos` más frecuentes para mantener la matriz
    manejable. Esta representación permite clustering y reducción dimensional.

    Args:
        df: DataFrame limpio con columna `efectos_secundarios` (list[str]).
        top_n_efectos: Número máximo de efectos a incluir. Por defecto 30.

    Returns:
        DataFrame binario: filas = medicamentos, columnas = efectos (top N).
        Valor 1 si el medicamento tiene ese efecto, 0 si no.

    Raises:
        KeyError: Si `efectos_secundarios` no existe en el DataFrame.
        RuntimeError: Si ocurre un error inesperado durante la binarización.
    """
    if "efectos_secundarios" not in df.columns:
        raise KeyError(
            "La columna 'efectos_secundarios' no encontrada. "
            "Ejecuta run_cleaning_pipeline primero."
        )

    try:
        top_efectos = (
            df["efectos_secundarios"]
            .explode()
            .dropna()
            .value_counts()
            .head(top_n_efectos)
            .index.tolist()
        )

        # Filtrar las listas de cada medicamento a solo los top efectos
        listas_filtradas = df["efectos_secundarios"].map(
            lambda lst: [e for e in lst if e in top_efectos]
        )

        mlb = MultiLabelBinarizer(classes=top_efectos)
        matriz = mlb.fit_transform(listas_filtradas)

        print(f"[construir_matriz_efectos] Matriz binaria generada: {matriz.shape[0]}×{matriz.shape[1]}")

        return pd.DataFrame(matriz, columns=mlb.classes_, index=df.index)

    except Exception as exc:
        raise RuntimeError(f"[construir_matriz_efectos] Error: {exc}") from exc


# ---------------------------------------------------------------------------
# Pipeline orquestador
# ---------------------------------------------------------------------------

def run_transform_pipeline(
    df: pd.DataFrame,
    min_observaciones: int = 5,
    top_n_efectos: int = 30,
    save: bool = True,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Ejecuta el flujo completo de transformaciones sobre el DataFrame limpio.

    Pasos en orden:
        1. Producto cartesiano componente × efecto → df_long.
        2. Tabla de contingencia → crosstab.
        3. Normalización del crosstab por fila → crosstab_norm.
        4. (Opcional) Exportar los tres DataFrames a data/processed/.

    Args:
        df: DataFrame limpio generado por run_cleaning_pipeline.
        min_observaciones: Umbral mínimo para incluir un componente en el crosstab.
        top_n_efectos: Número de efectos top para la matriz binaria.
        save: Si True, exporta los DataFrames como CSV.

    Returns:
        Tupla (df_long, crosstab, crosstab_norm).

    Raises:
        ValueError: Si el DataFrame de entrada está vacío.
    """
    if df.empty:
        raise ValueError("El DataFrame de entrada está vacío.")

    print("=" * 55)
    print("INICIO DEL PIPELINE DE TRANSFORMACIONES  [Enfoque 3]")
    print("=" * 55)

    df_long = explotar_todo(df)
    crosstab = construir_crosstab(df_long, min_observaciones=min_observaciones)
    crosstab_norm = normalizar_crosstab(crosstab)

    print("-" * 55)
    print(f"df_long shape       : {df_long.shape}")
    print(f"crosstab shape      : {crosstab.shape}")
    print(f"crosstab_norm shape : {crosstab_norm.shape}")
    print("=" * 55)

    if save:
        try:
            DIR_PROCESADO.mkdir(parents=True, exist_ok=True)

            # La columna componentes y efectos_secundarios contienen listas Python.
            # Se convierten a string para serializar correctamente en CSV.
            df_long_csv = df_long.copy()
            for col in ["componentes", "efectos_secundarios"]:
                if col in df_long_csv.columns and df_long_csv[col].dtype == object:
                    if df_long_csv[col].map(lambda x: isinstance(x, list)).any():
                        df_long_csv[col] = df_long_csv[col].astype(str)
            df_long_csv.to_csv(RUTA_LONG, index=False)

            crosstab.to_csv(RUTA_CROSSTAB)
            crosstab_norm.to_csv(RUTA_CROSSTAB_NORM)

            print(f"[run_transform_pipeline] Archivos guardados en: {DIR_PROCESADO}")
        except OSError as exc:
            raise IOError(f"No se pudo guardar los archivos: {exc}") from exc

    return df_long, crosstab, crosstab_norm