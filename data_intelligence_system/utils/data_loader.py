"""
utils/data_loader.py

تحميل البيانات من ملفات مختلفة (CSV, Excel, JSON, Parquet, TSV, Feather) بشكل موحد،
مع دعم تسجيل الأخطاء والتنبيه للملفات الفارغة.
"""

import json
from pathlib import Path
from typing import Callable

import pandas as pd

# ✅ لوجر موحد من جذر المشروع
from data_intelligence_system.utils.logger import get_logger

logger = get_logger(name="DataLoader")


def _load_csv(path: Path, encoding: str) -> pd.DataFrame:
    return pd.read_csv(path, encoding=encoding, on_bad_lines='warn')


def _load_excel(path: Path, encoding: str) -> pd.DataFrame:
    return pd.read_excel(path)


def _load_json(path: Path, encoding: str) -> pd.DataFrame:
    with open(path, 'r', encoding=encoding) as f:
        data = json.load(f)
    if isinstance(data, list):
        return pd.json_normalize(data)
    elif isinstance(data, dict):
        return pd.DataFrame([data])
    raise ValueError("تنسيق JSON غير مدعوم")


def _load_parquet(path: Path, encoding: str) -> pd.DataFrame:
    return pd.read_parquet(path)


def _load_tsv(path: Path, encoding: str) -> pd.DataFrame:
    return pd.read_csv(path, sep='\t', encoding=encoding)


def _load_feather(path: Path, encoding: str) -> pd.DataFrame:
    return pd.read_feather(path)


# خريطة الامتدادات إلى الدوال الخاصة بها (كلها بنفس التوقيع)
EXTENSION_LOADERS: dict[str, Callable[[Path, str], pd.DataFrame]] = {
    ".csv": _load_csv,
    ".xlsx": _load_excel,
    ".xls": _load_excel,
    ".json": _load_json,
    ".parquet": _load_parquet,
    ".tsv": _load_tsv,
    ".feather": _load_feather,
}


def load_data(filepath: str, encoding: str = "utf-8") -> pd.DataFrame:
    """
    تحميل البيانات من ملفات متعددة الصيغ.

    Args:
        filepath (str): المسار الكامل للملف
        encoding (str): ترميز القراءة للملفات النصية (افتراضي: utf-8)

    Returns:
        pd.DataFrame: إطار البيانات المحمّل

    Raises:
        FileNotFoundError: إذا لم يكن الملف موجودًا
        ValueError: إذا كان نوع الملف غير مدعوم أو المحتوى غير صالح
        RuntimeError: إذا فشل التحميل لأي سبب آخر
    """
    path = Path(filepath).expanduser().resolve()

    if not path.exists():
        logger.error(f"❌ الملف غير موجود: {path}")
        raise FileNotFoundError(f"الملف غير موجود: {path}")

    ext = path.suffix.lower()
    loader = EXTENSION_LOADERS.get(ext)

    if loader is None:
        logger.error(f"❌ نوع الملف غير مدعوم: {ext}")
        raise ValueError(f"نوع الملف غير مدعوم: {ext}")

    try:
        logger.info(f"📁 بدء تحميل الملف: {path}")
        df = loader(path, encoding)

        if df.empty:
            logger.warning(f"⚠️ تم تحميل الملف لكنه فارغ: {path}")

        return df

    except Exception as e:
        logger.exception(f"⚠️ فشل تحميل الملف: {path} بسبب: {e}")
        raise RuntimeError(f"⚠️ تعذر تحميل الملف '{path}': {str(e)}") from e
