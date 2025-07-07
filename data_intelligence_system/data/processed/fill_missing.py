import pandas as pd
import os
import logging

# إعداد اللوجنغ
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("FillMissing")

# ✅ تحديد المسار الجذري للمشروع تلقائيًا
PROJECT_ROOT = os.path.abspath(os.path.join(__file__, "../../../.."))
PROCESSED_DIR = os.path.join(PROJECT_ROOT, "data_intelligence_system", "data", "processed")

# ✅ تحديد الملفات بدقة
INPUT_FILE = os.path.join(PROCESSED_DIR, "clean_data_normalized.csv")
OUTPUT_FILE = os.path.join(PROCESSED_DIR, "clean_data_filled.csv")


def fill_missing(df: pd.DataFrame) -> pd.DataFrame:
    """
    تعويض القيم المفقودة في الأعمدة الرقمية بالوسيط،
    وفي الأعمدة النصية أو الفئوية بالقيمة الأكثر تكرارًا.
    """
    for col in df.columns:
        if df[col].isnull().sum() == 0:
            continue

        if df[col].dtype in ['float64', 'int64']:
            df[col] = df[col].fillna(df[col].median())
        else:
            mode = df[col].mode()
            if not mode.empty:
                df[col] = df[col].fillna(mode[0])
            else:
                df[col] = df[col].fillna("missing")
    return df


def main():
    print(f"📁 PROCESSED_DIR: {PROCESSED_DIR}")
    print(f"📄 INPUT_FILE: {INPUT_FILE}")

    if not os.path.exists(INPUT_FILE):
        logger.error(f"❌ الملف غير موجود: {INPUT_FILE}")
        return

    try:
        logger.info(f"📂 قراءة الملف: {INPUT_FILE}")
        df = pd.read_csv(INPUT_FILE, encoding='utf-8')
        logger.info("🔄 معالجة القيم المفقودة...")

        df = fill_missing(df)

        os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
        df.to_csv(OUTPUT_FILE, index=False, encoding='utf-8')

        logger.info(f"✅ تم الحفظ: {OUTPUT_FILE}")
    except Exception as e:
        logger.error(f"❌ خطأ أثناء المعالجة: {e}")


if __name__ == "__main__":
    main()
