"""
Módulo de limpieza de datos para el foco: Efectos Secundarios por Componentes.

Responsabilidades:
    - Eliminar duplicados completos del dataset raw.
    - Extraer y normalizar la columna `Composition` → lista de componentes activos.
    - Extraer y normalizar la columna `Side_effects` → lista de efectos secundarios.
    - Generar columnas derivadas: `componentes`, `efectos_secundarios`,
      `n_componentes`, `n_efectos`.
    - Marcar registros con anomalías (sin componentes o sin efectos).
    - Exportar el DataFrame limpio a data/processed/.

Uso desde notebook:
    from src.enfoque_03_efectos_secundarios_componentes.cleaning import run_cleaning_pipeline
    df_limpio = run_cleaning_pipeline(df_raw)
"""

import re
from pathlib import Path

import pandas as pd

RUTA_PROYECTO = Path(__file__).resolve().parents[2]
DATA_A_PROCESAR = RUTA_PROYECTO / "data" / "processed"
DATA_LIMPIA = DATA_A_PROCESAR / "e03_medicine_cleaned.csv"

# Columnas requeridas en el dataset raw
COLUMNAS_RAW_REQUERIDAS: list[str] = [
    "Medicine Name",
    "Composition",
    "Side_effects",
    "Manufacturer",
    "Excellent Review %",
    "Average Review %",
    "Poor Review %",
]


# ---------------------------------------------------------------------------
# Funciones auxiliares internas
# ---------------------------------------------------------------------------

def _normalizar_texto(valor: str) -> str:
    """
    Normaliza un string a minúsculas y colapsa espacios múltiples.

    Args:
        valor: Texto a normalizar.

    Returns:
        Texto en minúsculas sin espacios múltiples ni espacios al inicio/fin.
    """
    return re.sub(r"\s+", " ", valor.strip().lower())


# ---------------------------------------------------------------------------
# Paso 1: Eliminar duplicados
# ---------------------------------------------------------------------------

def eliminar_duplicados(df: pd.DataFrame) -> pd.DataFrame:
    """
    Elimina filas duplicadas completas del DataFrame.

    Se consideran duplicados aquellos registros donde TODAS las columnas
    son idénticas. No se eliminan filas con el mismo nombre de medicamento
    pero distinta composición o fabricante, ya que esos casos son legítimos.

    Args:
        df: DataFrame original cargado desde el CSV raw.

    Returns:
        DataFrame sin duplicados completos. Se conserva la primera ocurrencia
        de cada grupo de duplicados.

    Raises:
        TypeError: Si `df` no es un DataFrame de pandas.
    """
    if not isinstance(df, pd.DataFrame):
        raise TypeError(f"Se esperaba un DataFrame, se recibió {type(df)}")

    antes = len(df)
    df_limpio = df.drop_duplicates(keep="first").reset_index(drop=True)
    despues = len(df_limpio)

    eliminados = antes - despues
    print(f"[eliminar_duplicados] Filas antes: {antes} | Eliminados: {eliminados} | Filas después: {despues}")

    return df_limpio


# ---------------------------------------------------------------------------
# Paso 2: Extracción de componentes activos
# ---------------------------------------------------------------------------

def extraer_componentes(composition: object) -> list[str]:
    """
    Extrae los nombres de componentes activos desde una cadena `Composition`.

    Proceso:
        1. Valida que el valor sea un string no nulo.
        2. Elimina las dosis entre paréntesis (ej: `(500mg)`, `(10 mcg)`).
        3. Divide por el separador `+`.
        4. Normaliza a minúsculas sin espacios extra.
        5. Descarta tokens vacíos resultantes del proceso anterior.

    Args:
        composition: Valor crudo de la columna `Composition`.
            Ejemplo: ``"Amoxycillin (500mg) + Clavulanic Acid (125mg)"``

    Returns:
        Lista de nombres de componentes limpios y normalizados.
        Retorna lista vacía si el input es nulo, no es string, o no parseable.

    Example:
        >>> extraer_componentes("Amoxycillin (500mg) + Clavulanic Acid (125mg)")
        ['amoxycillin', 'clavulanic acid']
        >>> extraer_componentes("Paracetamol (650mg)")
        ['paracetamol']
    """
    try:
        if pd.isna(composition) or not isinstance(composition, str):
            return []
        texto = re.sub(r"\(.*?\)", "", str(composition))
        partes = re.split(r"\s*\+\s*", texto)
        return [_normalizar_texto(p) for p in partes if _normalizar_texto(p)]
    except Exception as exc:
        print(f"[extraer_componentes] Error procesando: {composition!r} -> {exc}")
        return []


