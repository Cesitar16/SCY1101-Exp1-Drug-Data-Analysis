"""
Módulo de transformaciones avanzadas para el foco: Combinaciones de Componentes.
 
Responsabilidades:
    - Expandir componentes a filas individuales (explode).
    - Generar todos los pares posibles de componentes por medicamento.
    - Construir la matriz de co-ocurrencia entre componentes.
    - Exportar los DataFrames transformados a data/processed/.
 
Uso desde notebook:
    from src.enfoque_01_combinaciones_componentes.transform import run_transform_pipeline
    df_exploded, df_pairs, cooc_matrix = run_transform_pipeline(df_clean)
"""

from itertools import combinations
from pathlib import Path
import pandas as pd

RUTA_PROYECTO = Path(__file__).resolve().parents[2]
DIR_PROCESADO = RUTA_PROYECTO / "data" / "processed"
RUTA_EXPLODED = DIR_PROCESADO / "medicine_exploded.csv"
PAIRS_PATH = DIR_PROCESADO / "medicine_pairs.csv"
COOC_PATH = DIR_PROCESADO / "cooc_matrix.csv"

def explotar_componentes(df: pd.DataFrame) -> pd.DataFrame:
    """
    Expande la columna `components_list` para tener una fila por componente.
 
    Transforma el DataFrame de formato "wide" (una fila por medicamento con
    lista de componentes) a formato "long" (una fila por componente), lo que
    permite calcular frecuencias individuales y hacer agrupaciones por componente.
 
    Esta operación aumenta el número de filas: un medicamento con 3 componentes
    genera 3 filas. Las columnas restantes se repiten en cada fila resultante.
    Esto es esperado y necesario para el análisis posterior.
 
    Args:
        df: DataFrame limpio con la columna `components_list` (list[str]).
 
    Returns:
        DataFrame expandido con la columna `component` (str) en lugar de
        `components_list`. Incluye todas las columnas originales.
 
    Raises:
        KeyError: Si `components_list` no existe en el DataFrame.
 
    Example:
        Un medicamento con [A, B] genera dos filas, una con component='A'
        y otra con component='B', ambas con el mismo Medicine Name.
    """
    if 'components_list' not in df.columns:
        raise KeyError(
            "La columna 'component_list' no existe."
            "Ejecuta run_cleaning_pipeline primero."
        )
    
    antes = len(df)

    df_exploded = (
        df.assign(component=df['components_list'])
        .explode('component')
        .reset_index(drop=True)
    )

    df_exploded = df_exploded[df_exploded['component'].str.strip() != ""]

    despues = len(df_exploded)
    print(f'[explotar_componentes] Filas antes: {antes} -> después: {despues}')
    print(f"[explotar_componentes] Componentes únicos: {df_exploded['component'].nunique()}")

    return df_exploded

def generar_pares(components: list[str]) -> list[tuple[str, str]]:
    """
    Genera todos los pares posibles de componentes de una combinación.
 
    Usa `itertools.combinations` con r=2 para producir pares sin repetición
    y sin considerar el orden (A,B) == (B,A). Los componentes se ordenan
    alfabéticamente antes de generar pares para garantizar consistencia:
    independientemente del orden en que aparezcan en `Composition`,
    el par siempre se representa de la misma forma.
 
    Args:
        components: Lista de nombres de componentes de un medicamento.
 
    Returns:
        Lista de tuplas (componente_a, componente_b) ordenadas alfabéticamente.
        Retorna lista vacía si hay menos de 2 componentes (no hay par posible).
 
    Example:
        >>> generar_pares(['Amoxycillin', 'Clavulanic Acid'])
        [('Amoxycillin', 'Clavulanic Acid')]
        >>> generar_pares(['A', 'B', 'C'])
        [('A', 'B'), ('A', 'C'), ('B', 'C')]
        >>> generar_pares(['Paracetamol'])
        []
    """
    try:
        if not isinstance(components, list) or len(components) < 2:
            return []
        return list(combinations(sorted(components), 2))
    except Exception as exc:
        print(f'[generar_pares] Error procesando {components!r} -> {exc}')
        return []

def explotar_pares(df: pd.DataFrame) -> pd.DataFrame:
    """
    Genera un DataFrame con una fila por par de componentes co-ocurrentes.
 
    Para cada medicamento con N componentes, genera C(N,2) filas, una por
    cada par posible. Esto permite calcular con qué frecuencia dos componentes
    aparecen juntos en el dataset (co-ocurrencia).
 
    Args:
        df: DataFrame limpio con la columna `components_list`.
 
    Returns:
        DataFrame con las columnas `comp_a` y `comp_b` (los dos componentes
        del par) más todas las columnas originales del medicamento.
        Solo contiene medicamentos con 2 o más componentes.
 
    Raises:
        KeyError: Si `components_list` no existe en el DataFrame.
    """
    if 'components_list' not in df.columns:
        raise KeyError(
            "La columna 'component_list' no existe."
            "Ejecuta run_cleaning_pipeline primero."
        )
    
    df_multi = df[df["n_components"] >= 2].copy()
 
    df_multi["pairs"] = df_multi["components_list"].apply(generar_pares)
 
    df_pairs = df_multi.explode("pairs").reset_index(drop=True)
 
    df_pairs[["comp_a", "comp_b"]] = pd.DataFrame(
        df_pairs["pairs"].tolist(), index=df_pairs.index
    )

    df_pairs = df_pairs.dropna(subset=["comp_a", "comp_b"])
    df_pairs = df_pairs.drop(columns=["pairs"])
 
    print(f"[explotar_pares] Total de pares generados: {len(df_pairs)}")
    print(f"[explotar_pares] Pares únicos: {df_pairs[['comp_a', 'comp_b']].drop_duplicates().shape[0]}")
 
    return df_pairs

