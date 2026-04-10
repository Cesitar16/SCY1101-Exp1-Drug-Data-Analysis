from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from .transform import build_manufacturer_composition_frame, explode_side_effects, explode_therapeutic_areas


def market_share_proxy(
    df: pd.DataFrame,
    *,
    top_n: int = 15,
) -> pd.DataFrame:
    """Approximate market presence by medicines per manufacturer."""
    counts = (
        df["manufacturer_clean"]
        .dropna()
        .value_counts()
        .rename_axis("manufacturer_clean")
        .reset_index(name="n_medicines")
    )
    counts["share_pct"] = (counts["n_medicines"] / counts["n_medicines"].sum() * 100).round(2)
    return counts.head(top_n)


def manufacturer_reputation_ranking(
    df: pd.DataFrame,
    *,
    min_medicines: int = 5,
) -> pd.DataFrame:
    """Ranking by mean review balance and review mix."""
    summary = (
        df.dropna(subset=["manufacturer_clean"])
        .groupby("manufacturer_clean", as_index=False)
        .agg(
            n_medicines=("Medicine Name", "count"),
            excellent_mean=("Excellent Review %", "mean"),
            average_mean=("Average Review %", "mean"),
            poor_mean=("Poor Review %", "mean"),
            review_balance_mean=("review_balance", "mean"),
        )
    )
    summary = summary[summary["n_medicines"] >= min_medicines].copy()
    summary["excellent_mean"] = summary["excellent_mean"].round(2)
    summary["average_mean"] = summary["average_mean"].round(2)
    summary["poor_mean"] = summary["poor_mean"].round(2)
    summary["review_balance_mean"] = summary["review_balance_mean"].round(2)
    return summary.sort_values(
        ["review_balance_mean", "excellent_mean", "n_medicines"],
        ascending=[False, False, False],
    ).reset_index(drop=True)


def manufacturer_consistency(
    df: pd.DataFrame,
    *,
    min_medicines: int = 5,
) -> pd.DataFrame:
    """Describe internal variation of reviews within each manufacturer."""
    grouped = (
        df.dropna(subset=["manufacturer_clean"])
        .groupby("manufacturer_clean")
        .agg(
            n_medicines=("Medicine Name", "count"),
            review_balance_mean=("review_balance", "mean"),
            review_balance_std=("review_balance", "std"),
            excellent_iqr=("Excellent Review %", lambda s: s.quantile(0.75) - s.quantile(0.25)),
            poor_iqr=("Poor Review %", lambda s: s.quantile(0.75) - s.quantile(0.25)),
        )
        .reset_index()
    )
    grouped = grouped[grouped["n_medicines"] >= min_medicines].copy()
    grouped["review_balance_std"] = grouped["review_balance_std"].fillna(0).round(2)
    grouped["review_balance_mean"] = grouped["review_balance_mean"].round(2)
    grouped["excellent_iqr"] = grouped["excellent_iqr"].round(2)
    grouped["poor_iqr"] = grouped["poor_iqr"].round(2)
    return grouped.sort_values(
        ["review_balance_std", "review_balance_mean"],
        ascending=[True, False],
    ).reset_index(drop=True)


def composition_company_comparison(
    df: pd.DataFrame,
    *,
    min_manufacturers: int = 2,
) -> pd.DataFrame:
    """Compare the same ingredient combination across manufacturers."""
    pairs = build_manufacturer_composition_frame(df, min_manufacturers=min_manufacturers)
    numeric_columns = [
        "excellent_mean",
        "average_mean",
        "poor_mean",
        "review_balance_mean",
    ]
    for column in numeric_columns:
        pairs[column] = pairs[column].round(2)
    return pairs.sort_values(
        ["n_manufacturers", "review_balance_mean", "n_medicines"],
        ascending=[False, False, False],
    ).reset_index(drop=True)