# ---------------------------------------------------------------------------
# Paso 3: Extracción de efectos secundarios
# ---------------------------------------------------------------------------

def extraer_efectos_secundarios(side_effects: object) -> list[str]:
    """
    Extrae y normaliza los efectos secundarios desde texto sin delimitador explícito.

    La columna `Side_effects` concatena efectos usando mayúscula inicial como
    delimitador implícito (ej: ``"Vomiting Nausea High blood pressure"``).
    Se usa regex para capturar cada efecto donde inicia mayúscula.

    Args:
        side_effects: Valor crudo de la columna `Side_effects`.
            Ejemplo: ``"Vomiting Nausea High blood pressure"``

    Returns:
        Lista de efectos secundarios normalizados a minúsculas.
        Retorna lista vacía si el valor es nulo o no parseable.

    Example:
        >>> extraer_efectos_secundarios("Vomiting Nausea High blood pressure")
        ['vomiting', 'nausea', 'high blood pressure']
        >>> extraer_efectos_secundarios("Abdominal pain Diarrhea")
        ['abdominal pain', 'diarrhea']
    """
    try:
        if pd.isna(side_effects) or not isinstance(side_effects, str):
            return []
        partes = re.findall(r"[A-Z][^A-Z]*", str(side_effects))
        return [_normalizar_texto(p) for p in partes if _normalizar_texto(p)]
    except Exception as exc:
        print(f"[extraer_efectos_secundarios] Error procesando: {side_effects!r} -> {exc}")
        return []


# ---------------------------------------------------------------------------
# Paso 4: Agregar columnas derivadas
# ---------------------------------------------------------------------------

def añadir_columnas_derivadas(df: pd.DataFrame) -> pd.DataFrame:
    """
    Agrega las columnas derivadas de `Composition` y `Side_effects` al DataFrame.

    Columnas generadas:
        - `componentes` (list[str]): nombres de componentes activos normalizados.
        - `efectos_secundarios` (list[str]): efectos secundarios normalizados.
        - `manufacturer` (str): nombre del fabricante normalizado.
        - `n_componentes` (int): cantidad de componentes por medicamento.
        - `n_efectos` (int): cantidad de efectos secundarios por medicamento.

    Args:
        df: DataFrame con las columnas `Composition`, `Side_effects` y `Manufacturer`.

    Returns:
        DataFrame con las cinco columnas nuevas añadidas.

    Raises:
        KeyError: Si alguna de las columnas requeridas no existe en el DataFrame.
    """
    for col in ["Composition", "Side_effects", "Manufacturer"]:
        if col not in df.columns:
            raise KeyError(f"La columna '{col}' no existe en el DataFrame.")

    df = df.copy()

    df["componentes"] = df["Composition"].apply(extraer_componentes)
    df["efectos_secundarios"] = df["Side_effects"].apply(extraer_efectos_secundarios)

    # Normalizar fabricante para análisis agrupado posterior
    df["manufacturer"] = (
        df["Manufacturer"]
        .fillna("")
        .astype(str)
        .map(_normalizar_texto)
    )

    df["n_componentes"] = df["componentes"].map(len)
    df["n_efectos"] = df["efectos_secundarios"].map(len)

    print("[añadir_columnas_derivadas] Columnas generadas: componentes, efectos_secundarios, manufacturer, n_componentes, n_efectos")

    dist_comp = df["n_componentes"].value_counts().sort_index()
    print("[añadir_columnas_derivadas] Distribución por número de componentes:")
    for n, count in dist_comp.items():
        print(f"    {n} componente(s)  -> {count:>5} medicamentos")

    return df


# ---------------------------------------------------------------------------
# Paso 5: Marcar anomalías
# ---------------------------------------------------------------------------

