import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def top_side_effects(
    df: pd.DataFrame,
    *,
    top_n: int = 15,
) -> pd.Series:
    """Calcula los efectos secundarios más frecuentes en todo el dataset.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame limpio con columna efectos_secundarios (lista).
    top_n : int, default 15
        Cantidad de efectos a retornar.

    Returns
    -------
    pd.Series
        Frecuencias absolutas, ordenadas descendente.
    """
    try:
        return (
            df["efectos_secundarios"]
            .explode()
            .dropna()
            .value_counts()
            .head(top_n)
        )
    except Exception as exc:
        raise RuntimeError(f"[top_side_effects] Error: {exc}") from exc


def effects_count_stats(df: pd.DataFrame) -> pd.Series:
    """Estadísticas descriptivas de cantidad de efectos por medicamento.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame limpio con columna n_efectos.

    Returns
    -------
    pd.Series
        Estadísticas: count, mean, std, min, percentiles, max.
    """
    try:
        return df["n_efectos"].describe().round(2)
    except Exception as exc:
        raise RuntimeError(f"[effects_count_stats] Error: {exc}") from exc


def components_by_effect_count(
    df: pd.DataFrame,
    *,
    top_n: int = 20,
) -> pd.DataFrame:
    """Identifica los componentes con mayor cantidad de efectos distintos.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame expandido por explode_all().
    top_n : int, default 20
        Número de componentes a retornar.

    Returns
    -------
    pd.DataFrame
        Columnas: componentes, efectos_distintos.
    """
    try:
        return (
            df.groupby("componentes")["efectos_secundarios"]
            .nunique()
            .sort_values(ascending=False)
            .head(top_n)
            .reset_index()
            .rename(columns={"efectos_secundarios": "efectos_distintos"})
        )
    except Exception as exc:
        raise RuntimeError(f"[components_by_effect_count] Error: {exc}") from exc


def average_reviews_by_effect_count(df: pd.DataFrame) -> pd.DataFrame:
    """Promedio de reseñas agrupado por cantidad de efectos secundarios.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame limpio con n_efectos y columnas de reseñas.

    Returns
    -------
    pd.DataFrame
        Promedios de Excellent, Average y Poor Review % por grupo.
    """
    review_cols = ["Excellent Review %", "Average Review %", "Poor Review %"]
    try:
        temp = df.copy()
        for col in review_cols:
            temp[col] = pd.to_numeric(temp[col], errors="coerce")
        return temp.groupby("n_efectos")[review_cols].mean().round(2)
    except Exception as exc:
        raise RuntimeError(f"[average_reviews_by_effect_count] Error: {exc}") from exc


def normalize_crosstab(table: pd.DataFrame) -> pd.DataFrame:
    """Normaliza una tabla de frecuencias por filas (cada fila suma 1).

    Parameters
    ----------
    table : pd.DataFrame
        Tabla de frecuencias (crosstab).

    Returns
    -------
    pd.DataFrame
        Tabla normalizada en rango [0, 1] por fila.
    """
    row_sums = table.sum(axis=1).replace(0, np.nan)
    return table.div(row_sums, axis=0).fillna(0.0)


def plot_top_effects(
    df: pd.DataFrame,
    *,
    top_n: int = 15,
    save_path: str | None = None,
) -> plt.Figure:
    """Barplot horizontal con los efectos secundarios más comunes.

    Responde a: ¿Cuáles son los efectos secundarios más frecuentes?

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame limpio con columna efectos_secundarios.
    top_n : int, default 15
        Cantidad de efectos a mostrar.
    save_path : str | None
        Si se provee, guarda la figura en esa ruta.

    Returns
    -------
    plt.Figure
    """
    try:
        counts = top_side_effects(df, top_n=top_n)

        fig, ax = plt.subplots(figsize=(10, 7))
        colors = plt.cm.RdYlGn_r(np.linspace(0.2, 0.85, len(counts)))
        counts[::-1].plot(kind="barh", ax=ax, color=colors[::-1], edgecolor="white")

        ax.set_title(
            f"Top {top_n} Efectos Secundarios más Frecuentes",
            fontsize=14, fontweight="bold", pad=15,
        )
        ax.set_xlabel("Número de medicamentos", fontsize=11)
        ax.set_ylabel("Efecto secundario", fontsize=11)
        ax.tick_params(axis="y", labelsize=9)

        for bar in ax.patches:
            ax.text(
                bar.get_width() + 5,
                bar.get_y() + bar.get_height() / 2,
                f"{int(bar.get_width())}",
                va="center", fontsize=8,
            )

        plt.tight_layout()
        if save_path:
            fig.savefig(save_path, dpi=150, bbox_inches="tight")
        return fig
    except Exception as exc:
        raise RuntimeError(f"[plot_top_effects] Error: {exc}") from exc


