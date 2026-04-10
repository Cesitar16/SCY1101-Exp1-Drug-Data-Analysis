"""
Módulo de análisis y visualización para el foco: Efectos Secundarios por Componentes.

Responsabilidades:
    - Calcular rankings de efectos secundarios y componentes con mayor diversidad de efectos.
    - Generar visualizaciones guardadas en outputs/figures/.
    - Exportar tablas de ranking a outputs/tables/.
    - Todas las funciones de plot son reutilizables e independientes entre sí.

Uso desde notebook:
    from src.enfoque_03_efectos_secundarios_componentes.analysis import run_analysis_pipeline
    run_analysis_pipeline(df_clean, df_long, crosstab, crosstab_norm)
"""

from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
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


# ---------------------------------------------------------------------------
# Helpers privados de guardado
# ---------------------------------------------------------------------------

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
# Gráfico 1: Top efectos secundarios globales
# ---------------------------------------------------------------------------

def plot_top_efectos(df: pd.DataFrame, top_n: int = 15) -> pd.DataFrame:
    """
    Genera un barplot horizontal con los efectos secundarios más frecuentes.

    Agrega las listas de `efectos_secundarios` de cada medicamento y cuenta
    cuántos medicamentos presentan cada efecto. El gráfico responde:
    ¿cuáles son los efectos secundarios transversales en el dataset?

    Args:
        df: DataFrame limpio con la columna `efectos_secundarios` (list[str]).
        top_n: Número de efectos a mostrar. Por defecto 15.

    Returns:
        DataFrame con el ranking de efectos y sus frecuencias.

    Raises:
        KeyError: Si `efectos_secundarios` no existe en df.
    """
    if "efectos_secundarios" not in df.columns:
        raise KeyError("Columna 'efectos_secundarios' no encontrada en df.")

    ranking = (
        df["efectos_secundarios"]
        .explode()
        .dropna()
        .value_counts()
        .head(top_n)
        .reset_index()
        .rename(columns={"efectos_secundarios": "efecto", "count": "frecuencia"})
    )

    # Paleta degradada para resaltar la magnitud de cada efecto
    colores = [
        "#E53935" if i == 0 else "#EF9A9A" if i < 3 else "#42A5F5"
        for i in range(len(ranking))
    ]

    fig, ax = plt.subplots(figsize=(10, 8))
    ax.barh(
        ranking["efecto"][::-1],
        ranking["frecuencia"][::-1],
        color=colores[::-1],
        edgecolor="white",
    )
    ax.set_xlabel("Número de medicamentos")
    ax.set_title(f"Top {top_n} efectos secundarios más frecuentes", fontweight="bold")

    leyenda = [
        mpatches.Patch(color="#E53935", label="Efecto más frecuente"),
        mpatches.Patch(color="#EF9A9A", label="Top 3"),
        mpatches.Patch(color="#42A5F5", label="Resto del top"),
    ]
    ax.legend(handles=leyenda, loc="lower right")

    for i, v in enumerate(ranking["frecuencia"][::-1]):
        ax.text(v + 1, i, str(v), va="center", fontsize=9)

    _guardar_figura(fig, "e03_top_efectos_globales")
    _guardar_tabla(ranking, "e03_top_efectos_globales")

    return ranking


# ---------------------------------------------------------------------------
# Gráfico 2: Top componentes con mayor diversidad de efectos
# ---------------------------------------------------------------------------

