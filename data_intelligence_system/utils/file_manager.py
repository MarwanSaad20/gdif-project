import os
import pandas as pd
import json
from datetime import datetime
import shutil
import base64
import uuid
from pathlib import Path

# ✅ استيراد اللوجر الموحّد
from data_intelligence_system.utils.logger import get_logger

logger = get_logger(name="FileManager")


# ====================
# 📥 قراءة البيانات
# ====================
def read_file(filepath: str, encoding: str = "utf-8") -> pd.DataFrame:
    ext = os.path.splitext(filepath)[1].lower()

    try:
        if ext == ".csv":
            return pd.read_csv(filepath, encoding=encoding)

        elif ext in [".xls", ".xlsx"]:
            return pd.read_excel(filepath)

        elif ext == ".json":
            with open(filepath, "r", encoding=encoding) as f:
                data = json.load(f)

            if isinstance(data, dict):
                return pd.json_normalize(data)

            elif isinstance(data, list):
                if all(isinstance(item, dict) for item in data):
                    return pd.json_normalize(data)
                elif all(isinstance(item, list) for item in data):
                    return pd.DataFrame(data)
                elif all(isinstance(item, (list, dict)) for item in data):
                    return pd.DataFrame(data)
                else:
                    raise RuntimeError(
                        f"⚠️ JSON contains unsupported list elements → type: {type(data[0])} in: {filepath}"
                    )

            else:
                raise RuntimeError(f"⚠️ Unsupported JSON root type: {type(data)} in: {filepath}")

        elif ext == ".parquet":
            return pd.read_parquet(filepath)

        elif ext == ".tsv":
            return pd.read_csv(filepath, sep="\t", encoding=encoding)

        elif ext == ".feather":
            return pd.read_feather(filepath)

        else:
            raise ValueError(f"❌ Unsupported file format: {ext}")

    except Exception as e:
        logger.exception(f"⚠️ Failed to read file '{filepath}': {e}")
        raise RuntimeError(f"⚠️ Failed to read file '{filepath}': {e}")


# ====================
# 💾 حفظ البيانات
# ====================
def save_file(df: pd.DataFrame, filepath: str, encoding: str = "utf-8", compress: bool = False):
    ext = os.path.splitext(filepath)[1].lower()
    os.makedirs(os.path.dirname(filepath), exist_ok=True)

    try:
        if ext == ".csv":
            df.to_csv(filepath, index=False, encoding=encoding, compression="gzip" if compress else None)
        elif ext in [".xls", ".xlsx"]:
            df.to_excel(filepath, index=False)
        elif ext == ".json":
            df.to_json(filepath, orient="records", indent=4, force_ascii=False)
        elif ext == ".parquet":
            df.to_parquet(filepath, index=False, compression="snappy" if compress else None)
        elif ext == ".feather":
            df.to_feather(filepath)
        else:
            raise ValueError(f"❌ Unsupported file format: {ext}")
    except Exception as e:
        logger.exception(f"⚠️ Failed to save file '{filepath}': {e}")
        raise RuntimeError(f"⚠️ Failed to save file '{filepath}': {e}")


# ====================
# 🔁 تحويل بين الصيغ
# ====================
def convert_file_format(source_path: str, target_format: str, target_path: str = None, encoding: str = "utf-8"):
    supported_formats = [".csv", ".xlsx", ".json", ".parquet", ".feather"]

    if not target_format.startswith("."):
        target_format = "." + target_format.lower()

    if target_format not in supported_formats:
        raise ValueError(f"❌ Unsupported target format: {target_format}")

    df = read_file(source_path, encoding=encoding)

    if not target_path:
        base, _ = os.path.splitext(source_path)
        target_path = f"{base}{target_format}"

    save_file(df, target_path, encoding=encoding)
    return target_path


# ====================
# 🔠 استخراج اسم الملف فقط بدون الامتداد
# ====================
def extract_file_name(filepath: str) -> str:
    base = os.path.basename(filepath)
    name = os.path.splitext(base)[0]
    return name


# ====================
# 📤 حفظ ملف مرفوع من المستخدم عبر واجهة Dash
# ====================
def save_uploaded_file(content: str, filename: str, target_dir: str = "data/raw") -> str:
    try:
        content_type, content_string = content.split(',')
        decoded = base64.b64decode(content_string)

        ext = os.path.splitext(filename)[1]
        unique_id = uuid.uuid4().hex[:8]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_name = f"{timestamp}_{unique_id}{ext}"

        os.makedirs(target_dir, exist_ok=True)
        path = os.path.join(target_dir, safe_name)

        with open(path, "wb") as f:
            f.write(decoded)

        return path

    except Exception as e:
        logger.exception(f"❌ Failed to save uploaded file: {e}")
        raise RuntimeError(f"❌ Failed to save uploaded file: {e}")


# ====================
# 🕑 الحصول على أحدث ملف معالجة في مجلد data/processed
# ====================
def get_latest_processed_file(directory: str = "data/processed") -> str | None:
    """
    يعيد مسار أحدث ملف .csv تم حفظه في مجلد المعالجة.
    """
    try:
        csv_files = list(Path(directory).glob("*.csv"))
        if not csv_files:
            return None
        latest_file = max(csv_files, key=lambda x: x.stat().st_mtime)
        return str(latest_file)
    except Exception as e:
        logger.exception(f"❌ Failed to find latest processed file: {e}")
        raise RuntimeError(f"❌ Failed to find latest processed file: {e}")
