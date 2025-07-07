import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px  # حالياً غير مستخدم، يمكن حذفه أو تفعيل دوال باستخدامه مستقبلاً

# === إعدادات ثابتة للرسم ===

# ضبط ستايل seaborn بطريقة صحيحة
sns.set_theme(style="darkgrid")
sns.set_context('notebook')
sns.set_palette('Set2')

# حجم الرسومات الافتراضي
DEFAULT_FIGSIZE = (12, 7)

# مجلد البيانات الافتراضي (يمكن تعديله حسب هيكل مشروعك)
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data', 'processed')
REPORTS_DIR = os.path.join(BASE_DIR, 'reports', 'output')


# === دوال تحميل البيانات ===

def load_clean_data(filename='clean_data.csv', data_dir=DATA_DIR):
    """
    تحميل ملف البيانات النظيفة (CSV) من مجلد البيانات المعالجة.

    Args:
        filename (str): اسم ملف البيانات
        data_dir (str): مسار مجلد البيانات المعالجة

    Returns:
        pd.DataFrame: بيانات محملة
    """
    path = os.path.join(data_dir, filename)
    if not os.path.exists(path):
        raise FileNotFoundError(f"File not found: {path}")
    df = pd.read_csv(path)
    return df


# === دوال رسم بياني جاهزة ===

def plot_boxplot(df, column, by=None, figsize=DEFAULT_FIGSIZE, title=None, save_path=None):
    """
    رسم Boxplot لعمود معين، مع إمكانية تقسيمه حسب عمود آخر.

    Args:
        df (pd.DataFrame): بيانات الإدخال
        column (str): اسم العمود المراد رسمه
        by (str, optional): عمود التقسيم (categorical)
        figsize (tuple): حجم الشكل
        title (str, optional): عنوان الرسم
        save_path (str, optional): مسار لحفظ الصورة

    Returns:
        matplotlib.figure.Figure: كائن الشكل
    """
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
    """
    رسم توزيع بيانات عددية (Histogram + KDE).

    Args:
        df (pd.DataFrame): بيانات الإدخال
        column (str): اسم العمود المراد رسمه
        bins (int): عدد الحاويات
        figsize (tuple): حجم الشكل
        title (str, optional): عنوان الرسم
        save_path (str, optional): مسار لحفظ الصورة

    Returns:
        matplotlib.figure.Figure: كائن الشكل
    """
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
    """
    رسم مصفوفة التبعثر (pairplot) للمتغيرات العددية.

    Args:
        df (pd.DataFrame): بيانات الإدخال
        columns (list, optional): قائمة الأعمدة المراد رسمها، إذا None يتم اختيار العددية تلقائيًا
        figsize (tuple): حجم الشكل
        diag_kind (str): نوع الرسم في القطر ('kde' أو 'hist')
        title (str, optional): عنوان الرسم
        save_path (str, optional): مسار لحفظ الصورة

    Returns:
        matplotlib.figure.Figure: كائن الشكل
    """
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
    """
    التأكد من وجود مجلد، وإن لم يكن موجوداً يتم إنشاؤه.

    Args:
        path (str): مسار المجلد
    """
    if not os.path.exists(path):
        os.makedirs(path)


def save_figure(fig, filename, folder=REPORTS_DIR, dpi=300):
    """
    حفظ الشكل (figure) في ملف داخل مجلد معين.

    Args:
        fig (matplotlib.figure.Figure): كائن الشكل
        filename (str): اسم الملف مع الامتداد (مثلاً 'plot.png')
        folder (str): مسار المجلد الذي سيتم الحفظ فيه
        dpi (int): جودة الصورة
    """
    ensure_dir(folder)
    full_path = os.path.join(folder, filename)
    fig.savefig(full_path, dpi=dpi, bbox_inches='tight')
    print(f"Figure saved to: {full_path}")
