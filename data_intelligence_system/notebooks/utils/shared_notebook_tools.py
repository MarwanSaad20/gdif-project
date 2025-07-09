import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px  # حالياً غير مستخدم، يمكن تفعيله لاحقًا
from pathlib import Path

# === إعدادات ثابتة للرسم ===
sns.set_theme(style="darkgrid")
sns.set_context('notebook')
sns.set_palette('Set2')

DEFAULT_FIGSIZE = (12, 7)

# === إعداد المسارات من جذر المشروع ===
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data_intelligence_system" / "data" / "processed"
REPORTS_DIR = PROJECT_ROOT / "data_intelligence_system" / "reports" / "output"

# === دوال تحميل البيانات ===

def load_clean_data(filename='clean_data.csv', data_dir=DATA_DIR):
    """
    تحميل ملف البيانات النظيفة (CSV) من مجلد البيانات المعالجة.
    """
    path = data_dir / filename
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    df = pd.read_csv(path)
    return df

# === دوال رسم بياني جاهزة ===

def plot_boxplot(df, column, by=None, figsize=DEFAULT_FIGSIZE, title=None, save_path=None):
    fig, ax = plt.subplots(figsize=figsize)
    if by:
        sns.boxplot(data=df, x=by, y=column, ax=ax)
        ax.set_xlabel(by)
        ax.set_ylabel(column)
    else:
        sns.boxplot(data=df, y=column, ax=ax)
        ax.set_ylabel(column)
    if title:
        ax.set_title(title)
    if save_path:
        fig.savefig(save_path, bbox_inches='tight', dpi=300)
        print(f"Boxplot saved to: {save_path}")
    plt.show()
    return fig

def plot_distribution(df, column, bins=30, figsize=DEFAULT_FIGSIZE, title=None, save_path=None):
    fig, ax = plt.subplots(figsize=figsize)
    sns.histplot(df[column], bins=bins, kde=True, ax=ax)
    ax.set_xlabel(column)
    if title:
        ax.set_title(title)
    if save_path:
        fig.savefig(save_path, bbox_inches='tight', dpi=300)
        print(f"Distribution plot saved to: {save_path}")
    plt.show()
    return fig

def plot_scatter_matrix(df, columns=None, figsize=(15, 15), diag_kind='kde', title=None, save_path=None):
    if columns is None:
        columns = df.select_dtypes(include='number').columns.tolist()
    pair_grid = sns.pairplot(df[columns], diag_kind=diag_kind)
    pair_grid.fig.set_size_inches(figsize)
    if title:
        pair_grid.fig.suptitle(title, y=1.02)
    if save_path:
        pair_grid.fig.savefig(save_path, bbox_inches='tight', dpi=300)
        print(f"Scatter matrix saved to: {save_path}")
    plt.show()
    return pair_grid.fig

# === دوال مساعدة أخرى ===

def ensure_dir(path):
    path = Path(path)
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)

def save_figure(fig, filename, folder=REPORTS_DIR, dpi=300):
    ensure_dir(folder)
    full_path = folder / filename
    fig.savefig(full_path, dpi=dpi, bbox_inches='tight')
    print(f"Figure saved to: {full_path}")