def plot_componentes_por_diversidad_efectos(
    df_long: pd.DataFrame,
    top_n: int = 20,
) -> pd.DataFrame:
    """
    Genera un barplot con los componentes que tienen mayor cantidad de efectos distintos.

    Cuenta cuántos efectos secundarios únicos tiene cada componente en el dataset.
    Responde: ¿qué componentes presentan mayor riesgo en términos de variedad de efectos?

    Args:
        df_long: DataFrame expandido (resultado de `explotar_todo`) con columnas
            `componentes` y `efectos_secundarios`.
        top_n: Número de componentes a mostrar.

    Returns:
        DataFrame con el ranking de componentes y su número de efectos distintos.

    Raises:
        KeyError: Si `componentes` o `efectos_secundarios` no existen en df_long.
    """
    for col in ["componentes", "efectos_secundarios"]:
        if col not in df_long.columns:
            raise KeyError(f"Columna '{col}' no encontrada en df_long.")

    ranking = (
        df_long
        .groupby("componentes")["efectos_secundarios"]
        .nunique()
        .sort_values(ascending=False)
        .head(top_n)
        .reset_index()
        .rename(columns={"efectos_secundarios": "efectos_distintos"})
    )

    fig, ax = plt.subplots(figsize=(10, 8))
    ax.barh(
        ranking["componentes"][::-1],
        ranking["efectos_distintos"][::-1],
        color="#5E35B1",
        edgecolor="white",
    )
    ax.set_xlabel("Número de efectos secundarios distintos")
    ax.set_title(
        f"Top {top_n} componentes con mayor diversidad de efectos secundarios",
        fontweight="bold",
    )

    for i, v in enumerate(ranking["efectos_distintos"][::-1]):
        ax.text(v + 0.3, i, str(v), va="center", fontsize=9)

    _guardar_figura(fig, "e03_componentes_por_diversidad_efectos")
    _guardar_tabla(ranking, "e03_componentes_por_diversidad_efectos")

    return ranking


# ---------------------------------------------------------------------------
# Gráfico 3: Heatmap del crosstab normalizado (componente × efecto)
# ---------------------------------------------------------------------------


def _ordenar_filas_heatmap(
    matriz: pd.DataFrame,
    estrategia: str = "max_intensity",
) -> pd.DataFrame:
    """
    Reordena las filas de una matriz de asociación normalizada para mejorar
    la narrativa visual del heatmap.

    Args:
        matriz: Submatriz normalizada (filas = componentes, columnas = efectos).
        estrategia: Criterio de ordenamiento.
            - "max_intensity": ordena por el valor máximo de cada fila.
              Pone arriba los componentes con asociaciones más fuertes.
            - "entropy": ordena por entropía de Shannon. Pone arriba los
              perfiles más concentrados (baja entropía) y abajo los más
              dispersos (alta entropía).

    Returns:
        Matriz con las filas reordenadas según la estrategia.

    Raises:
        ValueError: Si la estrategia no es reconocida.
    """
    estrategias_validas = {"max_intensity", "entropy"}
    if estrategia not in estrategias_validas:
        raise ValueError(
            f"Estrategia '{estrategia}' no reconocida. "
            f"Opciones válidas: {sorted(estrategias_validas)}"
        )

    try:
        if estrategia == "max_intensity":
            scores = matriz.max(axis=1)
            indice_ordenado = scores.sort_values(ascending=False).index
        else:  # entropy
            # Entropía de Shannon: -sum(p * log(p))
            # Baja entropía = perfil concentrado, alta entropía = disperso
            matriz_segura = matriz.replace(0, np.nan)
            scores = -(matriz_segura * np.log(matriz_segura)).sum(axis=1)
            # Concentrados arriba → orden ascendente de entropía
            indice_ordenado = scores.sort_values(ascending=True).index

        return matriz.loc[indice_ordenado]

    except Exception as exc:
        raise RuntimeError(
            f"Error al ordenar la matriz con estrategia '{estrategia}': {exc}"
        ) from exc


