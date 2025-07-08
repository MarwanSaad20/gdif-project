import os
import logging
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from typing import Optional

from data_intelligence_system.utils.data_loader import load_data
from data_intelligence_system.utils.timer import Timer  # ⏱️ تكامل مع نظام التوقيت الجديد

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s — %(levelname)s — %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)

# تحديد جذر المشروع بناءً على المسار الثابت
BASE_DIR = Path(__file__).resolve().parents[2]
OUTPUT_DIR = BASE_DIR / "analysis" / "analysis_output"


def ensure_output_dir(path: Optional[Path] = OUTPUT_DIR) -> Path:
    """إنشاء مجلد الإخراج إذا لم يكن موجودًا"""
    Path(path).mkdir(parents=True, exist_ok=True)
    return path


def save_plot(fig: plt.Figure, filename: str, output_dir: Optional[Path] = OUTPUT_DIR):
    """حفظ الرسم البياني كصورة داخل مجلد التحليل"""
    ensure_output_dir(output_dir)
    filepath = output_dir / filename
    fig.savefig(filepath, bbox_inches='tight')
    plt.close(fig)
    logger.info(f"✅ تم حفظ الرسم البياني: {filepath}")


def plot_distribution(df: pd.DataFrame, column: str, output_name: str, output_dir: Optional[Path] = OUTPUT_DIR):
    """رسم توزيع متغير رقمي أو نوعي"""
    ensure_output_dir(output_dir)
    fig, ax = plt.subplots(figsize=(8, 5))

    if pd.api.types.is_numeric_dtype(df[column]):
        sns.histplot(df[column].dropna(), kde=True, ax=ax, color='steelblue')
    else:
        unique_vals = df[column].nunique()
        if unique_vals > 30:
            logger.warning(f"عمود '{column}' يحتوي على {unique_vals} فئة، الرسم قد يكون مزدحمًا.")
        sns.countplot(x=column, data=df, ax=ax, palette='viridis')
        ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha='right')

    ax.set_title(f"Distribution of {column}")
    save_plot(fig, output_name, output_dir)


def save_dataframe(df: pd.DataFrame, name: str, output_dir: Optional[Path] = OUTPUT_DIR, file_format: str = 'csv'):
    """حفظ داتا فريم بصيغة محددة"""
    ensure_output_dir(output_dir)
    file_format = file_format.lower()
    filepath = output_dir / f"{name}.{file_format}"

    if file_format == 'csv':
        df.to_csv(filepath, index=False)
    elif file_format in ['excel', 'xlsx']:
        df.to_excel(filepath, index=False)
    elif file_format == 'parquet':
        df.to_parquet(filepath, index=False)
    else:
        raise ValueError(f"صيغة غير مدعومة: {file_format}")

    logger.info(f"✅ تم حفظ البيانات: {filepath}")


def get_numerical_columns(df: pd.DataFrame) -> list:
    """إرجاع أسماء الأعمدة الرقمية مع استثناء الأعمدة الزمنية"""
    numerical_cols = df.select_dtypes(include=['number']).columns.tolist()
    datetime_cols = df.select_dtypes(include=['datetime64']).columns.tolist()
    return [col for col in numerical_cols if col not in datetime_cols]


def get_categorical_columns(df: pd.DataFrame) -> list:
    """إرجاع أسماء الأعمدة النوعية (categorical)"""
    return df.select_dtypes(include=['object', 'category', 'bool']).columns.tolist()


def log_basic_info(df: pd.DataFrame, name: str = "DataFrame"):
    """عرض معلومات أساسية عن البيانات مع تحذير للقيم المفقودة الكبيرة"""
    logger.info(f"📊 {name}: الشكل = {df.shape}")
    logger.info(f"📈 أعمدة رقمية: {get_numerical_columns(df)}")
    logger.info(f"📋 أعمدة فئوية: {get_categorical_columns(df)}")
    missing = df.isnull().sum()
    logger.info(f"🧼 قيم مفقودة:\n{missing}")

    total_rows = df.shape[0]
    missing_ratio = missing / total_rows
    high_missing = missing_ratio[missing_ratio > 0.3]
    if not high_missing.empty:
        for col, ratio in high_missing.items():
            logger.warning(f"⚠️ عمود '{col}' يحتوي على نسبة عالية من القيم المفقودة: {ratio:.2%}")
