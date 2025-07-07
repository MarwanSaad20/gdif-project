import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO
from typing import Optional, Union
from matplotlib.figure import Figure  # استيراد الشكل بشكل صريح

def ensure_dir(path: str):
    """تأكد من وجود مجلد، وإذا لم يكن موجوداً يتم إنشاؤه."""
    if not os.path.exists(path):
        os.makedirs(path)

def save_dataframe_to_csv(df: pd.DataFrame, filename: str, output_dir: str):
    """
    حفظ DataFrame إلى ملف CSV بعد التأكد من وجود مجلد الحفظ.
    """
    ensure_dir(output_dir)
    full_path = os.path.join(output_dir, f"{filename}.csv")
    df.to_csv(full_path, index=False, encoding='utf-8-sig')

def save_dataframe_to_excel(df: pd.DataFrame, filename: str, output_dir: str, sheet_name: str = "Sheet1"):
    """
    حفظ DataFrame إلى ملف Excel مع ضبط عرض الأعمدة تلقائيًا.
    """
    ensure_dir(output_dir)
    full_path = os.path.join(output_dir, f"{filename}.xlsx")
    with pd.ExcelWriter(full_path, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name=sheet_name, index=False)
        worksheet = writer.sheets[sheet_name]
        for idx, col in enumerate(df.columns):
            max_len = max(df[col].astype(str).map(len).max(), len(str(col))) + 2
            worksheet.set_column(idx, idx, max_len)

def save_plot(fig_or_plt: Union[Figure, plt], filename: str, output_dir: str, dpi: int = 300):
    """
    حفظ رسم matplotlib إلى صورة PNG.
    يدعم كلا من Figure أو plt مباشرة.
    """
    ensure_dir(output_dir)
    if not filename.endswith('.png'):
        filename += '.png'
    full_path = os.path.join(output_dir, filename)
    if isinstance(fig_or_plt, Figure):
        fig_or_plt.savefig(full_path, dpi=dpi, bbox_inches='tight')
        plt.close(fig_or_plt)
    else:
        fig_or_plt.savefig(full_path, dpi=dpi, bbox_inches='tight')
        plt.close()

def df_to_html_table(df: pd.DataFrame, classes: Optional[str] = None, index: bool = False) -> str:
    """
    تحويل DataFrame إلى جدول HTML منسق، مع دعم CSS.
    """
    return df.to_html(classes=classes, index=index, border=0, justify='center')

def plot_correlation_heatmap(df_corr: pd.DataFrame, filename: str, output_dir: str,
                             cmap: str = "coolwarm", annot: bool = True):
    """
    رسم خريطة حرارة لمصفوفة الارتباط، وحفظها كصورة.
    """
    ensure_dir(output_dir)
    fig, ax = plt.subplots(figsize=(12, 10))
    sns.heatmap(df_corr, annot=annot, fmt=".2f", cmap=cmap, square=True, cbar_kws={"shrink": 0.8}, ax=ax)
    ax.set_title("Correlation Heatmap")
    fig.tight_layout()
    save_plot(fig, filename, output_dir)

def save_image_bytes(fig: Figure, dpi: int = 300) -> bytes:
    """
    تحويل شكل matplotlib إلى Bytes (مثالي لـ HTML أو إرسال الشبكة).
    """
    buf = BytesIO()
    fig.savefig(buf, format='png', dpi=dpi, bbox_inches='tight')
    plt.close(fig)
    buf.seek(0)
    return buf.getvalue()