def composition_winners(
    df: pd.DataFrame,
    *,
    min_manufacturers: int = 2,
) -> pd.DataFrame:
    """Return the best-ranked manufacturer for each comparable composition."""
    pairs = composition_company_comparison(df, min_manufacturers=min_manufacturers)
    winners = (
        pairs.sort_values(
            ["composition_key", "review_balance_mean", "excellent_mean", "n_medicines"],
            ascending=[True, False, False, False],
        )
        .groupby("composition_key", as_index=False)
        .head(1)
        .reset_index(drop=True)
    )
    return winners.sort_values(
        ["n_manufacturers", "review_balance_mean"],
        ascending=[False, False],
    ).reset_index(drop=True)


def manufacturer_side_effect_summary(
    df: pd.DataFrame,
    *,
    min_medicines: int = 5,
) -> pd.DataFrame:
    """Summarize safety signals by manufacturer."""
    exploded = explode_side_effects(df)
    distinct_effects = (
        exploded.groupby("manufacturer_clean")["side_effect"]
        .nunique()
        .rename("distinct_side_effects")
    )
    summary = (
        df.dropna(subset=["manufacturer_clean"])
        .groupby("manufacturer_clean", as_index=False)
        .agg(
            n_medicines=("Medicine Name", "count"),
            avg_side_effects=("n_side_effects", "mean"),
            median_side_effects=("n_side_effects", "median"),
            poor_mean=("Poor Review %", "mean"),
            review_balance_mean=("review_balance", "mean"),
        )
    )
    summary = summary.merge(
        distinct_effects,
        on="manufacturer_clean",
        how="left",
    )
    summary = summary[summary["n_medicines"] >= min_medicines].copy()
    for column in ["avg_side_effects", "median_side_effects", "poor_mean", "review_balance_mean"]:
        summary[column] = summary[column].round(2)
    summary["distinct_side_effects"] = summary["distinct_side_effects"].fillna(0).astype(int)
    return summary.sort_values(
        ["avg_side_effects", "poor_mean", "n_medicines"],
        ascending=[False, False, False],
    ).reset_index(drop=True)


def manufacturer_specialization(
    df: pd.DataFrame,
    *,
    min_medicines: int = 5,
) -> pd.DataFrame:
    """Therapeutic-area mix by manufacturer."""
    exploded = explode_therapeutic_areas(df)
    counts = (
        exploded.groupby(["manufacturer_clean", "therapeutic_area"], as_index=False)
        .agg(n_medicines=("Medicine Name", "count"))
    )
    totals = counts.groupby("manufacturer_clean")["n_medicines"].sum().rename("total_medicines")
    counts = counts.merge(totals, on="manufacturer_clean", how="left")
    counts = counts[counts["total_medicines"] >= min_medicines].copy()
    counts["share_within_company_pct"] = (
        counts["n_medicines"] / counts["total_medicines"] * 100
    ).round(2)
    return counts.sort_values(
        ["manufacturer_clean", "share_within_company_pct", "n_medicines"],
        ascending=[True, False, False],
    ).reset_index(drop=True)


def quality_quantity_balance(
    df: pd.DataFrame,
    *,
    min_medicines: int = 5,
) -> pd.DataFrame:
    """Compare manufacturer scale against review quality."""
    ranking = manufacturer_reputation_ranking(df, min_medicines=min_medicines)
    ranking["segment"] = np.where(
        ranking["review_balance_mean"] >= ranking["review_balance_mean"].median(),
        "high_quality",
        "mid_or_low_quality",
    )
    ranking["scale"] = np.where(
        ranking["n_medicines"] >= ranking["n_medicines"].median(),
        "large",
        "small",
    )
    return ranking


def top_medicines_by_manufacturer(
    df: pd.DataFrame,
    *,
    min_company_size: int = 5,
    top_n: int = 3,
) -> pd.DataFrame:
    """Best-rated medicines inside each eligible manufacturer."""
    eligible = (
        df["manufacturer_clean"]
        .value_counts()
        .loc[lambda s: s >= min_company_size]
        .index
    )
    temp = df[df["manufacturer_clean"].isin(eligible)].copy()
    temp = temp.sort_values(
        ["manufacturer_clean", "review_balance", "Excellent Review %", "Poor Review %"],
        ascending=[True, False, False, True],
    )
    top = (
        temp.groupby("manufacturer_clean", as_index=False)
        .head(top_n)
        .loc[:, ["manufacturer_clean", "Medicine Name", "composition_key", "Excellent Review %", "Poor Review %", "review_balance"]]
        .reset_index(drop=True)
    )
    top["review_balance"] = top["review_balance"].round(2)
    return top