def plot_poor_review_by_effects(
    df: pd.DataFrame,
    *,
    max_effects: int = 20,
    save_path: str | None = None,
) -> plt.Figure:
    """Boxplot de Poor Review % según cantidad de efectos secundarios.

    Responde a: ¿Más efectos secundarios implica peores reseñas?

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame limpio con n_efectos y Poor Review %.
    max_effects : int, default 20
        Filtra medicamentos con más de este número de efectos.
    save_path : str | None
        Si se provee, guarda la figura.

    Returns
    -------
    plt.Figure
    """
    try:
        temp = df.copy()
        temp["Poor Review %"] = pd.to_numeric(temp["Poor Review %"], errors="coerce")
        temp = temp[temp["n_efectos"] <= max_effects].dropna(subset=["Poor Review %"])

        groups = [
            temp[temp["n_efectos"] == n]["Poor Review %"].values
            for n in sorted(temp["n_efectos"].unique())
        ]
        labels = sorted(temp["n_efectos"].unique())

        fig, ax = plt.subplots(figsize=(12, 6))
        bp = ax.boxplot(groups, labels=labels, patch_artist=True)

        cmap = plt.cm.RdYlGn_r
        for i, patch in enumerate(bp["boxes"]):
            patch.set_facecolor(cmap(i / len(bp["boxes"])))
            patch.set_alpha(0.75)

        ax.set_title(
            "Distribución de Poor Review % según Cantidad de Efectos Secundarios",
            fontsize=13, fontweight="bold", pad=15,
        )
        ax.set_xlabel("Cantidad de efectos secundarios", fontsize=11)
        ax.set_ylabel("Poor Review %", fontsize=11)
        ax.grid(axis="y", linestyle="--", alpha=0.4)

        plt.tight_layout()
        if save_path:
            fig.savefig(save_path, dpi=150, bbox_inches="tight")
        return fig
    except Exception as exc:
        raise RuntimeError(f"[plot_poor_review_by_effects] Error: {exc}") from exc


def plot_cooccurrence_heatmap(
    df: pd.DataFrame,
    *,
    top_n_effects: int = 15,
    save_path: str | None = None,
) -> plt.Figure:
    """Heatmap de co-ocurrencia entre los efectos secundarios más comunes.

    Responde a: ¿Qué efectos suelen aparecer juntos en el mismo medicamento?

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame limpio con columna efectos_secundarios (lista).
    top_n_effects : int, default 15
        Efectos a incluir en el heatmap.
    save_path : str | None
        Si se provee, guarda la figura.

    Returns
    -------
    plt.Figure
    """
    try:
        top_effects = (
            df["efectos_secundarios"]
            .explode()
            .dropna()
            .value_counts()
            .head(top_n_effects)
            .index.tolist()
        )

        binary = pd.DataFrame(
            {
                effect: df["efectos_secundarios"].map(lambda lst, e=effect: int(e in lst))
                for effect in top_effects
            }
        )

        cooccurrence = binary.T @ binary
        np.fill_diagonal(cooccurrence.values, 0)

        fig, ax = plt.subplots(figsize=(12, 10))
        im = ax.imshow(cooccurrence.values, cmap="YlOrRd", aspect="auto")
        plt.colorbar(im, ax=ax, label="Co-ocurrencias")

        ax.set_xticks(range(len(top_effects)))
        ax.set_yticks(range(len(top_effects)))
        ax.set_xticklabels(top_effects, rotation=45, ha="right", fontsize=9)
        ax.set_yticklabels(top_effects, fontsize=9)
        ax.set_title(
            f"Co-ocurrencia de los Top {top_n_effects} Efectos Secundarios",
            fontsize=13, fontweight="bold", pad=15,
        )

        for i in range(len(top_effects)):
            for j in range(len(top_effects)):
                val = int(cooccurrence.iloc[i, j])
                if val > 0:
                    ax.text(
                        j, i, str(val),
                        ha="center", va="center", fontsize=7,
                        color="black" if val < cooccurrence.values.max() * 0.6 else "white",
                    )

        plt.tight_layout()
        if save_path:
            fig.savefig(save_path, dpi=150, bbox_inches="tight")
        return fig
    except Exception as exc:
        raise RuntimeError(f"[plot_cooccurrence_heatmap] Error: {exc}") from exc


