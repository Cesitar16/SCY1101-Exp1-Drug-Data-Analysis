"""
Módulo de análisis y visualización para el foco: Combinaciones de Componentes.
 
Responsabilidades:
    - Calcular rankings de combinaciones y componentes más frecuentes.
    - Generar visualizaciones guardadas en outputs/figures/.
    - Todas las funciones son reutilizables e independientes entre sí.
 
Uso desde notebook:
    from src.enfoque_01_combinaciones_componentes.analysis import run_analysis_pipeline
    run_analysis_pipeline(df_clean, df_exploded, df_pairs, cooc_matrix)
"""
from pathlib import Path
 
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import networkx as nx
import numpy as np
import pandas as pd
import seaborn as sns

RUTA_PROYECTO = Path(__file__).resolve().parents[2]
FIGURES_DIR = RUTA_PROYECTO / "outputs" / "figures"
RUTA_TABLAS = RUTA_PROYECTO / "outputs" / "tables"

# Estilo visual consistente en todos los gráficos
plt.rcParams.update({
    "figure.dpi": 120,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "font.size": 11,
})

def _guardar_figura(fig: plt.Figure, nombre: str) -> None:
    """
    Guarda una figura en outputs/figures/ y la cierra para liberar memoria.
 
    Args:
        fig: Figura de matplotlib a guardar.
        nombre: Nombre del archivo sin extensión (se guarda como .png).
    """
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    ruta = FIGURES_DIR / f"{nombre}.png"
    fig.savefig(ruta, bbox_inches="tight")
    plt.show()
    plt.close(fig)
    print(f"[analysis] Figura guardada: {ruta}")

def _guardar_tabla(df: pd.DataFrame, nombre: str) -> None:
    """
    Exporta un DataFrame como CSV en outputs/tables/.
 
    Args:
        df: DataFrame a exportar.
        nombre: Nombre del archivo sin extensión.
    """
    RUTA_TABLAS.mkdir(parents=True, exist_ok=True)
    ruta = RUTA_TABLAS / f"{nombre}.csv"
    df.to_csv(ruta, index=False)
    print(f"[analysis] Tabla guardada: {ruta}")

# ---------------------------------------------------------------------------
# Gráfico 1: Top 20 pares de componentes más frecuentes
# ---------------------------------------------------------------------------

def plot_top_pares(df_pairs: pd.DataFrame, top_n: int = 20) -> pd.DataFrame:
    """
    Genera un barplot horizontal con los pares de componentes más frecuentes.
 
    Agrupa df_pairs por (comp_a, comp_b) y cuenta ocurrencias. Cada par
    representa una combinación de 2 componentes que aparece en el dataset.
    El gráfico responde: ¿qué dúos dominan el mercado farmacéutico?
 
    Args:
        df_pairs: DataFrame con columnas `comp_a` y `comp_b`.
        top_n: Número de pares a mostrar. Por defecto 20.
 
    Returns:
        DataFrame con el ranking de pares y sus frecuencias.
 
    Raises:
        KeyError: Si `comp_a` o `comp_b` no existen en df_pairs.
    """
    for col in ["comp_a", "comp_b"]:
        if col not in df_pairs.columns:
            raise KeyError(f"Columna '{col}' no encontrada en df_pairs.")
 
    # Crear etiqueta legible del par y contar frecuencias
    ranking = (
        df_pairs
        .assign(par=df_pairs["comp_a"] + " + " + df_pairs["comp_b"])
        .groupby("par", as_index=False)
        .size()
        .rename(columns={"size": "frecuencia"})
        .sort_values("frecuencia", ascending=False)
        .head(top_n)
        .reset_index(drop=True)
    )
 
    fig, ax = plt.subplots(figsize=(10, 8))
    ax.barh(
        ranking["par"][::-1],
        ranking["frecuencia"][::-1],
        color="#2196F3",
        edgecolor="white",
    )
    ax.set_xlabel("Número de medicamentos")
    ax.set_title(f"Top {top_n} pares de componentes más frecuentes", fontweight="bold")
    ax.set_ylabel("")
 
    # Etiquetas de valor al final de cada barra
    for i, v in enumerate(ranking["frecuencia"][::-1]):
        ax.text(v + 1, i, str(v), va="center", fontsize=9)
 
    _guardar_figura(fig, "top_pares_componentes")
    _guardar_tabla(ranking, "top_pares_componentes")
 
    return ranking

