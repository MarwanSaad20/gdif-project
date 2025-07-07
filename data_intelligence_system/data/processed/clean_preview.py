from pathlib import Path
import pandas as pd
import logging
import sys

# إعداد المسارات
BASE_DIR = Path(__file__).resolve().parents[2]
PROCESSED_DIR = BASE_DIR / 'data' / 'processed'
INPUT_FILE = PROCESSED_DIR / 'clean_data.csv'

# إعداد اللوغر
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("CleanPreview")

def preview(df: pd.DataFrame, rows: int = 10) -> None:
    """
    عرض أول N صفوف وبعض الإحصاءات من DataFrame.
    """
    logger.info(f"📋 معاينة أول {rows} صفوف:")
    logger.info("\n" + df.head(rows).to_string())
    logger.info("📊 إحصاءات موجزة:")
    logger.info("\n" + df.describe(include='all').transpose().to_string())

def run_preview(file_path: Path = INPUT_FILE) -> pd.DataFrame:
    """
    تحميل البيانات من الملف المحدد ومعاينتها.
    """
    if not file_path.exists():
        logger.error(f"❌ الملف غير موجود: {file_path}")
        sys.exit(1)

    try:
        df = pd.read_csv(file_path, encoding='utf-8')
        preview(df)
        return df
    except Exception as e:
        logger.error(f"❌ خطأ عند قراءة الملف: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_preview()
