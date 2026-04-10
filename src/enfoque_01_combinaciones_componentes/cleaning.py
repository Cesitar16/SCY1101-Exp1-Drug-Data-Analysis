"""
Módulo de limpieza de datos para el foco: Combinaciones de Componentes.
 
Responsabilidades:
    - Eliminar duplicados completos del dataset raw.
    - Normalizar la columna `Composition` (espacios, capitalización).
    - Extraer nombres de componentes activos sin dosis.
    - Generar columnas derivadas: `components_list`, `n_components`, `size_category`.
    - Exportar el DataFrame limpio a data/processed/.
 
Uso desde notebook:
    from src.cleaning import run_cleaning_pipeline
    df_limpio = run_cleaning_pipeline(df)
"""

import re
from pathlib import Path
import pandas as pd

RUTA_PROYECTO = Path(__file__).resolve().parents[2]
DATA_A_PROCESAR = RUTA_PROYECTO / "data" / "processed"
DATA_LIMPIA = DATA_A_PROCESAR / "medicine_cleaned.csv"

TAMAÑO_CATEGORIAS_MAP: dict[int, str] = {
    1: "mono",
    2: "duo",
    3: "trio",
    4: "cuádruple",
}
CATEGORIAS_TAMAÑO_ORDER: list[str] = ["mono", "duo", "trio", "cuádruple", "complejo"]

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
        raise TypeError(f'Se esperaba un DataFrame, se recibio {type(df)}')
    
    antes = len(df)
    df_limpio = df.drop_duplicates(keep="first").reset_index(drop=True)
    despues = len(df_limpio)

    eliminados = antes - despues
    print(f'[eliminar_duplicados] Files antes: {antes} | Eliminados: {eliminados} | Files despues: {despues}')

    return df_limpio

