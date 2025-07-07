from pathlib import Path
from functools import wraps
from typing import List, Optional, Union

# ✅ استيراد لوجر موحد من النظام
from data_intelligence_system.utils.logger import get_logger

logger = get_logger(name="ETLUtils")


def log_step(func):
    """
    Decorator to log the start and end of a function, and handle exceptions.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        logger.info(f"↪️ تشغيل: {func.__name__}")
        try:
            result = func(*args, **kwargs)
        except Exception as e:
            logger.error(f"❌ خطأ في {func.__name__}: {e}")
            raise
        logger.info(f"✅ انتهى: {func.__name__}")
        return result
    return wrapper


def get_all_files(directory: Union[str, Path], extensions: Optional[List[str]] = None) -> List[str]:
    """
    Return a list of all files in the directory. Optionally filter by extensions.
    """
    directory = Path(directory)
    files = []
    normalized_exts = {f".{ext.lstrip('.').lower()}" for ext in extensions} if extensions else None

    for path in directory.rglob("*"):
        if path.is_file() and (not normalized_exts or path.suffix.lower() in normalized_exts):
            files.append(str(path.resolve()))

    logger.info(f"📂 تم العثور على {len(files)} ملفات في {directory}")
    return files


def detect_file_type(filepath: Union[str, Path]) -> str:
    """
    Detect file type based on extension: csv, excel, json, or unsupported.
    """
    ext = Path(filepath).suffix.lower()
    if ext == '.csv':
        return 'csv'
    elif ext in ['.xls', '.xlsx']:
        return 'excel'
    elif ext == '.json':
        return 'json'
    else:
        return 'unsupported'


def is_supported_file(filepath: Union[str, Path]) -> bool:
    """
    Return True if the file is a supported type.
    """
    return detect_file_type(filepath) != 'unsupported'


def ensure_directory_exists(path: Union[str, Path]) -> Path:
    """
    Ensure directory exists; create it if it doesn't.
    """
    path = Path(path)
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)
        logger.info(f"📁 تم إنشاء المجلد: {path}")
    return path
