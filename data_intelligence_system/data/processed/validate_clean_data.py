import pandas as pd
import logging
from pathlib import Path

# إعداد اللوجنغ
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("ValidateCleanData")

# المسار المبدئي (قابل للتعديل لاحقًا من config)
PROCESSED_DIR = Path("C:/Users/PC/PycharmProjects/PythonProject10/data_intelligence_system/data/processed")
INPUT_FILE = PROCESSED_DIR / "clean_data_scaled.csv"


def validate(df: pd.DataFrame) -> dict:
    """تحقق من جودة البيانات وارجع ملخص النتائج"""

    result = {
        "num_rows": df.shape[0],
        "num_columns": df.shape[1],
        "total_missing": df.isnull().sum().sum(),
        "empty": df.empty
    }

    logger.info("📊 ملخص البيانات النهائية:")
    logger.info(f"- عدد الصفوف: {result['num_rows']}")
    logger.info(f"- عدد الأعمدة: {result['num_columns']}")
    logger.info(f"- القيم الناقصة الكلية: {result['total_missing']}")

    if result["empty"]:
        logger.warning("⚠️ الملف فارغ تمامًا!")
    elif result["total_missing"] > 0:
        logger.warning("⚠️ توجد قيم ناقصة! راجع مرحلة التنظيف.")
    else:
        logger.info("✅ لا توجد قيم ناقصة.")

    try:
        desc = df.describe().to_string()
        logger.info("\n📈 وصف إحصائي للبيانات:\n" + desc)
    except Exception as e:
        logger.warning(f"⚠️ فشل في توليد الوصف الإحصائي: {e}")

    return result


def main(input_file: Path = INPUT_FILE):
    if not input_file.exists():
        logger.error(f"❌ الملف غير موجود: {input_file}")
        return

    try:
        df = pd.read_csv(input_file, encoding='utf-8')
        if df.empty:
            logger.warning("⚠️ تم تحميل ملف فارغ.")
        return validate(df)
    except pd.errors.EmptyDataError:
        logger.error("❌ الملف موجود لكنّه فارغ تمامًا.")
    except Exception as e:
        logger.error(f"❌ خطأ أثناء التحميل أو التحقق: {e}")


if __name__ == "__main__":
    main()