def normalizar_composicion(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normaliza los espacios y capitalización de la columna `Composition`.
 
    Operaciones aplicadas (vectorizadas):
        1. Strip de espacios al inicio y al final de la cadena completa.
        2. Colapso de múltiples espacios consecutivos a uno solo.
        3. Normalización de espacios alrededor del separador `+`.
 
    No se eliminan las dosis ni se modifica el contenido semántico;
    eso ocurre en `extract_components`. Esta función solo estandariza
    el formato para que el parseo posterior sea confiable.
 
    Args:
        df: DataFrame con la columna `Composition` presente.
 
    Returns:
        DataFrame con la columna `Composition` normalizada en su lugar.
 
    Raises:
        KeyError: Si la columna `Composition` no existe en el DataFrame.
    """
    if 'Composition' not in df.columns:
        raise KeyError("La columna 'Coposición' no existe en el DataFrame.")
    
    df = df.copy()

    df['Composition'] = (
    df["Composition"]
        .str.strip()
        .str.replace(r"\s+", " ", regex=True)
        .str.replace(r"\s*\+\s*", " + ", regex=True)
        )

    print('[normalizar_composicion] Normalización de espacios completada.')

    return df

def extraer_componentes(composition: str) -> list[str]:
    """
    Extrae los nombres de componentes activos desde una cadena `Composition`.
 
    Proceso:
        1. Divide por el separador `+`.
        2. Elimina las dosis entre paréntesis (ej: `(500mg)`, `(10 mcg)`).
        3. Elimina espacios sobrantes y aplica capitalización Title Case.
        4. Descarta tokens vacíos resultantes del proceso anterior.
 
    Args:
        composition: String del campo `Composition`.
            Ejemplo: "Amoxycillin (500mg) + Clavulanic Acid (125mg)"
 
    Returns:
        Lista de nombres de componentes limpios y normalizados.
        Retorna lista vacía si el input es nulo, no es string, o no parseable.
 
    Example:
        >>> extract_components("Amoxycillin (500mg) + Clavulanic Acid (125mg)")
        ['Amoxycillin', 'Clavulanic Acid']
        >>> extract_components("Paracetamol (650mg)")
        ['Paracetamol']
    """
    try:
        if pd.isna(composition) or not isinstance(composition, str):
            return[]
    
        parts = composition.split("+")

        limpios = [
            re.sub(r"\(.*?\)", "", part).strip().title()
            for part in parts
        ]

        return [l for l in limpios if l]
    except Exception as exc:
        print(f'[extraer_componentes] Error procesando: {composition!r} -> {exc}')
        return []

def añadir_columnas_componentes(df: pd.DataFrame) -> pd.DataFrame:
    """
    Agrega las columnas derivadas de `Composition` al DataFrame.
 
    Columnas generadas:
        - `components_list` (list[str]): nombres de componentes sin dosis.
        - `n_components` (int): cantidad de componentes por medicamento.
        - `size_category` (pd.Categorical): categoría ordinal del tamaño
          de la combinación. Orden: mono < duo < trio < cuádruple < complejo.
 
    La columna `size_category` se crea como `pd.Categorical` con `ordered=True`
    para que operaciones como `sort_values`, `groupby` y comparaciones
    (`df[df.size_category > "duo"]`) respeten el orden lógico farmacológico,
    no el orden alfabético.
 
    Args:
        df: DataFrame con la columna `Composition` ya normalizada.
 
    Returns:
        DataFrame con las tres columnas nuevas añadidas.
 
    Raises:
        KeyError: Si la columna `Composition` no existe en el DataFrame.
    """
    if "Composition" not in df.columns:
        raise KeyError("La columna 'Composition' no existe. Ejecuta 'normalizar_composicion' primero.")
    
    df = df.copy()

    df['components_list'] = df['Composition'].apply(extraer_componentes)

    df['n_components'] = df["components_list"].apply(len)

    df['size_category'] = pd.Categorical(
        df["n_components"].map(TAMAÑO_CATEGORIAS_MAP).fillna('complejo'),
        categories=CATEGORIAS_TAMAÑO_ORDER,
        ordered=True,
    )

    dist = df['size_category'].value_counts().sort_index()
    print('[añadir_columnas_componentes] Distribución por tamaño de combinación:')
    for cat, count in dist.items():
        print(f'    {cat:<12} -> {count:>5} medicamentos')
    
    return df

def flag_anomalies(df: pd.DataFrame) -> pd.DataFrame:
    """
    Detecta y marca registros con posibles anomalías en `Composition`.
 
    Anomalías marcadas con la columna booleana `composition_anomaly`:
        - `components_list` vacío (no se pudo parsear la composición).
        - `n_components` == 0 (no se encontró ningún componente válido).
 
    Estos registros NO se eliminan automáticamente. La decisión de
    descartarlos o imputarlos queda registrada en `docs/decisiones_limpieza.md`
    y se implementa de forma explícita si el análisis lo requiere.
 
    Args:
        df: DataFrame con las columnas `components_list` y `n_components`.
 
    Returns:
        DataFrame con la columna `composition_anomaly` añadida.
    """
    if 'n_components' not in df.columns:
        raise KeyError("La columna 'n_components' no eixste. Ejecuta 'añadir_columnas_componentes' primero.")
    
    df = df.copy()
    df['composition_anomaly'] = df['n_components'] == 0

    anomalias = df["composition_anomaly"].sum()
    print(f'[flag_anomalies] Registros con anomalía en Composition: {anomalias}')

    return df

def run_cleaning_pipeline(
    df: pd.DataFrame,
    save: bool = True,
    output_path: str | Path = DATA_LIMPIA,
) -> pd.DataFrame:
    """
    Ejecuta el flujo completo de limpieza para el foco de combinaciones.
 
    Pasos en orden:
        1. Eliminar duplicados completos.
        2. Normalizar la columna `Composition`.
        3. Extraer componentes y generar columnas derivadas.
        4. Marcar anomalías sin eliminarlas automáticamente.
        5. (Opcional) Exportar el resultado a `data/processed/`.
 
    El parámetro `save=True` exporta el CSV limpio, lo que permite
    que los notebooks de transformación y análisis trabajen siempre
    desde el dato ya procesado, sin volver a ejecutar la limpieza.
 
    Args:
        df: DataFrame raw cargado con `load_medicine_data()`.
        save: Si True, guarda el resultado en `output_path`.
        output_path: Ruta de destino del CSV limpio.
 
    Returns:
        DataFrame limpio con todas las columnas derivadas añadidas.
 
    Raises:
        ValueError: Si el DataFrame de entrada está vacío.
        IOError: Si no se puede escribir el archivo de salida.
    """
    if df.empty:
        raise ValueError('El DataFrame de entrada está vacio. Verifica la carga de datos')
    
    print("=" * 55)
    print("INICIO DEL PIPELINE DE LIMPIEZA")
    print("=" * 55)
 
    df_clean = eliminar_duplicados(df)
    df_clean = normalizar_composicion(df_clean)
    df_clean = añadir_columnas_componentes(df_clean)
    df_clean = flag_anomalies(df_clean)
 
    print("-" * 55)
    print(f"Forma final del DataFrame: {df_clean.shape}")
    print("=" * 55)
 
    if save:
        try:
            output = Path(output_path)
            output.parent.mkdir(parents=True, exist_ok=True)
            df_clean.to_csv(output, index=False)
            print(f"[run_cleaning_pipeline] CSV limpio guardado en: {output}")
        except OSError as exc:
            raise IOError(f"No se pudo guardar el archivo en {output_path}: {exc}") from exc
 
    return df_clean