def plot_scatter_effects_vs_poor_review(
    df: pd.DataFrame,
    *,
    save_path: str | None = None,
) -> plt.Figure:
    """Scatterplot de cantidad de efectos vs Poor Review %.

    Responde a: ¿Existe correlación entre efectos secundarios y malas reseñas?

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame limpio con n_efectos y Poor Review %.
    save_path : str | None
        Si se provee, guarda la figura.

    Returns
    -------
    plt.Figure
    """
    try:
        temp = df.copy()
        temp["Poor Review %"] = pd.to_numeric(temp["Poor Review %"], errors="coerce")
        temp = temp.dropna(subset=["Poor Review %", "n_efectos"])

        z = np.polyfit(temp["n_efectos"], temp["Poor Review %"], 1)
        p = np.poly1d(z)
        x_line = np.linspace(temp["n_efectos"].min(), temp["n_efectos"].max(), 100)
        corr = temp["n_efectos"].corr(temp["Poor Review %"])

        fig, ax = plt.subplots(figsize=(10, 6))
        ax.scatter(
            temp["n_efectos"], temp["Poor Review %"],
            alpha=0.3, s=20, color="steelblue", label="Medicamentos",
        )
        ax.plot(x_line, p(x_line), color="crimson", linewidth=2,
                label=f"Tendencia (r={corr:.3f})")

        ax.set_title(
            "Cantidad de Efectos Secundarios vs Poor Review %",
            fontsize=13, fontweight="bold", pad=15,
        )
        ax.set_xlabel("Número de efectos secundarios", fontsize=11)
        ax.set_ylabel("Poor Review %", fontsize=11)
        ax.legend()
        ax.grid(linestyle="--", alpha=0.3)

        plt.tight_layout()
        if save_path:
            fig.savefig(save_path, dpi=150, bbox_inches="tight")
        return fig
    except Exception as exc:
        raise RuntimeError(f"[plot_scatter_effects_vs_poor_review] Error: {exc}") from exc


def component_vs_effects(
    df: pd.DataFrame,
    *,
    min_component_observations: int | None = None,
) -> pd.DataFrame:
    """Tabla de frecuencia componente vs efecto secundario.

    Compatible con notebooks que esperan esta API.
    """
    base = df
    if min_component_observations is not None:
        counts = base["componentes"].value_counts()
        keep = counts[counts >= min_component_observations].index
        base = base[base["componentes"].isin(keep)]

    return pd.crosstab(base["componentes"], base["efectos_secundarios"])


def normalize(table: pd.DataFrame) -> pd.DataFrame:
    """Alias de normalización por filas en rango [0, 1]."""
    return normalize_crosstab(table)


def effects_by_manufacturer(df: pd.DataFrame) -> pd.DataFrame:
    """Frecuencia de efectos secundarios por fabricante limpio."""
    return pd.crosstab(df["manufacturer"], df["efectos_secundarios"])


def average_reviews_by_component(df: pd.DataFrame) -> pd.DataFrame:
    """Promedio de reviews por componente."""
    review_cols = ["Excellent Review %", "Average Review %", "Poor Review %"]
    temp = df.copy()
    for col in review_cols:
        temp[col] = pd.to_numeric(temp[col], errors="coerce")
    return temp.groupby("componentes", dropna=True)[review_cols].mean()


def top_effects_by_component(
    frequency_table: pd.DataFrame,
    *,
    top_n: int = 5,
) -> pd.DataFrame:
    """Top N efectos por componente a partir de una tabla de frecuencia."""
    top_rows: list[dict[str, object]] = []
    for component, row in frequency_table.iterrows():
        top_effects = row.sort_values(ascending=False).head(top_n)
        for effect, value in top_effects.items():
            if value > 0:
                top_rows.append(
                    {
                        "componentes": component,
                        "efectos_secundarios": effect,
                        "frecuencia": int(value),
                    }
                )
    return pd.DataFrame(top_rows)