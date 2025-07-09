import pandas as pd
import numpy as np
from tabulate import tabulate
import logging
from typing import Dict, Any, Union
from pathlib import Path

# === إعداد المسارات ===
BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "data_intelligence_system" / "data" / "processed"
OUTPUT_DIR = BASE_DIR / "data_intelligence_system" / "analysis" / "analysis_output"

# === استيراد الأدوات المساعدة ===
from data_intelligence_system.analysis.analysis_utils import ensure_output_dir, plot_distribution
from data_intelligence_system.utils.data_loader import load_data
from data_intelligence_system.utils.timer import Timer

# === إعداد اللوجر ===
logging.basicConfig(level=logging.INFO, format="%(asctime)s — %(levelname)s — %(message)s")
logger = logging.getLogger(__name__)


def compute_general_stats(df: pd.DataFrame) -> Dict[str, Union[int, float]]:
    """
    تحسب إحصائيات عامة عن الداتا فريم.
    
    Returns:
        dict: عدد الصفوف، الأعمدة، القيم المفقودة (عدد ونسبة)، والصفوف المكررة.
    """
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
    """
    تحسب ملخص إحصائي للأعمدة الرقمية مع قيم مفقودة.
    
    Returns:
        dict: إحصائيات الوصفية لكل عمود رقمي.
    """
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    if numeric_cols.empty:
        return {}
    
    numeric_df = df[numeric_cols]
    desc = numeric_df.describe().T
    missing_counts = numeric_df.isnull().sum()
    missing_percents = (numeric_df.isnull().mean() * 100).round(2)
    
    desc["missing_values"] = missing_counts
    desc["missing_%"] = missing_percents
    return desc.to_dict(orient="index")


def analyze_categorical_columns(df: pd.DataFrame, top_n: int = 10) -> Dict[str, pd.Series]:
    """
    تحلل الأعمدة التصنيفية وتعيد تكرار أعلى القيم.
    """
    categorical_cols = df.select_dtypes(include=["object", "category"]).columns
    cat_summary = {}
    for col in categorical_cols:
        counts = df[col].value_counts(dropna=False).head(top_n)
        cat_summary[col] = counts
        logger.info(f"🔤 تكرار القيم للعمود '{col}':\n{counts.to_string()}")
    return cat_summary


def analyze_datetime_columns(df: pd.DataFrame) -> Dict[str, pd.Series]:
    """
    تحلل الأعمدة الزمنية وتعيد توزيع التكرار الشهري.
    """
    datetime_cols = df.select_dtypes(include=['datetime64[ns]', 'datetime64[ns, UTC]']).columns
    datetime_summary = {}
    for col in datetime_cols:
        freq = df[col].dt.to_period("M").value_counts().sort_index()
        datetime_summary[col] = freq
        logger.info(f"⏱️ توزيع زمني للعمود '{col}':\n{freq.to_string()}")
    return datetime_summary


def generate_numeric_histograms(df: pd.DataFrame, filename_prefix: str,
                                output_dir: Path = OUTPUT_DIR, bins: int = 30):
    """
    توليد وحفظ الرسوم البيانية للأعمدة الرقمية.
    """
    ensure_output_dir(output_dir)
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    for col in numeric_cols:
        try:
            plot_distribution(df, column=col,
                              output_name=f"{filename_prefix}_distribution_{col}.png",
                              output_dir=output_dir, bins=bins)
        except Exception as e:
            logger.warning(f"⚠️ فشل رسم العمود '{col}': {e}")
    logger.info(f"✅ حفظ الرسوم البيانية للأعمدة الرقمية في: {output_dir}")


@Timer("التحليل الوصفي الكامل")
def generate_descriptive_stats(df_or_path: Union[pd.DataFrame, str, Path],
                               filename_prefix: str = "output",
                               output_dir: Path = OUTPUT_DIR,
                               save_outputs: bool = True) -> Dict[str, Any]:
    """
    الدالة الرئيسية لإجراء التحليل الوصفي الكامل.
    
    Args:
        df_or_path: إما DataFrame أو مسار ملف بيانات.
        filename_prefix: بادئة أسماء الملفات الناتجة.
        output_dir: مجلد حفظ النتائج.
        save_outputs: حفظ النتائج إلى ملفات إذا True.
    
    Returns:
        dict: ملخصات التحليل العام، الرقمي، التصنيفي، والزمني.
    """
    if isinstance(df_or_path, (str, Path)):
        df = load_data(str(df_or_path))
        filename_prefix = Path(df_or_path).stem
        logger.info(f"✅ تحميل البيانات من: {df_or_path}")
    elif isinstance(df_or_path, pd.DataFrame):
        df = df_or_path.copy()
    else:
        raise TypeError("المدخل يجب أن يكون DataFrame أو مسار ملف.")

    logger.info("🚀 بدء التحليل الوصفي الكامل...")

    # محاولة تحويل الأعمدة النصية إلى تواريخ مرة واحدة فقط
    object_cols = df.select_dtypes(include=["object"]).columns
    for col in object_cols:
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

        general_info_path = output_dir / f"{filename_prefix}_general_info.txt"
        general_info_path.write_text(
            tabulate(general_info.items(), tablefmt="grid", stralign="left"), encoding="utf-8"
        )
        logger.info(f"📄 حفظ المعلومات العامة في: {general_info_path}")

        numeric_stats_path = output_dir / f"{filename_prefix}_numeric_stats.csv"
        pd.DataFrame(numeric_summary).T.to_csv(numeric_stats_path)
        logger.info(f"📄 حفظ الإحصائيات الرقمية في: {numeric_stats_path}")

        for col, counts in categorical_summary.items():
            cat_path = output_dir / f"{filename_prefix}_value_counts_{col}.csv"
            counts.to_csv(cat_path)
            logger.info(f"📄 حفظ القيم المتكررة للعمود: {col} في {cat_path}")

        for col, freq in datetime_summary.items():
            datetime_path = output_dir / f"{filename_prefix}_datetime_freq_{col}.csv"
            freq.to_csv(datetime_path)
            logger.info(f"📄 حفظ التوزيع الزمني للعمود: {col} في {datetime_path}")

        generate_numeric_histograms(df, filename_prefix, output_dir)

    logger.info("✅ التحليل الوصفي اكتمل بنجاح.")
    return {
        "general_info": general_info,
        "numeric_summary": numeric_summary,
        "categorical_summary": categorical_summary,
        "datetime_summary": datetime_summary
    }


if __name__ == "__main__":
    if not DATA_DIR.exists():
        logger.error(f"❌ مجلد البيانات غير موجود: {DATA_DIR}")
        exit(1)

    for file in DATA_DIR.iterdir():
        if file.suffix.lower() in [".csv", ".xlsx", ".xls", ".json"] and file.stat().st_size > 0:
            generate_descriptive_stats(file)
