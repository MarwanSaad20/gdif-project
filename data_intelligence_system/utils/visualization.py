import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
from typing import Optional, List, Tuple, Union

# ✅ استيراد اللوجر من المسار الجذري الجديد
from data_intelligence_system.utils.logger import get_logger

# إعدادات عامة للمظهر
sns.set_theme(style="whitegrid", palette="muted", font_scale=1.1)
plt.rcParams["figure.figsize"] = (10, 6)

# تهيئة اللوجر
logger = get_logger("Visualization")


def _handle_save_or_show(fig: plt.Figure, save_path: Optional[str]) -> None:
    """
    دالة مساعدة لحفظ الشكل إلى ملف أو عرضه.
    """
    try:
        if save_path:
            fig.savefig(save_path)
            plt.close(fig)
        else:
            plt.show()
    except Exception as e:
        logger.exception(f"❌ خطأ أثناء حفظ أو عرض الشكل: {e}")
        plt.close(fig)
        raise RuntimeError(f"خطأ أثناء حفظ أو عرض الشكل: {e}")


def _validate_columns(df: pd.DataFrame, columns: List[str]) -> None:
    """
    التحقق من وجود الأعمدة المطلوبة في DataFrame.
    """
    missing = [col for col in columns if col not in df.columns]
    if missing:
        raise ValueError(f"الأعمدة التالية غير موجودة في البيانات: {missing}")
    if df.empty:
        raise ValueError("DataFrame فارغ، لا يمكن إنشاء الرسم.")


def plot_box(df: pd.DataFrame, column: str, by: Optional[str] = None,
             title: Optional[str] = None, save_path: Optional[str] = None) -> Tuple[plt.Figure, plt.Axes]:
    _validate_columns(df, [column] + ([by] if by else []))
    data = df[[column, by]].dropna() if by else df[[column]].dropna()
    fig, ax = plt.subplots()
    if by:
        sns.boxplot(x=by, y=column, data=data, ax=ax)
    else:
        sns.boxplot(y=data[column], ax=ax)
    ax.set_title(title or f"Box Plot of {column}")
    fig.tight_layout()
    _handle_save_or_show(fig, save_path)
    return fig, ax


def plot_distribution(df: pd.DataFrame, column: str, kde: bool = True, bins: int = 30,
                      title: Optional[str] = None, save_path: Optional[str] = None) -> Tuple[plt.Figure, plt.Axes]:
    _validate_columns(df, [column])
    data = df[column].dropna()
    fig, ax = plt.subplots()
    sns.histplot(data, kde=kde, bins=bins, color='steelblue', ax=ax)
    ax.set_title(title or f"Distribution of {column}")
    ax.set_xlabel(column)
    ax.set_ylabel("Frequency")
    fig.tight_layout()
    _handle_save_or_show(fig, save_path)
    return fig, ax


def plot_line(df: pd.DataFrame, x: str, y: str,
              title: Optional[str] = None, save_path: Optional[str] = None) -> Tuple[plt.Figure, plt.Axes]:
    _validate_columns(df, [x, y])
    data = df[[x, y]].dropna()
    fig, ax = plt.subplots()
    sns.lineplot(data=data, x=x, y=y, marker='o', ax=ax)
    ax.set_title(title or f"{y} over {x}")
    ax.set_xlabel(x)
    ax.set_ylabel(y)
    fig.tight_layout()
    _handle_save_or_show(fig, save_path)
    return fig, ax


def compare_distributions(df: pd.DataFrame, columns: List[str],
                          title: str = "Comparing Distributions",
                          save_path: Optional[str] = None) -> plt.Figure:
    _validate_columns(df, columns)
    fig, ax = plt.subplots()
    for col in columns:
        sns.kdeplot(df[col].dropna(), label=col, fill=True, alpha=0.3, ax=ax)
    ax.set_title(title)
    ax.legend()
    fig.tight_layout()
    _handle_save_or_show(fig, save_path)
    return fig


def plot_comparison_distribution(df: pd.DataFrame, column: str, group_col: str,
                                 title: Optional[str] = None,
                                 save_path: Optional[str] = None) -> Tuple[plt.Figure, plt.Axes]:
    _validate_columns(df, [column, group_col])
    data = df[[column, group_col]].dropna()
    fig, ax = plt.subplots()
    sns.histplot(data=data, x=column, hue=group_col, kde=True,
                 element="step", stat="density", common_norm=False, ax=ax)
    ax.set_title(title or f"Distribution of {column} by {group_col}")
    ax.set_xlabel(column)
    ax.set_ylabel("Density")
    fig.tight_layout()
    _handle_save_or_show(fig, save_path)
    return fig, ax


def interactive_scatter_matrix(df: pd.DataFrame, dimensions: List[str],
                               color: Optional[str] = None,
                               title: str = "Scatter Matrix",
                               save_path: Optional[str] = None) -> Union[px.scatter_matrix, None]:
    _validate_columns(df, dimensions)
    if color and color not in df.columns:
        raise ValueError(f"Color column '{color}' not found in DataFrame.")

    fig = px.scatter_matrix(df, dimensions=dimensions, color=color, title=title)
    fig.update_traces(diagonal_visible=False)

    if save_path:
        if not save_path.endswith('.html'):
            raise ValueError("للحفظ يجب أن يكون الامتداد .html لرسومات Plotly.")
        try:
            fig.write_html(save_path)
        except Exception as e:
            logger.exception(f"❌ خطأ أثناء حفظ ملف HTML: {e}")
            raise RuntimeError(f"خطأ أثناء حفظ ملف HTML: {e}")
        return None
    else:
        fig.show()
        return fig


def plot_correlation_heatmap(df: pd.DataFrame, method: str = "pearson",
                             title: str = "Correlation Heatmap",
                             save_path: Optional[str] = None) -> Tuple[plt.Figure, plt.Axes]:
    if df.empty:
        raise ValueError("DataFrame فارغ، لا يمكن إنشاء خريطة الحرارة.")
    corr = df.corr(method=method)
    fig, ax = plt.subplots()
    sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm", linewidths=0.5, ax=ax)
    ax.set_title(title)
    fig.tight_layout()
    _handle_save_or_show(fig, save_path)
    return fig, ax