# ---------------------------------------------------------------------------
# Gráfico 2: Top 20 componentes individuales más frecuentes
# ---------------------------------------------------------------------------
 
 
def plot_top_componentes(df_exploded: pd.DataFrame, top_n: int = 20) -> pd.DataFrame:
    """
    Genera un barplot con los componentes individuales más frecuentes.
 
    Usa df_exploded (una fila por componente) para contar en cuántos
    medicamentos distintos aparece cada componente. Responde: ¿qué
    componentes son los "hubs" del dataset?
 
    Args:
        df_exploded: DataFrame expandido con columna `component`.
        top_n: Número de componentes a mostrar.
 
    Returns:
        DataFrame con el ranking de componentes y sus frecuencias.
 
    Raises:
        KeyError: Si `component` no existe en df_exploded.
    """
    if "component" not in df_exploded.columns:
        raise KeyError("Columna 'component' no encontrada en df_exploded.")
 
    ranking = (
        df_exploded
        .groupby("component", as_index=False)
        .size()
        .rename(columns={"size": "frecuencia"})
        .sort_values("frecuencia", ascending=False)
        .head(top_n)
        .reset_index(drop=True)
    )
 
    fig, ax = plt.subplots(figsize=(10, 7))
    colores = ["#E53935" if i == 0 else "#42A5F5" for i in range(top_n)]
    ax.barh(
        ranking["component"][::-1],
        ranking["frecuencia"][::-1],
        color=colores[::-1],
        edgecolor="white",
    )
    ax.set_xlabel("Número de medicamentos")
    ax.set_title(f"Top {top_n} componentes activos más frecuentes", fontweight="bold")
 
    leyenda = [
        mpatches.Patch(color="#E53935", label="Componente más frecuente"),
        mpatches.Patch(color="#42A5F5", label="Resto del top"),
    ]
    ax.legend(handles=leyenda, loc="lower right")
 
    for i, v in enumerate(ranking["frecuencia"][::-1]):
        ax.text(v + 1, i, str(v), va="center", fontsize=9)
 
    _guardar_figura(fig, "top_componentes_individuales")
    _guardar_tabla(ranking, "top_componentes_individuales")
 
    return ranking

# ---------------------------------------------------------------------------
# Gráfico 3: Heatmap de co-ocurrencia
# ---------------------------------------------------------------------------
 
 
def plot_heatmap_coocurrencia(cooc_matrix: pd.DataFrame) -> None:
    """
    Genera un heatmap de la matriz de co-ocurrencia entre componentes.
 
    Cada celda [i][j] muestra cuántos medicamentos contienen ambos
    componentes i y j. La diagonal es 0 (un componente no co-ocurre
    consigo mismo). El heatmap permite identificar visualmente qué
    pares tienen mayor afinidad de combinación.
 
    Args:
        cooc_matrix: Matriz cuadrada generada por construir_matriz_coocurrencia.
 
    Raises:
        ValueError: Si cooc_matrix está vacía.
    """
    if cooc_matrix.empty:
        raise ValueError("cooc_matrix está vacía.")
 
    fig, ax = plt.subplots(figsize=(14, 11))
 
    # Máscara para la diagonal: visualmente es más limpio no colorear
    # la diagonal ya que siempre es 0 y distrae del patrón real.
    mascara = np.eye(len(cooc_matrix), dtype=bool)
 
    sns.heatmap(
        cooc_matrix,
        mask=mascara,
        annot=True,
        fmt="d",
        cmap="Blues",
        linewidths=0.5,
        ax=ax,
        cbar_kws={"label": "Número de medicamentos"},
    )
    ax.set_title("Matriz de co-ocurrencia entre componentes activos\n(Top 20 más frecuentes)",
                 fontweight="bold", pad=15)
    ax.set_xlabel("Componente B")
    ax.set_ylabel("Componente A")
    plt.xticks(rotation=45, ha="right")
    plt.yticks(rotation=0)
 
    _guardar_figura(fig, "heatmap_coocurrencia")