def plot_heatmap_componente_efecto(
    crosstab_norm: pd.DataFrame,
    top_n_componentes: int = 20,
    top_n_efectos: int = 20,
    estrategia_orden: str = "max_intensity",
) -> None:
    """
    Genera un heatmap de la tabla normalizada componente × efecto.

    Cada celda [i][j] muestra la proporción de registros del componente i
    que tienen el efecto j. Al estar normalizado por fila, permite comparar
    patrones entre componentes independientemente de su frecuencia total.

    La selección de los top componentes se hace por frecuencia (suma de
    proporciones), pero el orden visual se reorganiza según `estrategia_orden`
    para que los componentes con asociaciones más fuertes aparezcan arriba.

    Args:
        crosstab_norm: Tabla normalizada por fila generada por `normalizar_crosstab`.
        top_n_componentes: Número de componentes más frecuentes a mostrar.
        top_n_efectos: Número de efectos a mostrar en el eje X.
        estrategia_orden: Cómo ordenar las filas del heatmap.
            - "max_intensity" (default): los componentes con asociaciones
              más intensas aparecen arriba (ej: simethicone, tetanus toxoid).
            - "entropy": los componentes con perfiles más concentrados
              aparecen arriba; los más dispersos abajo.

    Raises:
        ValueError: Si crosstab_norm está vacía o la estrategia es inválida.
    """
    if crosstab_norm.empty:
        raise ValueError("crosstab_norm está vacía.")

    # 1. Selección por frecuencia (mantiene los componentes/efectos relevantes)
    top_comp = (
        crosstab_norm.sum(axis=1)
        .sort_values(ascending=False)
        .head(top_n_componentes)
        .index
    )
    top_efec = (
        crosstab_norm.sum(axis=0)
        .sort_values(ascending=False)
        .head(top_n_efectos)
        .index
    )
    submatriz = crosstab_norm.loc[top_comp, top_efec]

    # 2. Reordenamiento visual por intensidad o entropía
    submatriz = _ordenar_filas_heatmap(submatriz, estrategia=estrategia_orden)

    # 3. Render
    fig, ax = plt.subplots(figsize=(15, 10))

    sns.heatmap(
        submatriz,
        annot=True,
        fmt=".2f",
        cmap="Blues",
        linewidths=0.5,
        ax=ax,
        cbar_kws={"label": "Proporción relativa al componente"},
    )

    titulo_orden = {
        "max_intensity": "ordenado por intensidad máxima",
        "entropy": "ordenado por entropía (concentrados arriba)",
    }[estrategia_orden]

    ax.set_title(
        f"Asociación componente → efecto secundario (normalizado por fila)\n"
        f"(Top {top_n_componentes} componentes | Top {top_n_efectos} efectos | {titulo_orden})",
        fontweight="bold",
        pad=15,
    )
    ax.set_xlabel("Efecto secundario")
    ax.set_ylabel("Componente activo")
    plt.xticks(rotation=45, ha="right")
    plt.yticks(rotation=0)

    _guardar_figura(fig, f"e03_heatmap_componente_efecto_norm_{estrategia_orden}")


# ---------------------------------------------------------------------------
# Gráfico 4: Boxplot de efectos secundarios por número de componentes
# ---------------------------------------------------------------------------

def plot_efectos_por_n_componentes(df_clean: pd.DataFrame) -> None:
    """
    Genera un boxplot que relaciona el número de efectos secundarios con el
    número de componentes activos del medicamento.

    Responde: ¿los medicamentos con más componentes tienen más efectos secundarios?
    Esta es la pregunta de complejidad del Enfoque 3.

    Args:
        df_clean: DataFrame limpio con columnas `n_componentes` y `n_efectos`.

    Raises:
        KeyError: Si alguna columna requerida no existe.
    """
    for col in ["n_componentes", "n_efectos"]:
        if col not in df_clean.columns:
            raise KeyError(f"Columna '{col}' no encontrada en df_clean.")

    df = df_clean.copy()

    # Limitar a medicamentos con hasta 6 componentes para una visualización limpia
    df = df[df["n_componentes"] <= 6]
    orden = sorted(df["n_componentes"].unique())

    datos_por_grupo = [
        df.loc[df["n_componentes"] == n, "n_efectos"].dropna().values
        for n in orden
    ]

    fig, ax = plt.subplots(figsize=(10, 6))
    bp = ax.boxplot(
        datos_por_grupo,
        labels=orden,
        patch_artist=True,
        medianprops={"color": "black", "linewidth": 2},
    )

    # Paleta azul progresiva: más componentes = azul más oscuro
    colores = ["#90CAF9", "#64B5F6", "#42A5F5", "#1E88E5", "#1565C0", "#0D47A1"]
    for patch, color in zip(bp["boxes"], colores[:len(orden)]):
        patch.set_facecolor(color)
        patch.set_alpha(0.8)

    ax.set_xlabel("Número de componentes activos")
    ax.set_ylabel("Número de efectos secundarios")
    ax.set_title(
        "Efectos secundarios según número de componentes del medicamento",
        fontweight="bold",
    )

    _guardar_figura(fig, "e03_boxplot_efectos_por_n_componentes")


