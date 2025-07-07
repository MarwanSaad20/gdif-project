import logging
from pathlib import Path
from typing import Optional, Union, List, Tuple
from datetime import datetime
import pandas as pd

# ✅ استيرادات محدثة من الجذر
from data_intelligence_system.etl.transform import transform_datasets
from data_intelligence_system.analysis.descriptive_stats import (
    analyze_numerical_columns,
    analyze_categorical_columns,
    analyze_datetime_columns
)
from data_intelligence_system.etl.extract import extract_file, extract_all_data
from data_intelligence_system.core.data_bindings import save_uploaded_data
from data_intelligence_system.config.paths_config import RAW_DATA_DIR, PROCESSED_DATA_DIR

# 🛠️ إعداد نظام التسجيل
LOG_FORMAT = "%(asctime)s — %(levelname)s — %(name)s — %(message)s"
logging.basicConfig(
    level=logging.INFO,
    format=LOG_FORMAT,
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("etl.pipeline")


def analyze_columns(df: pd.DataFrame, name: str):
    logger.info(f"📊 بدء التحليل للملف: {name}")

    numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns.tolist()
    categorical_cols = df.select_dtypes(include=['object', 'category', 'bool']).columns.tolist()
    datetime_cols = df.select_dtypes(include=['datetime64[ns]']).columns.tolist()

    logger.info(f"   الأعمدة الرقمية: {numeric_cols}")
    logger.info(f"   الأعمدة النصية: {categorical_cols}")
    logger.info(f"   الأعمدة الزمنية: {datetime_cols}")

    if numeric_cols:
        analyze_numerical_columns(df[numeric_cols])
        logger.info("   ✅ تحليل الأعمدة الرقمية مكتمل.")

    if categorical_cols:
        analyze_categorical_columns(df[categorical_cols])
        logger.info("   ✅ تحليل الأعمدة النصية مكتمل.")

    if datetime_cols:
        analyze_datetime_columns(df[datetime_cols])
        logger.info("   ✅ تحليل الأعمدة الزمنية مكتمل.")


def run_full_pipeline(
    filepath: Optional[Union[str, Path]] = None,
    output_dir: Union[str, Path] = PROCESSED_DATA_DIR,
    encode_type: str = 'label',
    scale_type: str = 'standard',
) -> bool:
    """
    🚀 تنفيذ شامل لخط أنابيب ETL:
    - استخراج بيانات من ملف محدد أو من مجلد raw/
    - تحويل وتنظيف وترميز وموازنة البيانات
    - تحليل الأعمدة الرقمية، النصية والزمنية
    - حفظ البيانات النهائية في مجلد processed/
    """
    output_dir = Path(output_dir)
    start_time = datetime.now()
    logger.info("🚀 بدء تنفيذ خط أنابيب ETL ...")

    try:
        if filepath:
            filepath = Path(filepath)
            logger.info(f"📥 استخراج ملف واحد: {filepath.name}")
            df_dict = extract_file(filepath)
            datasets = list(df_dict.items())  # extract_file returns Dict[str, DataFrame]
        else:
            logger.info(f"📥 استخراج جميع الملفات من المسارات المحددة")
            datasets = extract_all_data()

        if not datasets:
            logger.warning("⚠️ لم يتم العثور على بيانات للمعالجة.")
            return False

        logger.info("🧹 بدء تحويل البيانات (تنظيف + ترميز + موازنة)")
        cleaned_datasets = transform_datasets(
            datasets,
            encode_type=encode_type,
            scale_type=scale_type
        )

        for name, df_clean in cleaned_datasets:
            if df_clean.empty:
                logger.warning(f"⚠️ الملف {name} فارغ بعد التحويل. تم تخطيه.")
                continue

            analyze_columns(df_clean, name)

            clean_name = name.rsplit(".", 1)[0]  # إزالة الامتداد إن وجد
            saved_path = save_uploaded_data(df_clean, filename=f"cleaned_{clean_name}.csv")
            logger.info(f"💾 تم حفظ البيانات المعالجة في: {saved_path}")

        elapsed = datetime.now() - start_time
        logger.info(f"✅ التحليل الكامل اكتمل خلال {elapsed}")
        return True

    except Exception as e:
        logger.exception(f"❌ فشل في تنفيذ التحليل الديناميكي: {e}")
        return False


if __name__ == "__main__":
    success = run_full_pipeline(
        output_dir=PROCESSED_DATA_DIR,
        encode_type='onehot',
        scale_type='minmax',
    )
    if success:
        logger.info("✅ ETL pipeline انتهت بنجاح 🚀")
    else:
        logger.error("❌ فشل تنفيذ ETL pipeline، راجع التفاصيل.")
