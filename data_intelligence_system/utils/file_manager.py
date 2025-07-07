import os
import pandas as pd
import json
import base64
import uuid
from datetime import datetime
from pathlib import Path

from data_intelligence_system.utils.logger import get_logger

logger = get_logger(name="FileManager")

SUPPORTED_FORMATS = [".csv", ".xlsx", ".xls", ".json", ".parquet", ".tsv", ".feather"]


def read_file(filepath: str, encoding: str = "utf-8") -> pd.DataFrame:
    path = Path(filepath)
    ext = path.suffix.lower()

    try:
        match ext:
            case ".csv":
                return pd.read_csv(path, encoding=encoding)
            case ".tsv":
                return pd.read_csv(path, sep="\t", encoding=encoding)
            case ".xls" | ".xlsx":
                return pd.read_excel(path)
            case ".json":
                with open(path, "r", encoding=encoding) as f:
                    data = json.load(f)
                if isinstance(data, dict):
                    return pd.json_normalize(data)
                elif isinstance(data, list):
                    if all(isinstance(i, dict) for i in data):
                        return pd.json_normalize(data)
                    elif all(isinstance(i, (list, dict)) for i in data):
                        return pd.DataFrame(data)
                    else:
                        raise ValueError(f"Unsupported JSON structure in: {path}")
                else:
                    raise ValueError(f"Unsupported JSON root type in: {path}")
            case ".parquet":
                return pd.read_parquet(path)
            case ".feather":
                return pd.read_feather(path)
            case _:
                raise ValueError(f"❌ Unsupported file format: {ext}")
    except Exception as e:
        logger.exception(f"⚠️ Failed to read file '{filepath}': {e}")
        raise RuntimeError(f"⚠️ Failed to read file '{filepath}': {e}")


def save_file(df: pd.DataFrame, filepath: str, encoding: str = "utf-8", compress: bool = False):
    path = Path(filepath)
    ext = path.suffix.lower()
    path.parent.mkdir(parents=True, exist_ok=True)

    try:
        match ext:
            case ".csv":
                df.to_csv(path, index=False, encoding=encoding, compression="gzip" if compress else None)
            case ".xls" | ".xlsx":
                df.to_excel(path, index=False)
            case ".json":
                df.to_json(path, orient="records", indent=4, force_ascii=False)
            case ".parquet":
                df.to_parquet(path, index=False, compression="snappy" if compress else None)
            case ".feather":
                df.to_feather(path)
            case _:
                raise ValueError(f"❌ Unsupported file format: {ext}")
    except Exception as e:
        logger.exception(f"⚠️ Failed to save file '{filepath}': {e}")
        raise RuntimeError(f"⚠️ Failed to save file '{filepath}': {e}")


def convert_file_format(source_path: str, target_format: str, target_path: str = None, encoding: str = "utf-8"):
    if not target_format.startswith("."):
        target_format = "." + target_format.lower()

    if target_format not in SUPPORTED_FORMATS:
        raise ValueError(f"❌ Unsupported target format: {target_format}")

    df = read_file(source_path, encoding=encoding)

    if not target_path:
        base = str(Path(source_path).with_suffix(""))
        target_path = f"{base}{target_format}"

    save_file(df, target_path, encoding=encoding)
    return target_path


def extract_file_name(filepath: str) -> str:
    return Path(filepath).stem


def save_uploaded_file(content: str, filename: str, target_dir: str = "data/raw") -> str:
    try:
        ext = Path(filename).suffix.lower()
        if ext not in SUPPORTED_FORMATS:
            raise ValueError(f"❌ Unsupported uploaded file format: {ext}")

        _, content_string = content.split(',')
        decoded = base64.b64decode(content_string)

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
        files = list(Path(directory).glob("*.csv"))
        if not files:
            return None
        latest_file = max(files, key=lambda f: f.stat().st_mtime)
        return str(latest_file)
    except Exception as e:
        logger.exception(f"❌ Failed to find latest processed file: {e}")
        raise RuntimeError(f"❌ Failed to find latest processed file: {e}")