# ---------------------------------------------------------------------------
# Gráfico 4: Boxplot de efectos secundarios por tamaño de combinación
# ---------------------------------------------------------------------------
 
 
def plot_efectos_secundarios_por_tamanio(df_clean: pd.DataFrame) -> None:
    """
    Genera un boxplot que relaciona el número de efectos secundarios
    con el tamaño de la combinación de componentes.
 
    El número de efectos secundarios se aproxima contando las palabras
    en la columna `Side_effects`, separadas por coma. Esta es una
    aproximación válida para el análisis exploratorio dado que el campo
    no está estructurado.
 
    Responde: ¿los medicamentos con más componentes tienen más efectos
    secundarios?
 
    Args:
        df_clean: DataFrame limpio con columnas `Side_effects`,
            `size_category` y `n_components`.
 
    Raises:
        KeyError: Si alguna columna requerida no existe.
    """
    for col in ["Side_effects", "size_category", "n_components"]:
        if col not in df_clean.columns:
            raise KeyError(f"Columna '{col}' no encontrada en df_clean.")
 
    df = df_clean.copy()
 
    # Aproximación vectorizada: contar comas + 1 da el número de efectos
    # listados. Es más rápido que split().apply(len) para strings largos.
    df["n_efectos"] = df["Side_effects"].str.split().apply(
        lambda words: sum(1 for w in words if w[0].isupper()) if words else 0
    )
 
    orden = ["mono", "duo", "trio", "cuádruple", "complejo"]
    datos_por_categoria = [
        df.loc[df["size_category"] == cat, "n_efectos"].dropna().values
        for cat in orden
        if cat in df["size_category"].cat.categories
    ]
    etiquetas = [
        cat for cat in orden
        if cat in df["size_category"].cat.categories
    ]
 
    fig, ax = plt.subplots(figsize=(10, 6))
    bp = ax.boxplot(
        datos_por_categoria,
        labels=etiquetas,
        patch_artist=True,
        medianprops={"color": "black", "linewidth": 2},
    )
 
    colores = ["#64B5F6", "#42A5F5", "#1E88E5", "#1565C0", "#0D47A1"]
    for patch, color in zip(bp["boxes"], colores[:len(etiquetas)]):
        patch.set_facecolor(color)
        patch.set_alpha(0.8)
 
    ax.set_xlabel("Tamaño de combinación")
    ax.set_ylabel("Número de efectos secundarios")
    ax.set_title("Efectos secundarios según tamaño de combinación",
                 fontweight="bold")
 
    _guardar_figura(fig, "boxplot_efectos_secundarios")

# ---------------------------------------------------------------------------
# Gráfico 5: Network graph de co-ocurrencia
# ---------------------------------------------------------------------------
 
 
def plot_network_graph(
    df_pairs: pd.DataFrame,
    top_n_componentes: int = 15,
    min_frecuencia: int = 5,
) -> None:
    """
    Genera un grafo de red donde los nodos son componentes y las aristas
    representan co-ocurrencias frecuentes entre ellos.
 
    Cada nodo es un componente activo. El grosor de cada arista es
    proporcional a la frecuencia con que ambos componentes aparecen
    juntos. El tamaño del nodo es proporcional a su grado (número de
    conexiones), permitiendo identificar visualmente los componentes
    "hub" que dominan las combinaciones.
 
    Args:
        df_pairs: DataFrame con columnas `comp_a`, `comp_b`.
        top_n_componentes: Número de componentes más frecuentes a incluir.
        min_frecuencia: Umbral mínimo de co-ocurrencia para dibujar una arista.
            Filtra conexiones débiles que ensucian el grafo.
 
    Raises:
        KeyError: Si `comp_a` o `comp_b` no existen en df_pairs.
    """
    for col in ["comp_a", "comp_b"]:
        if col not in df_pairs.columns:
            raise KeyError(f"Columna '{col}' no encontrada en df_pairs.")
 
    # Seleccionar los top_n componentes más frecuentes
    freq = (
        pd.concat([df_pairs["comp_a"], df_pairs["comp_b"]])
        .value_counts()
        .head(top_n_componentes)
    )
    top_componentes = freq.index.tolist()
 
    # Filtrar pares donde ambos están en el top y superan el umbral
    df_filtered = df_pairs[
        df_pairs["comp_a"].isin(top_componentes) &
        df_pairs["comp_b"].isin(top_componentes)
    ]
 
    edge_weights = (
        df_filtered
        .groupby(["comp_a", "comp_b"])
        .size()
        .reset_index(name="peso")
    )
    edge_weights = edge_weights[edge_weights["peso"] >= min_frecuencia]
 
    # Construir el grafo con networkx
    G = nx.Graph()
    for _, row in edge_weights.iterrows():
        G.add_edge(row["comp_a"], row["comp_b"], weight=row["peso"])
 
    if G.number_of_nodes() == 0:
        print("[plot_network_graph] Sin nodos para graficar con los filtros actuales.")
        return
 
    # Layout: spring_layout distribuye nodos por fuerza de conexión.
    # seed fija la posición para reproducibilidad del gráfico.
    pos = nx.spring_layout(G, seed=42, k=2)
 
    grados = dict(G.degree())
    tamanios_nodo = [300 + grados[n] * 200 for n in G.nodes()]
 
    pesos_arista = [G[u][v]["weight"] for u, v in G.edges()]
    max_peso = max(pesos_arista) if pesos_arista else 1
    grosores = [0.5 + 4 * (w / max_peso) for w in pesos_arista]
 
    fig, ax = plt.subplots(figsize=(18, 13))
 
    nx.draw_networkx_nodes(G, pos, node_size=tamanios_nodo,
                           node_color="#1E88E5", alpha=0.85, ax=ax)
    nx.draw_networkx_edges(G, pos, width=grosores,
                           edge_color="#90CAF9", alpha=0.7, ax=ax)
    labels = {n: n for n in G.nodes()}
    nx.draw_networkx_labels(G, pos, labels=labels, font_size=7,
                            font_color="black", font_weight="bold",
                            verticalalignment="bottom", ax=ax)
 
    ax.set_title(
        f"Red de co-ocurrencia entre componentes activos\n"
        f"(Top {top_n_componentes} componentes | umbral mínimo: {min_frecuencia} medicamentos)",
        fontweight="bold",
    )
    ax.axis("off")
 
    _guardar_figura(fig, "network_graph_coocurrencia")

