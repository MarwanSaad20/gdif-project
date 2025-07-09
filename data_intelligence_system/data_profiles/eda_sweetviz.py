import os
from pathlib import Path
import sys
import pandas as pd
from ydata_profiling import ProfileReport

# ✅ إضافة مسار الجذر للمشروع
BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(BASE_DIR))

# ✅ استيراد من جذر المشروع
from data_intelligence_system.analysis.correlation_analysis import generate_correlation_matrix
from data_intelligence_system.data_profiles.eda_utils import load_clean_data, logger

# 🧭 المسارات
DEFAULT_DATA_PATH = BASE_DIR / "data_intelligence_system" / "data" / "processed" / "clean_data.csv"
OUTPUT_DIR = BASE_DIR / "data_profiles" / "eda_output"
REPORT_NAME = "eda_profile_report.html"
REPORT_PATH = OUTPUT_DIR / REPORT_NAME


def generate_profile_report(
    data_path: Path = None,
    output_path: Path = REPORT_PATH,
    compare_with: Path = None
):
    """
    توليد تقرير ydata-profiling تفاعلي للبيانات.

    :param data_path: مسار البيانات الرئيسية (CSV).
    :param output_path: مسار حفظ التقرير HTML.
    :param compare_with: ملف إضافي للمقارنة (اختياري).
    """
    logger.info("🚀 بدء توليد تقرير ydata-profiling ...")

    data_path = Path(data_path) if data_path else DEFAULT_DATA_PATH

    try:
        if not data_path.exists():
            logger.error(f"❌ الملف غير موجود: {data_path}")
            raise FileNotFoundError(f"File not found: {data_path}")

        df = load_clean_data(str(data_path))
        if df.empty:
            logger.error(f"❌ الملف موجود لكنه فارغ: {data_path}")
            raise ValueError(f"Data file is empty: {data_path}")

        # ✅ تجهيز مصفوفة الارتباط (حتى لو لم تُستخدم مباشرةً هنا)
        corr_matrix = generate_correlation_matrix(df)
        logger.info(f"✅ مصفوفة الارتباط:\n{corr_matrix}")

        if compare_with:
            compare_path = Path(compare_with)
            if not compare_path.exists():
                raise FileNotFoundError(f"File not found: {compare_path}")
            df_compare = load_clean_data(str(compare_path))

            logger.info("🔁 توليد تقرير مقارنة بين ملفين (يُعرض ملفين في تقريرين منفصلين)")
            profile_main = ProfileReport(df, title="الملف الرئيسي", explorative=True)
            profile_compare = ProfileReport(df_compare, title="الملف المقارن", explorative=True)

            OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
            profile_main.to_file(OUTPUT_DIR / "profile_main.html")
            profile_compare.to_file(OUTPUT_DIR / "profile_compare.html")
            logger.info("✅ تم حفظ تقريري المقارنة في مجلد الإخراج")

        else:
            profile = ProfileReport(df, title="تقرير البيانات", explorative=True)
            OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
            profile.to_file(str(output_path))
            logger.info(f"✅ تم حفظ تقرير ydata-profiling في: {output_path}")

    except Exception as e:
        logger.exception("❌ فشل توليد تقرير ydata-profiling")


# تشغيل مباشر
if __name__ == "__main__":
    generate_profile_report()
