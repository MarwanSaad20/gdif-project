import os
import json
import logging
import pandas as pd

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))

# 📂 المسارات
RAW_DIR = os.path.join(BASE_DIR, 'data', 'raw')  # مسار ملفات البيانات الخام
SUPPORTED_FORMATS = {".csv", ".xlsx", ".json"}

# إعداد اللوجنج
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("ConvertFormat")


def load_dataframe(file_path: str) -> pd.DataFrame | None:
    """تحميل الملف إلى DataFrame بحسب الامتداد."""
    ext = os.path.splitext(file_path)[1].lower()
    try:
        if ext == ".csv":
            return pd.read_csv(file_path, encoding="utf-8")
        elif ext == ".xlsx":
            return pd.read_excel(file_path)
        elif ext == ".json":
            try:
                return pd.read_json(file_path, lines=True)
            except:
                with open(file_path, encoding='utf-8') as f:
                    return pd.json_normalize(json.load(f))
        else:
            raise ValueError(f"Unsupported source format: {ext}")
    except Exception as e:
        logger.error(f"❌ فشل قراءة الملف {file_path}: {e}")
        return None


def convert_file(file_path: str, target_format: str) -> None:
    """تحويل ملف مفرد إلى صيغة أخرى (csv, xlsx, json)."""
    filename, ext = os.path.splitext(os.path.basename(file_path))
    ext = ext.lower()
    target_format = target_format.lower()

    if ext == target_format:
        logger.warning(f"⚠️ الملف بالفعل بصيغة {target_format}: {filename}{ext}")
        return

    if target_format not in SUPPORTED_FORMATS:
        logger.error(f"❌ صيغة الهدف غير مدعومة: {target_format}")
        return

    df = load_dataframe(file_path)
    if df is None or df.empty:
        logger.warning(f"⚠️ تجاهل الملف (فارغ أو غير قابل للقراءة): {file_path}")
        return

    new_filename = f"{filename}{target_format}"
    new_path = os.path.join(RAW_DIR, new_filename)

    try:
        if target_format == ".csv":
            df.to_csv(new_path, index=False, encoding="utf-8")
        elif target_format == ".xlsx":
            df.to_excel(new_path, index=False)
        elif target_format == ".json":
            df.to_json(new_path, orient="records", indent=4, force_ascii=False)

        logger.info(f"✅ تم التحويل: {filename}{ext} → {new_filename}")
    except Exception as e:
        logger.error(f"❌ فشل حفظ الملف الجديد {new_path}: {e}")


def convert_all_files(target_format: str = ".csv", source_dir: str = RAW_DIR) -> None:
    """تحويل جميع الملفات في مجلد إلى صيغة محددة."""
    logger.info("🔁 بدء تحويل صيغ الملفات...\n")

    try:
        for file in os.listdir(source_dir):
            full_path = os.path.join(source_dir, file)
            if os.path.isfile(full_path):
                ext = os.path.splitext(file)[1].lower()
                if ext in SUPPORTED_FORMATS:
                    convert_file(full_path, target_format)
    except Exception as e:
        logger.error(f"❌ خطأ عام أثناء التحويل: {e}")

    logger.info("\n🎯 اكتمل التحويل.")


if __name__ == "__main__":
    convert_all_files(".csv")
