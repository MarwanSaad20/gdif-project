import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Optional, List, Tuple

from data_intelligence_system.utils.visualization.visuals_helpers import (
    _handle_save_or_show, _validate_columns
)

sns.set_theme(style="whitegrid", palette="muted", font_scale=1.1)
plt.rcParams["figure.figsize"] = (10, 6)

def plot_box(df: pd.DataFrame, column: str, by: Optional[str] = None,
             title: Optional[str] = None, save_path: Optional[str] = None) -> Tuple[plt.Figure, plt.Axes]:
    data = _validate_columns(df, [column] + ([by] if by else []))
    fig, ax = plt.subplots()
    sns.boxplot(data=data, x=by, y=column, ax=ax) if by else sns.boxplot(y=data[column], ax=ax)
    ax.set_title(title or f"Box Plot of {column}")
    fig.tight_layout()
    _handle_save_or_show(fig, save_path)
    return fig, ax

def plot_distribution(df: pd.DataFrame, column: str, kde: bool = True, bins: int = 30,
                      title: Optional[str] = None, save_path: Optional[str] = None) -> Tuple[plt.Figure, plt.Axes]:
    data = _validate_columns(df, [column])
    fig, ax = plt.subplots()
    sns.histplot(data[column], kde=kde, bins=bins, color='steelblue', ax=ax)
    ax.set_title(title or f"Distribution of {column}")
    fig.tight_layout()
    _handle_save_or_show(fig, save_path)
    return fig, ax

def plot_line(df: pd.DataFrame, x: str, y: str,
              title: Optional[str] = None, save_path: Optional[str] = None) -> Tuple[plt.Figure, plt.Axes]:
    data = _validate_columns(df, [x, y])
    fig, ax = plt.subplots()
    sns.lineplot(data=data, x=x, y=y, marker='o', ax=ax)
    ax.set_title(title or f"{y} over {x}")
    fig.tight_layout()
    _handle_save_or_show(fig, save_path)
    return fig, ax

def compare_distributions(df: pd.DataFrame, columns: List[str],
                          title: str = "Comparing Distributions",
                          save_path: Optional[str] = None) -> plt.Figure:
    data = _validate_columns(df, columns)
    fig, ax = plt.subplots()
    for col in columns:
        sns.kdeplot(data[col], label=col, fill=True, alpha=0.3, ax=ax)
    ax.set_title(title)
    ax.legend()
    fig.tight_layout()
    _handle_save_or_show(fig, save_path)
    return fig

def plot_comparison_distribution(df: pd.DataFrame, column: str, group_col: str,
                                 title: Optional[str] = None, save_path: Optional[str] = None) -> Tuple[plt.Figure, plt.Axes]:
    data = _validate_columns(df, [column, group_col])
    fig, ax = plt.subplots()
    sns.histplot(data=data, x=column, hue=group_col, kde=True,
                 element="step", stat="density", common_norm=False, ax=ax)
    ax.set_title(title or f"Distribution of {column} by {group_col}")
    fig.tight_layout()
    _handle_save_or_show(fig, save_path)
    return fig, ax


def plot_correlation_heatmap(df: pd.DataFrame, method: str = "pearson",
                             title: str = "Correlation Heatmap",
                             save_path: Optional[str] = None) -> Tuple[plt.Figure, plt.Axes]:
    if df.empty:
        raise ValueError("DataFrame is empty.")
    corr = df.corr(method=method)
    fig, ax = plt.subplots()
    sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm", linewidths=0.5, ax=ax)
    ax.set_title(title)
    fig.tight_layout()
    _handle_save_or_show(fig, save_path)
    return fig, ax