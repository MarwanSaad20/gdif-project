from pathlib import Path
import pandas as pd
import json
import base64
import uuid
from datetime import datetime

from data_intelligence_system.utils.logger import get_logger

logger = get_logger(name="FileManager")


def read_file(filepath: str, encoding: str = "utf-8") -> pd.DataFrame:
    ext = Path(filepath).suffix.lower()

    try:
        if ext == ".csv":
            return pd.read_csv(filepath, encoding=encoding)
        elif ext in [".xls", ".xlsx"]:
            return pd.read_excel(filepath)
        elif ext == ".json":
            with open(filepath, "r", encoding=encoding) as f:
                data = json.load(f)

            if isinstance(data, dict):
                # محاولة تفكيك JSON معقد يحتوي على بيانات داخل قائمة ضمن قيم المفاتيح
                # نحاول إيجاد أول قائمة في القيم وتحويلها إلى DataFrame
                for key, value in data.items():
                    if isinstance(value, list):
                        # إذا القائمة تحتوي dicts أو قوائم، نستخدمها مباشرة
                        if all(isinstance(item, (dict, list)) for item in value):
                            return pd.DataFrame(value)
                # إن لم نجد قائمة مناسبة، نستخدم normalize كخيار أخير
                return pd.json_normalize(data)

            elif isinstance(data, list):
                # تأكد أن القائمة تحتوي dicts أو قوائم
                if all(isinstance(item, (dict, list)) for item in data):
                    return pd.DataFrame(data)
                else:
                    raise RuntimeError(f"⚠️ JSON contains unsupported list elements → type: {type(data[0])}")
            else:
                raise RuntimeError(f"⚠️ Unsupported JSON root type: {type(data)}")
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


def save_file(df: pd.DataFrame, filepath: str, encoding: str = "utf-8", compress: bool = False):
    ext = Path(filepath).suffix.lower()
    Path(filepath).parent.mkdir(parents=True, exist_ok=True)

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


def convert_file_format(source_path: str, target_format: str, target_path: str = None, encoding: str = "utf-8") -> str:
    supported_formats = [".csv", ".xlsx", ".json", ".parquet", ".feather"]

    target_format = target_format if target_format.startswith(".") else f".{target_format.lower()}"
    if target_format not in supported_formats:
        raise ValueError(f"❌ Unsupported target format: {target_format}")

    df = read_file(source_path, encoding=encoding)
    if not target_path:
        target_path = str(Path(source_path).with_suffix(target_format))

    save_file(df, target_path, encoding=encoding)
    return target_path


def extract_file_name(filepath: str) -> str:
    return Path(filepath).stem


def save_uploaded_file(content: str, filename: str, target_dir: str = "data/raw") -> str:
    try:
        _, content_string = content.split(',')
        decoded = base64.b64decode(content_string)

        ext = Path(filename).suffix
        unique_id = uuid.uuid4().hex[:8]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_name = f"{timestamp}_{unique_id}{ext}"

        target_path = Path(target_dir) / safe_name
        target_path.parent.mkdir(parents=True, exist_ok=True)

        with open(target_path, "wb") as f:
            f.write(decoded)

        return str(target_path)

    except Exception as e:
        logger.exception(f"❌ Failed to save uploaded file: {e}")
        raise RuntimeError(f"❌ Failed to save uploaded file: {e}")


def get_latest_processed_file(directory: str = "data/processed") -> str | None:
    try:
        csv_files = list(Path(directory).glob("*.csv"))
        if not csv_files:
            return None
        latest_file = max(csv_files, key=lambda x: x.stat().st_mtime)
        return str(latest_file)
    except Exception as e:
        logger.exception(f"❌ Failed to find latest processed file: {e}")
        raise RuntimeError(f"❌ Failed to find latest processed file: {e}")