def construir_matriz_coocurrencia(
        df_pairs: pd.DataFrame,
        top_n: int = 20,
) -> pd.DataFrame:
    """
    Construye una matriz de co-ocurrencia entre los componentes más frecuentes.
 
    Usa `pd.crosstab` para contar cuántas veces cada par (comp_a, comp_b)
    aparece en el dataset. El resultado es una matriz cuadrada y simétrica
    donde el valor [i][j] indica cuántos medicamentos contienen ambos
    componentes i y j simultáneamente.
 
    Se limita a los `top_n` componentes más frecuentes para que la matriz
    sea legible en el heatmap. Una matriz de 500×500 no tiene valor visual.
 
    Args:
        df_pairs: DataFrame generado por `explotar_pares`, con columnas
            `comp_a` y `comp_b`.
        top_n: Número de componentes más frecuentes a incluir en la matriz.
            Por defecto 20, que es el tamaño óptimo para un heatmap legible.
 
    Returns:
        DataFrame cuadrado (top_n × top_n) con la matriz de co-ocurrencia.
        Índices y columnas son nombres de componentes.
 
    Raises:
        KeyError: Si `comp_a` o `comp_b` no existen en df_pairs.
        ValueError: Si df_pairs está vacío.
    """

    if df_pairs.empty:
        raise ValueError("df_pairs está vacío. Ejecuta explotar_pares primero.")

    for col in ["comp_a", "comp_b"]:
        if col not in df_pairs.columns:
            raise KeyError(f"La columna '{col}' no existe en df_pairs.")
        
    freq_a = df_pairs['comp_a'].value_counts()
    freq_b = df_pairs['comp_b'].value_counts()
    freq_total = (freq_a.add(freq_b, fill_value=0)
                  .sort_values(ascending=False))
    top_componentes = freq_total.head(top_n).index.tolist()

    mask = (
        df_pairs["comp_a"].isin(top_componentes) &
        df_pairs["comp_b"].isin(top_componentes)
    )
    
    df_filtered = df_pairs[mask]

    cooc = pd.crosstab(df_filtered['comp_a'], df_filtered['comp_b'])
    cooc = cooc.add(cooc.T, fill_value=0)
    cooc = cooc.reindex(index=top_componentes,columns=top_componentes,fill_value=0)
    cooc = cooc.fillna(0).astype(int)

    print(f'[construir_matriz_coocurrencia] Matriz generada {cooc.shape[0]}×{cooc.shape[1]}')
    

    return cooc

def run_transform_pipeline(
    df: pd.DataFrame,
    top_n: int = 20,
    save: bool = True,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Ejecuta el flujo completo de transformaciones sobre el DataFrame limpio.
 
    Pasos en orden:
        1. Explotar componentes → df_exploded (una fila por componente).
        2. Explotar pares → df_pairs (una fila por par de componentes).
        3. Construir matriz de co-ocurrencia → cooc_matrix (top_n × top_n).
        4. (Opcional) Exportar los tres DataFrames a data/processed/.
 
    Args:
        df: DataFrame limpio generado por run_cleaning_pipeline.
        top_n: Número de componentes top para la matriz de co-ocurrencia.
        save: Si True, exporta los tres DataFrames como CSV.
 
    Returns:
        Tupla (df_exploded, df_pairs, cooc_matrix).
 
    Raises:
        ValueError: Si el DataFrame de entrada está vacío.
    """
    if df.empty:
        raise ValueError("El DataFrame de entrada está vacío.")
 
    print("=" * 55)
    print("INICIO DEL PIPELINE DE TRANSFORMACIONES")
    print("=" * 55)
 
    df_exploded = explotar_componentes(df)
    df_pairs = explotar_pares(df)
    cooc_matrix = construir_matriz_coocurrencia(df_pairs, top_n=top_n)
 
    print("-" * 55)
    print(f"df_exploded shape : {df_exploded.shape}")
    print(f"df_pairs shape    : {df_pairs.shape}")
    print(f"cooc_matrix shape : {cooc_matrix.shape}")
    print("=" * 55)
 
    if save:
        try:
            DIR_PROCESADO.mkdir(parents=True, exist_ok=True)
 
            # La columna components_list contiene listas Python, que no se
            # serializan bien en CSV. La convertimos a string para exportar.
            df_exploded_csv = df_exploded.copy()
            df_exploded_csv["components_list"] = df_exploded_csv["components_list"].astype(str)
            df_exploded_csv.to_csv(RUTA_EXPLODED, index=False)
 
            df_pairs_csv = df_pairs.copy()
            df_pairs_csv["components_list"] = df_pairs_csv["components_list"].astype(str)
            df_pairs_csv.to_csv(PAIRS_PATH, index=False)
 
            cooc_matrix.to_csv(COOC_PATH)
 
            print(f"[run_transform_pipeline] Archivos guardados en: {DIR_PROCESADO}")
        except OSError as exc:
            raise IOError(f"No se pudo guardar los archivos: {exc}") from exc
 
    return df_exploded, df_pairs, cooc_matrix
