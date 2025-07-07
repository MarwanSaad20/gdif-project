import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from tabulate import tabulate
import logging
from typing import Dict, Any, Union
from pathlib import Path

# === إعداد المسارات ===
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data_intelligence_system" / "data" / "processed"
OUTPUT_DIR = BASE_DIR / "data_intelligence_system" / "analysis" / "analysis_output"

# === استيراد الأدوات المساعدة ===
from data_intelligence_system.analysis.analysis_utils import ensure_output_dir, save_plot
from data_intelligence_system.utils.data_loader import load_data  # ✅ جديد

# === إعداد اللوجر ===
logging.basicConfig(level=logging.INFO, format="%(asctime)s — %(levelname)s — %(message)s")
logger = logging.getLogger(__name__)


def compute_general_stats(df: pd.DataFrame) -> Dict[str, Union[int, float]]:
    total_cells = df.size
    missing_values = df.isnull().sum().sum()
    duplicated_rows = df.duplicated().sum()
    return {
        "Number of Rows": df.shape[0],
        "Number of Columns": df.shape[1],
        "Missing Values": missing_values,
        "Missing %": round((missing_values / total_cells) * 100, 2) if total_cells > 0 else 0.0,
        "Duplicated Rows": duplicated_rows
    }


def compute_numeric_summary(df: pd.DataFrame) -> Dict[str, Dict[str, Any]]:
    numeric_summary = df.describe(include=[np.number]).T
    numeric_summary["missing_values"] = df.isnull().sum()
    numeric_summary["missing_%"] = (df.isnull().mean() * 100).round(2)
    return numeric_summary.to_dict(orient="index")


def analyze_numerical_columns(df: pd.DataFrame):
    logger.info(f"🚀 بدء تحليل الأعمدة الرقمية ({len(df.columns)} عمود)")
    numeric_summary = compute_numeric_summary(df)
    logger.info(f"🔢 ملخص الإحصائيات الرقمية:\n{numeric_summary}")
    generate_numeric_histograms(df, filename_prefix="numeric_analysis")
    logger.info("✅ انتهى تحليل الأعمدة الرقمية")


def analyze_categorical_columns(df: pd.DataFrame, top_n: int = 10) -> Dict[str, pd.Series]:
    categorical_cols = df.select_dtypes(include=["object", "category"]).columns
    cat_summary = {}
    for col in categorical_cols:
        counts = df[col].value_counts(dropna=False).head(top_n)
        cat_summary[col] = counts
        logger.info(f"🔤 تحليل تكرار القيم للعمود '{col}':\n{counts.to_string()}")
    return cat_summary


def analyze_datetime_columns(df: pd.DataFrame) -> Dict[str, pd.Series]:
    datetime_cols = df.select_dtypes(include=['datetime64[ns]', 'datetime64[ns, UTC]']).columns
    datetime_summary = {}
    for col in datetime_cols:
        freq = df[col].dt.to_period("M").value_counts().sort_index()
        datetime_summary[col] = freq
        logger.info(f"⏱️ تحليل التوزيع الزمني للعمود '{col}':\n{freq.to_string()}")
    return datetime_summary


def generate_numeric_histograms(df: pd.DataFrame, filename_prefix: str, output_dir: Path = OUTPUT_DIR, bins: int = 30):
    ensure_output_dir(output_dir)
    numeric_cols = df.select_dtypes(include=[np.number]).columns

    for col in numeric_cols:
        plt.figure(figsize=(8, 4))
        df[col].hist(bins=bins, color='skyblue', edgecolor='black')
        plt.title(f"Distribution of {col}")
        plt.xlabel(col)
        plt.ylabel("Frequency")
        filename = f"{filename_prefix}_distribution_{col}.png"
        save_plot(plt.gcf(), filename, output_dir)
        plt.close()

    logger.info(f"✅ تم حفظ الرسوم البيانية للأعمدة الرقمية في: {output_dir}")


def save_categorical_value_counts(df: pd.DataFrame, filename_prefix: str, output_dir: Path = OUTPUT_DIR, top_n: int = 10):
    ensure_output_dir(output_dir)
    categorical_cols = df.select_dtypes(include=["object", "category"]).columns

    for col in categorical_cols:
        value_counts = df[col].value_counts(dropna=False).head(top_n)
        filepath = output_dir / f"{filename_prefix}_value_counts_{col}.csv"
        value_counts.to_csv(filepath)
        logger.info(f"✅ تم حفظ القيم المتكررة للعمود: {col}")


def generate_descriptive_stats(df_or_path: Union[pd.DataFrame, str, Path], filename_prefix: str = "output",
                               output_dir: Path = OUTPUT_DIR, save_outputs: bool = True) -> Dict[str, Any]:
    if isinstance(df_or_path, (str, Path)):
        df = load_data(str(df_or_path))  # ✅ استبدال التحميل اليدوي
        filename_prefix = Path(df_or_path).stem
        logger.info(f"✅ تم تحميل البيانات من: {df_or_path}")
    else:
        df = df_or_path

    logger.info("🚀 بدء التحليل الوصفي الكامل...")

    for col in df.columns:
        if df[col].dtype == object:
            try:
                converted = pd.to_datetime(df[col], errors='coerce')
                if not converted.isnull().all():
                    df[col] = converted
            except Exception:
                pass

    general_info = compute_general_stats(df)
    numeric_summary = compute_numeric_summary(df)
    categorical_summary = analyze_categorical_columns(df)
    datetime_summary = analyze_datetime_columns(df)

    if save_outputs:
        ensure_output_dir(output_dir)

        (output_dir / f"{filename_prefix}_general_info.txt").write_text(
            tabulate(general_info.items(), tablefmt="grid", stralign="left"), encoding="utf-8"
        )
        logger.info(f"📄 تم حفظ المعلومات العامة.")

        pd.DataFrame(numeric_summary).T.to_csv(output_dir / f"{filename_prefix}_numeric_stats.csv")
        logger.info(f"📄 تم حفظ الإحصائيات الرقمية.")

        for col, counts in categorical_summary.items():
            counts.to_csv(output_dir / f"{filename_prefix}_value_counts_{col}.csv")
            logger.info(f"📄 تم حفظ القيم المتكررة للعمود: {col}")

        for col, freq in datetime_summary.items():
            freq.to_csv(output_dir / f"{filename_prefix}_datetime_freq_{col}.csv")
            logger.info(f"📄 تم حفظ التحليل الزمني للعمود: {col}")

        generate_numeric_histograms(df, filename_prefix, output_dir)

    logger.info("✅ التحليل الوصفي اكتمل بنجاح.")
    return {
        "general_info": general_info,
        "numeric_summary": numeric_summary,
        "categorical_summary": categorical_summary,
        "datetime_summary": datetime_summary
    }


def compute_statistics(df_or_path):
    return generate_descriptive_stats(df_or_path)


if __name__ == "__main__":
    if not DATA_DIR.exists():
        logger.error(f"❌ مجلد البيانات غير موجود: {DATA_DIR}")
        exit(1)

    for file in DATA_DIR.iterdir():
        if file.suffix.lower() in [".csv", ".xlsx", ".xls", ".json"] and file.stat().st_size > 0:
            generate_descriptive_stats(file)
