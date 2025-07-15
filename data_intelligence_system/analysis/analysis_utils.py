import matplotlib
matplotlib.use('Agg')  # استخدام واجهة غير تفاعلية لـ Matplotlib

import logging
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from typing import Optional

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s — %(levelname)s — %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parents[2]
OUTPUT_DIR = BASE_DIR / "analysis" / "analysis_output"


def ensure_output_dir(path: Optional[Path] = OUTPUT_DIR) -> Path:
    Path(path).mkdir(parents=True, exist_ok=True)
    return path


def save_plot(fig: plt.Figure, filename: str, output_dir: Optional[Path] = OUTPUT_DIR, dpi: int = 300):
    ensure_output_dir(output_dir)
    filepath = output_dir / filename
    try:
        fig.savefig(filepath, bbox_inches='tight', dpi=dpi)
        logger.info(f"✅ تم حفظ الرسم البياني: {filepath}")
    except Exception as e:
        logger.error(f"❌ فشل حفظ الرسم البياني {filename}: {e}")
    finally:
        plt.close(fig)


def plot_distribution(df: pd.DataFrame, column: str, output_name: str,
                      output_dir: Optional[Path] = OUTPUT_DIR, palette: str = 'viridis', figsize: tuple = (8, 5)):
    ensure_output_dir(output_dir)

    if column not in df.columns:
        logger.error(f"❌ العمود '{column}' غير موجود في البيانات.")
        return

    fig, ax = plt.subplots(figsize=figsize)

    if pd.api.types.is_numeric_dtype(df[column]):
        sns.histplot(df[column].dropna(), kde=True, ax=ax, color='steelblue')
    else:
        unique_vals = df[column].nunique()
        if unique_vals > 30:
            logger.warning(f"⚠️ عمود '{column}' يحتوي على {unique_vals} فئة، الرسم قد يكون مزدحمًا.")
        sns.countplot(x=column, data=df, ax=ax, palette=palette)
        ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha='right')

    ax.set_title(f"Distribution of {column}")
    save_plot(fig, output_name, output_dir)


def save_dataframe(df: pd.DataFrame, name: str, output_dir: Optional[Path] = OUTPUT_DIR, file_format: str = 'csv'):
    ensure_output_dir(output_dir)
    file_format = file_format.lower()
    filepath = output_dir / f"{name}.{file_format}"

    try:
        if file_format == 'csv':
            df.to_csv(filepath, index=False)
        elif file_format in ['excel', 'xlsx']:
            df.to_excel(filepath, index=False)
        elif file_format == 'parquet':
            df.to_parquet(filepath, index=False)
        elif file_format == 'json':
            df.to_json(filepath, orient='records', lines=True)
        else:
            raise ValueError(f"صيغة غير مدعومة: {file_format}")
        logger.info(f"✅ تم حفظ البيانات: {filepath}")
    except Exception as e:
        logger.error(f"❌ فشل حفظ البيانات: {e}")


def get_numerical_columns(df: pd.DataFrame) -> list:
    numerical_cols = df.select_dtypes(include=['number']).columns.tolist()
    datetime_cols = df.select_dtypes(include=['datetime64[ns]']).columns.tolist()
    return [col for col in numerical_cols if col not in datetime_cols]


def get_categorical_columns(df: pd.DataFrame) -> list:
    return df.select_dtypes(include=['object', 'category', 'bool']).columns.tolist()


def log_basic_info(df: pd.DataFrame, name: str = "DataFrame", verbose: bool = True):
    logger.info(f"📊 {name}: الشكل = {df.shape}")
    logger.info(f"📈 أعمدة رقمية: {get_numerical_columns(df)}")
    logger.info(f"📋 أعمدة فئوية: {get_categorical_columns(df)}")

    if verbose:
        missing = df.isnull().sum()
        logger.info(f"🧼 قيم مفقودة:\n{missing}")

        total_rows = df.shape[0]
        missing_ratio = missing / total_rows
        high_missing = missing_ratio[missing_ratio > 0.3]
        if not high_missing.empty:
            for col, ratio in high_missing.items():
                logger.warning(f"⚠️ عمود '{col}' يحتوي على نسبة عالية من القيم المفقودة: {ratio:.2%}")
