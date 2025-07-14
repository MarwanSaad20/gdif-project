import logging
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path
from typing import Optional
from functools import lru_cache


@lru_cache(maxsize=None)
def get_logger(
    name: str = "DataIntelligenceLogger",
    log_dir: str = "logs",
    level: int = logging.INFO,
    reset: bool = False,
    rotation_when: str = 'midnight',
    backup_count: int = 7,
    console_only: bool = False,
    file_only: bool = False,
) -> logging.Logger:
    """
    إعداد لوجر موحد لتسجيل الأحداث في المشروع.
    - يستخدم TimedRotatingFileHandler لتدوير السجلات يوميًا.
    - يسمح بعرض الرسائل في الكونسول أيضًا.
    - يدعم إعادة تهيئة اللوجر لمنع التكرار عند إعادة الاستيراد.

    :param name: اسم اللوجر.
    :param log_dir: مسار مجلد السجلات.
    :param level: مستوى اللوجر.
    :param reset: إعادة تهيئة اللوجر (مسح الـ handlers).
    :param rotation_when: متى يتم تدوير الملفات (مثلاً: 'midnight').
    :param backup_count: عدد النسخ الاحتياطية المحتفظ بها.
    :param console_only: تفعيل اللوج فقط على الكونسول.
    :param file_only: تفعيل اللوج فقط على الملف.
    :return: كائن logging.Logger.
    """
    logger = logging.getLogger(name)

    if reset:
        logger.handlers.clear()

    logger.setLevel(level)
    logger.propagate = False  # لمنع تكرار اللوجات

    if not logger.hasHandlers():
        if not console_only:
            log_path = Path(log_dir).resolve()
            try:
                log_path.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                raise OSError(f"❌ فشل إنشاء مجلد السجلات '{log_path}': {e}") from e

            log_file = log_path / f"{name}.log"
            file_handler = TimedRotatingFileHandler(
                filename=log_file,
                when=rotation_when,
                backupCount=backup_count,
                encoding='utf-8'
            )
            file_formatter = logging.Formatter(
                '%(asctime)s — [%(levelname)s] — %(name)s — %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            file_handler.setFormatter(file_formatter)
            file_handler.setLevel(level)
            logger.addHandler(file_handler)

        if not file_only:
            console_handler = logging.StreamHandler()
            console_formatter = logging.Formatter('[%(levelname)s] %(message)s')
            console_handler.setFormatter(console_formatter)
            console_handler.setLevel(level)
            logger.addHandler(console_handler)

    return logger