def _save_if_requested(fig: plt.Figure, save_path: str | Path | None) -> None:
    if save_path is None:
        return
    destination = Path(save_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(destination, dpi=150, bbox_inches="tight")


def plot_top_manufacturers(
    df: pd.DataFrame,
    *,
    top_n: int = 15,
    save_path: str | Path | None = None,
) -> plt.Figure:
    """Horizontal bar chart for manufacturer size in the dataset."""
    table = market_share_proxy(df, top_n=top_n)
    fig, ax = plt.subplots(figsize=(10, 7))
    ax.barh(
        table["manufacturer_clean"][::-1],
        table["n_medicines"][::-1],
        color="#4C78A8",
    )
    ax.set_title(f"Top {top_n} manufacturers by medicines in dataset", fontsize=13, fontweight="bold")
    ax.set_xlabel("Number of medicines")
    ax.set_ylabel("Manufacturer")
    ax.grid(axis="x", linestyle="--", alpha=0.3)
    plt.tight_layout()
    _save_if_requested(fig, save_path)
    return fig


def plot_reputation_ranking(
    df: pd.DataFrame,
    *,
    top_n: int = 15,
    min_medicines: int = 5,
    save_path: str | Path | None = None,
) -> plt.Figure:
    """Bar chart of review balance for the best-rated manufacturers."""
    table = manufacturer_reputation_ranking(df, min_medicines=min_medicines).head(top_n)
    fig, ax = plt.subplots(figsize=(10, 7))
    ax.barh(
        table["manufacturer_clean"][::-1],
        table["review_balance_mean"][::-1],
        color="#59A14F",
    )
    ax.set_title("Manufacturer reputation ranking", fontsize=13, fontweight="bold")
    ax.set_xlabel("Mean review balance (Excellent - Poor)")
    ax.set_ylabel("Manufacturer")
    ax.grid(axis="x", linestyle="--", alpha=0.3)
    plt.tight_layout()
    _save_if_requested(fig, save_path)
    return fig


def plot_review_balance_boxplot(
    df: pd.DataFrame,
    *,
    top_n: int = 12,
    save_path: str | Path | None = None,
) -> plt.Figure:
    """Boxplot for internal review-balance variation among large manufacturers."""
    top_manufacturers = (
        df["manufacturer_clean"]
        .value_counts()
        .head(top_n)
        .index
    )
    temp = df[df["manufacturer_clean"].isin(top_manufacturers)].copy()
    order = temp["manufacturer_clean"].value_counts().index.tolist()
    groups = [temp.loc[temp["manufacturer_clean"] == name, "review_balance"].dropna().values for name in order]

    fig, ax = plt.subplots(figsize=(12, 6))
    bp = ax.boxplot(groups, labels=order, patch_artist=True)
    colors = plt.cm.Blues(np.linspace(0.45, 0.85, len(groups)))
    for patch, color in zip(bp["boxes"], colors):
        patch.set_facecolor(color)
    ax.set_title("Review balance distribution for top manufacturers", fontsize=13, fontweight="bold")
    ax.set_ylabel("Review balance")
    ax.tick_params(axis="x", rotation=45, labelsize=9)
    ax.grid(axis="y", linestyle="--", alpha=0.3)
    plt.tight_layout()
    _save_if_requested(fig, save_path)
    return fig


def plot_quality_vs_quantity(
    df: pd.DataFrame,
    *,
    min_medicines: int = 5,
    save_path: str | Path | None = None,
) -> plt.Figure:
    """Scatter plot of scale versus average quality."""
    table = quality_quantity_balance(df, min_medicines=min_medicines)
    fig, ax = plt.subplots(figsize=(10, 6))
    scatter = ax.scatter(
        table["n_medicines"],
        table["review_balance_mean"],
        s=np.clip(table["excellent_mean"] * 6, 40, 220),
        c=table["poor_mean"],
        cmap="RdYlGn_r",
        alpha=0.75,
        edgecolors="white",
    )
    colorbar = plt.colorbar(scatter, ax=ax)
    colorbar.set_label("Mean Poor Review %")
    ax.set_title("Quality vs quantity by manufacturer", fontsize=13, fontweight="bold")
    ax.set_xlabel("Number of medicines in dataset")
    ax.set_ylabel("Mean review balance")
    ax.grid(linestyle="--", alpha=0.3)
    plt.tight_layout()
    _save_if_requested(fig, save_path)
    return fig


def plot_correlation_size_vs_good_reviews(
    df: pd.DataFrame,
    *,
    min_medicines: int = 5,
    save_path: str | Path | None = None,
) -> plt.Figure:
    """Scatter plot of medicines-per-manufacturer vs mean excellent reviews."""
    table = manufacturer_reputation_ranking(df, min_medicines=min_medicines)
    corr = table["n_medicines"].corr(table["excellent_mean"])

    fig, ax = plt.subplots(figsize=(10, 6))
    scatter = ax.scatter(
        table["n_medicines"],
        table["excellent_mean"],
        s=np.clip(table["review_balance_mean"] * 4, 40, 220),
        c=table["review_balance_mean"],
        cmap="YlGnBu",
        alpha=0.8,
        edgecolors="white",
    )

    if len(table) >= 2:
        z = np.polyfit(table["n_medicines"], table["excellent_mean"], 1)
        p = np.poly1d(z)
        x_line = np.linspace(table["n_medicines"].min(), table["n_medicines"].max(), 100)
        ax.plot(x_line, p(x_line), color="#E15759", linewidth=2, label=f"Tendencia (r = {corr:.3f})")
        ax.legend()

    colorbar = plt.colorbar(scatter, ax=ax)
    colorbar.set_label("Mean review balance")
    ax.text(
        0.02,
        0.98,
        f"Pearson r = {corr:.3f}\nEmpresas = {len(table)}",
        transform=ax.transAxes,
        va="top",
        bbox={"boxstyle": "round", "facecolor": "white", "alpha": 0.9},
    )
    ax.set_title("Correlation: company size vs good reviews", fontsize=13, fontweight="bold")
    ax.set_xlabel("Number of medicines in dataset")
    ax.set_ylabel("Mean Excellent Review %")
    ax.grid(linestyle="--", alpha=0.3)
    plt.tight_layout()
    _save_if_requested(fig, save_path)
    return fig


def plot_specialization_heatmap(
    df: pd.DataFrame,
    *,
    top_n_manufacturers: int = 10,
    save_path: str | Path | None = None,
) -> plt.Figure:
    """Heatmap of therapeutic-area concentration for the largest manufacturers."""
    counts = manufacturer_specialization(df, min_medicines=1)
    largest = (
        df["manufacturer_clean"]
        .value_counts()
        .head(top_n_manufacturers)
        .index
    )
    pivot = (
        counts[counts["manufacturer_clean"].isin(largest)]
        .pivot(index="manufacturer_clean", columns="therapeutic_area", values="share_within_company_pct")
        .fillna(0.0)
    )
    pivot = pivot.reindex(largest).dropna(how="all")
    fig, ax = plt.subplots(figsize=(12, 6))
    image = ax.imshow(pivot.values, cmap="YlGnBu", aspect="auto")
    plt.colorbar(image, ax=ax, label="Share within manufacturer (%)")
    ax.set_xticks(range(len(pivot.columns)))
    ax.set_xticklabels(pivot.columns, rotation=45, ha="right")
    ax.set_yticks(range(len(pivot.index)))
    ax.set_yticklabels(pivot.index)
    ax.set_title("Therapeutic specialization by manufacturer", fontsize=13, fontweight="bold")
    plt.tight_layout()
    _save_if_requested(fig, save_path)
    return fig