# ---------------------------------------------------------------------------
# Gráfico 6: Histograma de distribución de n_components
# ---------------------------------------------------------------------------
 
 
def plot_histograma_componentes(df_clean: pd.DataFrame) -> None:
    """
    Genera un histograma de la distribución de medicamentos según su
    número de componentes activos.
 
    Permite visualizar qué tan común es cada tamaño de combinación en el
    dataset. Responde: ¿el mercado farmacéutico está dominado por
    monocomponentes o por combinaciones?
 
    Args:
        df_clean: DataFrame limpio con la columna `n_components`.
 
    Raises:
        KeyError: Si `n_components` no existe en df_clean.
    """
    if "n_components" not in df_clean.columns:
        raise KeyError("Columna 'n_components' no encontrada en df_clean.")
 
    conteos = df_clean["n_components"].value_counts().sort_index()
 
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.bar(
        conteos.index,
        conteos.values,
        color="#1E88E5",
        edgecolor="white",
        width=0.6,
    )
 
    # Etiqueta de valor sobre cada barra
    for x, y in zip(conteos.index, conteos.values):
        ax.text(x, y + 20, str(y), ha="center", va="bottom", fontsize=9)
 
    ax.set_xlabel("Número de componentes activos")
    ax.set_ylabel("Número de medicamentos")
    ax.set_title("Distribución de medicamentos según número de componentes",
                 fontweight="bold")
    ax.set_xticks(conteos.index)
 
    _guardar_figura(fig, "histograma_n_componentes")
 
 
