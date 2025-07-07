import os
import pandas as pd
import logging
import json

# 📁 إعداد المسارات
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
RAW_DIR = os.path.join(BASE_DIR, 'data', 'raw')
LOG_DIR = os.path.join(BASE_DIR, 'logs')
os.makedirs(LOG_DIR, exist_ok=True)

# ✅ إعداد اللوجر
logger = logging.getLogger("ValidateStructure")
logger.setLevel(logging.INFO)
if not logger.hasHandlers():
    handler = logging.StreamHandler()
    logger.addHandler(handler)

# ✅ الأعمدة المطلوبة حسب النوع
REQUIRED_COLUMNS = {
    ".csv": ["id", "date"],
    ".json": ["id", "date"],
    ".xlsx": ["id", "date"]
}


def load_dataframe(filepath: str, ext: str) -> pd.DataFrame | None:
    try:
        if ext == ".csv":
            return pd.read_csv(filepath, encoding="utf-8")
        elif ext == ".xlsx":
            return pd.read_excel(filepath)
        elif ext == ".json":
            try:
                return pd.read_json(filepath, lines=True)
            except Exception:
                with open(filepath, encoding='utf-8') as f:
                    return pd.json_normalize(json.load(f))
        return None
    except Exception as e:
        logger.error(f"❌ فشل قراءة الملف {os.path.basename(filepath)}: {e}")
        return None


def validate_file_structure(filepath: str) -> None:
    ext = os.path.splitext(filepath)[1].lower()
    filename = os.path.basename(filepath)

    if ext not in REQUIRED_COLUMNS:
        logger.warning(f"❌ صيغة غير مدعومة للتحقق: {filename}")
        return

    df = load_dataframe(filepath, ext)
    if df is None or df.empty or df.columns.empty:
        logger.warning(f"⚠️ {filename}: الملف فارغ أو لا يحتوي على أعمدة.")
        return

    missing = [col for col in REQUIRED_COLUMNS[ext] if col not in df.columns]
    if missing:
        logger.warning(f"⚠️ {filename}: الأعمدة الناقصة → {missing}")
    else:
        logger.info(f"✅ {filename}: الهيكلية صحيحة.")


def main() -> None:
    logger.info("🔎 بدء التحقق من هيكلية ملفات البيانات الخام...\n")

    try:
        files = os.listdir(RAW_DIR)
    except Exception as e:
        logger.error(f"❌ خطأ عند قراءة مجلد 'raw/': {e}")
        return

    for file in files:
        full_path = os.path.join(RAW_DIR, file)
        ext = os.path.splitext(file)[1].lower()
        if ext in REQUIRED_COLUMNS:
            validate_file_structure(full_path)

    logger.info("\n🎯 انتهى التحقق من الهيكلية.")


if __name__ == "__main__":
    main()