# ---------------------------------------------------------------------------
# Gráfico 5: Top efectos por componente específico (detalle)
# ---------------------------------------------------------------------------

def plot_top_efectos_por_componente(
    crosstab: pd.DataFrame,
    top_n_efectos: int = 10,
    top_n_componentes: int = 5,
) -> pd.DataFrame:
    """
    Genera un barplot comparativo de los efectos más frecuentes para los
    componentes más representados del dataset.

    Permite un análisis de detalle: en lugar del panorama general del heatmap,
    muestra la distribución de efectos para los componentes más relevantes.

    Args:
        crosstab: Tabla de contingencia (frecuencias absolutas) generada por
            `construir_crosstab`. Filas = componentes, columnas = efectos.
        top_n_efectos: Número de efectos a mostrar por componente.
        top_n_componentes: Número de componentes a analizar (los más frecuentes).

    Returns:
        DataFrame con columnas `componentes`, `efectos_secundarios`, `frecuencia`.

    Raises:
        ValueError: Si crosstab está vacía.
    """
    if crosstab.empty:
        raise ValueError("crosstab está vacía.")

    # Seleccionar los componentes con mayor suma total de efectos
    top_comp = crosstab.sum(axis=1).sort_values(ascending=False).head(top_n_componentes).index
    submatriz = crosstab.loc[top_comp]

    filas: list[dict] = []
    for componente, fila in submatriz.iterrows():
        top_efectos = fila.sort_values(ascending=False).head(top_n_efectos)
        for efecto, valor in top_efectos.items():
            if valor > 0:
                filas.append({
                    "componentes": componente,
                    "efectos_secundarios": efecto,
                    "frecuencia": int(valor),
                })
    ranking_detalle = pd.DataFrame(filas)

    if ranking_detalle.empty:
        print("[plot_top_efectos_por_componente] Sin datos para graficar.")
        return ranking_detalle

    fig, ax = plt.subplots(figsize=(12, 7))
    colores_comp = plt.cm.Set2(np.linspace(0, 1, top_n_componentes))
    colores_map = {comp: colores_comp[i] for i, comp in enumerate(top_comp)}

    for componente in top_comp:
        datos = ranking_detalle[ranking_detalle["componentes"] == componente]
        ax.scatter(
            datos["efectos_secundarios"],
            datos["frecuencia"],
            label=componente,
            color=colores_map[componente],
            s=80,
            alpha=0.85,
        )

    ax.set_xlabel("Efecto secundario")
    ax.set_ylabel("Frecuencia absoluta")
    ax.set_title(
        f"Top {top_n_efectos} efectos por componente "
        f"(Top {top_n_componentes} componentes más frecuentes)",
        fontweight="bold",
    )
    plt.xticks(rotation=45, ha="right")
    ax.legend(loc="upper right", fontsize=8)

    _guardar_figura(fig, "e03_top_efectos_por_componente_detalle")
    _guardar_tabla(ranking_detalle, "e03_top_efectos_por_componente_detalle")

    return ranking_detalle


# ---------------------------------------------------------------------------
# Gráfico 6: Distribución de n_efectos (histograma)
# ---------------------------------------------------------------------------