def flag_anomalias(df: pd.DataFrame) -> pd.DataFrame:
    """
    Detecta y marca registros con posibles anomalías en composición o efectos.

    Anomalías marcadas con columnas booleanas:
        - `anomalia_componentes`: True si `n_componentes` == 0.
        - `anomalia_efectos`: True si `n_efectos` == 0.

    Estos registros NO se eliminan automáticamente. La decisión de
    descartarlos queda registrada en `docs/decisiones_limpieza.md`.

    Args:
        df: DataFrame con las columnas `n_componentes` y `n_efectos`.

    Returns:
        DataFrame con las dos columnas de anomalía añadidas.

    Raises:
        KeyError: Si `n_componentes` o `n_efectos` no existen en el DataFrame.
    """
    for col in ["n_componentes", "n_efectos"]:
        if col not in df.columns:
            raise KeyError(
                f"La columna '{col}' no existe. Ejecuta 'añadir_columnas_derivadas' primero."
            )

    df = df.copy()
    df["anomalia_componentes"] = df["n_componentes"] == 0
    df["anomalia_efectos"] = df["n_efectos"] == 0

    anom_comp = df["anomalia_componentes"].sum()
    anom_efec = df["anomalia_efectos"].sum()
    print(f"[flag_anomalias] Registros sin componentes: {anom_comp}")
    print(f"[flag_anomalias] Registros sin efectos secundarios: {anom_efec}")

    return df


# ---------------------------------------------------------------------------
# Pipeline orquestador
# ---------------------------------------------------------------------------

def run_cleaning_pipeline(
    df: pd.DataFrame,
    save: bool = True,
    output_path: str | Path = DATA_LIMPIA,
) -> pd.DataFrame:
    """
    Ejecuta el flujo completo de limpieza para el foco de efectos por componentes.

    Pasos en orden:
        1. Eliminar duplicados completos.
        2. Extraer componentes y efectos secundarios; normalizar fabricante.
        3. Marcar anomalías sin eliminarlas automáticamente.
        4. (Opcional) Exportar el resultado a `data/processed/`.

    El parámetro `save=True` exporta el CSV limpio, lo que permite que los
    notebooks de transformación y análisis trabajen siempre desde el dato
    ya procesado, sin volver a ejecutar la limpieza.

    Args:
        df: DataFrame raw cargado con `load_medicine_data()`.
        save: Si True, guarda el resultado en `output_path`.
        output_path: Ruta de destino del CSV limpio.

    Returns:
        DataFrame limpio con todas las columnas derivadas añadidas.

    Raises:
        ValueError: Si el DataFrame de entrada está vacío.
        KeyError: Si faltan columnas requeridas en el DataFrame.
        IOError: Si no se puede escribir el archivo de salida.
    """
    if df.empty:
        raise ValueError("El DataFrame de entrada está vacío. Verifica la carga de datos.")

    faltantes = [c for c in COLUMNAS_RAW_REQUERIDAS if c not in df.columns]
    if faltantes:
        raise KeyError(f"Columnas faltantes en el DataFrame: {faltantes}")

    print("=" * 55)
    print("INICIO DEL PIPELINE DE LIMPIEZA  [Enfoque 3]")
    print("=" * 55)

    df_clean = eliminar_duplicados(df)
    df_clean = añadir_columnas_derivadas(df_clean)
    df_clean = flag_anomalias(df_clean)

    print("-" * 55)
    print(f"Forma final del DataFrame: {df_clean.shape}")
    print("=" * 55)

    if save:
        try:
            output = Path(output_path)
            output.parent.mkdir(parents=True, exist_ok=True)
            # Las columnas con listas no se serializan bien en CSV;
            # se guardan como strings para que el archivo sea legible.
            df_csv = df_clean.copy()
            df_csv["componentes"] = df_csv["componentes"].astype(str)
            df_csv["efectos_secundarios"] = df_csv["efectos_secundarios"].astype(str)
            df_csv.to_csv(output, index=False)
            print(f"[run_cleaning_pipeline] CSV limpio guardado en: {output}")
        except OSError as exc:
            raise IOError(f"No se pudo guardar el archivo en {output_path}: {exc}") from exc

    return df_clean