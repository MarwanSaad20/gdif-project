import os
import logging
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler

# إعداد اللوجنغ
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("ScaleNumericals")

# ✅ تعريف المسارات وفقًا لبنية المشروع
BASE_DIR = r"C:\Users\PC\PycharmProjects\PythonProject10\data_intelligence_system\data\processed"
INPUT_FILE = os.path.join(BASE_DIR, "clean_data_encoded.csv")
OUTPUT_FILE = os.path.join(BASE_DIR, "clean_data_scaled.csv")

def scale_numericals(df: pd.DataFrame, scaler=None) -> pd.DataFrame:
    """
    تطبيق موازنة على الأعمدة الرقمية في DataFrame باستخدام StandardScaler أو أي Scaler آخر.
    """
    df = df.copy()
    scaler = scaler or StandardScaler()

    num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    if not num_cols:
        logger.warning("⚠️ لا توجد أعمدة رقمية للموازنة.")
        return df

    try:
        df[num_cols] = scaler.fit_transform(df[num_cols])
        logger.info(f"✅ تمت موازنة الأعمدة الرقمية: {num_cols}")
    except Exception as e:
        logger.error(f"❌ فشل في موازنة الأعمدة الرقمية: {e}")
        raise

    return df

def main():
    if not os.path.exists(INPUT_FILE):
        logger.error(f"❌ الملف غير موجود: {INPUT_FILE}")
        return

    try:
        logger.info(f"📂 قراءة الملف: {INPUT_FILE}")
        df = pd.read_csv(INPUT_FILE, encoding="utf-8")

        logger.info("🔄 توحيد مقياس المتغيرات الرقمية...")
        df = scale_numericals(df)

        os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
        df.to_csv(OUTPUT_FILE, index=False, encoding="utf-8")
        logger.info(f"✅ تم حفظ الملف إلى: {OUTPUT_FILE}")
    except Exception as e:
        logger.error(f"❌ خطأ أثناء المعالجة: {e}")

if __name__ == "__main__":
    main()