def plot_histograma_n_efectos(df_clean: pd.DataFrame) -> None:
    """
    Genera un histograma de la distribución de medicamentos según su número
    de efectos secundarios.

    Permite visualizar qué tan variable es la carga de efectos secundarios
    en el dataset. Responde: ¿cuántos efectos secundarios tiene típicamente
    un medicamento?

    Args:
        df_clean: DataFrame limpio con la columna `n_efectos`.

    Raises:
        KeyError: Si `n_efectos` no existe en df_clean.
    """
    if "n_efectos" not in df_clean.columns:
        raise KeyError("Columna 'n_efectos' no encontrada en df_clean.")

    conteos = df_clean["n_efectos"].value_counts().sort_index()

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(
        conteos.index,
        conteos.values,
        color="#1E88E5",
        edgecolor="white",
        width=0.7,
    )

    # Etiqueta de valor sobre las barras más visibles
    for x, y in zip(conteos.index, conteos.values):
        if y > conteos.values.max() * 0.02:
            ax.text(x, y + 5, str(y), ha="center", va="bottom", fontsize=8)

    ax.set_xlabel("Número de efectos secundarios")
    ax.set_ylabel("Número de medicamentos")
    ax.set_title(
        "Distribución de medicamentos según número de efectos secundarios",
        fontweight="bold",
    )

    _guardar_figura(fig, "e03_histograma_n_efectos")


# ---------------------------------------------------------------------------
# Pipeline orquestador
# ---------------------------------------------------------------------------

def run_analysis_pipeline(
    df_clean: pd.DataFrame,
    df_long: pd.DataFrame,
    crosstab: pd.DataFrame,
    crosstab_norm: pd.DataFrame,
) -> None:
    """
    Ejecuta el pipeline completo de análisis y genera todos los gráficos.

    Llama en orden a todas las funciones de visualización. Cada gráfico
    se guarda automáticamente en outputs/figures/ y las tablas de ranking
    se exportan a outputs/tables/.

    Args:
        df_clean: DataFrame limpio (salida de run_cleaning_pipeline).
        df_long: DataFrame expandido componente × efecto (salida de explotar_todo).
        crosstab: Tabla de contingencia (salida de construir_crosstab).
        crosstab_norm: Tabla normalizada (salida de normalizar_crosstab).

    Raises:
        ValueError: Si alguno de los DataFrames de entrada está vacío.
    """
    for nombre, df in [
        ("df_clean", df_clean),
        ("df_long", df_long),
        ("crosstab", crosstab),
        ("crosstab_norm", crosstab_norm),
    ]:
        if df.empty:
            raise ValueError(f"El DataFrame '{nombre}' está vacío.")

    print("=" * 55)
    print("INICIO DEL PIPELINE DE ANÁLISIS  [Enfoque 3]")
    print("=" * 55)

    print("\n[1/6] Generando top efectos secundarios globales...")
    plot_top_efectos(df_clean, top_n=15)

    print("\n[2/6] Generando componentes por diversidad de efectos...")
    plot_componentes_por_diversidad_efectos(df_long, top_n=20)

    print("\n[3/6] Generando heatmap componente × efecto (normalizado)...")
    plot_heatmap_componente_efecto(crosstab_norm)

    print("\n[4/6] Generando boxplot de efectos por número de componentes...")
    plot_efectos_por_n_componentes(df_clean)

    print("\n[5/6] Generando detalle de top efectos por componente...")
    plot_top_efectos_por_componente(crosstab)

    print("\n[6/6] Generando histograma de distribución de n_efectos...")
    plot_histograma_n_efectos(df_clean)

    print("\n" + "=" * 55)
    print("ANÁLISIS COMPLETO  [Enfoque 3]")
    print(f"Figuras guardadas en : {FIGURES_DIR}")
    print(f"Tablas guardadas en  : {RUTA_TABLAS}")
    print("=" * 55)