# ---------------------------------------------------------------------------
# Gráfico 7: Scatterplot valoración vs número de componentes
# ---------------------------------------------------------------------------
 
 
def plot_scatter_valoracion(df_clean: pd.DataFrame) -> None:
    """
    Genera un scatterplot que relaciona la valoración excelente de usuarios
    con el número de componentes de cada medicamento.
 
    Para reducir el solapamiento de puntos (overplotting), se aplica jitter
    horizontal aleatorio sobre `n_components`, ya que es una variable discreta.
    Los puntos se colorean según `size_category` para facilitar la lectura.
 
    Responde: ¿los medicamentos con más componentes tienen mejor o peor
    valoración por parte de los usuarios?
 
    Args:
        df_clean: DataFrame limpio con columnas `n_components`,
            `Excellent Review %` y `size_category`.
 
    Raises:
        KeyError: Si alguna columna requerida no existe.
    """
    for col in ["n_components", "Excellent Review %", "size_category"]:
        if col not in df_clean.columns:
            raise KeyError(f"Columna '{col}' no encontrada en df_clean.")
 
    df = df_clean.copy()
 
    # Jitter: desplazamiento aleatorio pequeño sobre el eje X para evitar
    # que todos los puntos de n_components=1 se apilen en la misma columna.
    # seed=42 garantiza reproducibilidad del gráfico.
    rng = np.random.default_rng(seed=42)
    df["n_components_jitter"] = df["n_components"] + rng.uniform(-0.3, 0.3, size=len(df))
 
    # Mapa de colores por categoría
    colores_cat = {
        "mono": "#90CAF9",
        "duo": "#42A5F5",
        "trio": "#1E88E5",
        "cuádruple": "#1565C0",
        "complejo": "#0D47A1",
    }
    colores = df["size_category"].map(colores_cat).fillna("#90CAF9")
 
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.scatter(
        df["n_components_jitter"],
        df["Excellent Review %"],
        c=colores,
        alpha=0.4,
        s=15,
        edgecolors="none",
    )
 
    # Línea de tendencia (media por grupo) para facilitar la lectura
    media_por_grupo = df.groupby("n_components")["Excellent Review %"].mean()
    ax.plot(
        media_por_grupo.index,
        media_por_grupo.values,
        color="#E53935",
        linewidth=2,
        marker="o",
        markersize=6,
        label="Media por grupo",
        zorder=5,
    )
 
    # Leyenda de categorías
    leyenda = [
        mpatches.Patch(color=color, label=cat)
        for cat, color in colores_cat.items()
        if cat in df["size_category"].values
    ]
    leyenda.append(
        plt.Line2D([0], [0], color="#E53935", linewidth=2,
                   marker="o", label="Media por grupo")
    )
    ax.legend(handles=leyenda, loc="upper right", fontsize=8)
 
    ax.set_xlabel("Número de componentes activos")
    ax.set_ylabel("Valoración excelente (%)")
    ax.set_title("Valoración de usuarios según número de componentes",
                 fontweight="bold")
    ax.set_xticks(sorted(df["n_components"].unique()))
 
    _guardar_figura(fig, "scatter_valoracion_componentes")
 
 
# ---------------------------------------------------------------------------
# REEMPLAZA run_analysis_pipeline con esta versión actualizada
# (agrega las llamadas a los 2 gráficos nuevos al final)
# ---------------------------------------------------------------------------
 
 
def run_analysis_pipeline(
    df_clean: pd.DataFrame,
    df_exploded: pd.DataFrame,
    df_pairs: pd.DataFrame,
    cooc_matrix: pd.DataFrame,
) -> None:
    """
    Ejecuta el pipeline completo de análisis y genera todos los gráficos.
 
    Llama en orden a todas las funciones de visualización. Cada gráfico
    se guarda automáticamente en outputs/figures/ y las tablas de ranking
    se exportan a outputs/tables/.
 
    Args:
        df_clean: DataFrame limpio (salida de run_cleaning_pipeline).
        df_exploded: DataFrame expandido (salida de explotar_componentes).
        df_pairs: DataFrame de pares (salida de explotar_pares).
        cooc_matrix: Matriz de co-ocurrencia (salida de construir_matriz_coocurrencia).
 
    Raises:
        ValueError: Si alguno de los DataFrames de entrada está vacío.
    """
    for nombre, df in [("df_clean", df_clean), ("df_exploded", df_exploded),
                       ("df_pairs", df_pairs), ("cooc_matrix", cooc_matrix)]:
        if df.empty:
            raise ValueError(f"El DataFrame '{nombre}' está vacío.")
 
    print("=" * 55)
    print("INICIO DEL PIPELINE DE ANÁLISIS")
    print("=" * 55)
 
    print("\n[1/7] Generando top pares de componentes...")
    plot_top_pares(df_pairs, top_n=20)
 
    print("\n[2/7] Generando top componentes individuales...")
    plot_top_componentes(df_exploded, top_n=20)
 
    print("\n[3/7] Generando heatmap de co-ocurrencia...")
    plot_heatmap_coocurrencia(cooc_matrix)
 
    print("\n[4/7] Generando boxplot de efectos secundarios...")
    plot_efectos_secundarios_por_tamanio(df_clean)
 
    print("\n[5/7] Generando network graph...")
    plot_network_graph(df_pairs, top_n_componentes=15, min_frecuencia=5)
 
    print("\n[6/7] Generando histograma de componentes...")
    plot_histograma_componentes(df_clean)
 
    print("\n[7/7] Generando scatterplot de valoración...")
    plot_scatter_valoracion(df_clean)
 
    print("\n" + "=" * 55)
    print("ANÁLISIS COMPLETO")
    print(f"Figuras guardadas en : {FIGURES_DIR}")
    print(f"Tablas guardadas en  : {RUTA_TABLAS}")
    print("=" * 55)