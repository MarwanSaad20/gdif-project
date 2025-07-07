import logging
import os
from logging.handlers import TimedRotatingFileHandler
from typing import Optional


def get_logger(
    name: str = "DataIntelligenceLogger",
    log_dir: str = "logs",
    level: int = logging.INFO,
    reset: bool = False,
    rotation_when: str = 'midnight',
    backup_count: int = 7,
) -> logging.Logger:
    """
    إعداد لوجر موحد لتسجيل الأحداث في المشروع.
    - يستخدم TimedRotatingFileHandler لتدوير السجلات يوميًا والاحتفاظ بعدد محدد من الملفات.
    - يمكن إعادة تعيين الـlogger (reset) عند الحاجة.
    
    Args:
        name (str): اسم اللوجر.
        log_dir (str): مجلد حفظ ملفات اللوج.
        level (int): مستوى تسجيل الأحداث.
        reset (bool): إعادة تهيئة اللوجر بإزالة handlers الحاليين.
        rotation_when (str): فترة تدوير السجل (مثلاً 'midnight' يوميًا).
        backup_count (int): عدد النسخ الاحتياطية التي يتم الاحتفاظ بها.

    Returns:
        logging.Logger: كائن اللوجر المعدّ.
    """
    try:
        os.makedirs(log_dir, exist_ok=True)
    except Exception as e:
        raise OSError(f"فشل إنشاء مجلد السجلات '{log_dir}': {e}") from e

    log_file = os.path.join(log_dir, f"{name}.log")
    logger = logging.getLogger(name)

    if reset:
        logger.handlers.clear()

    logger.setLevel(level)

    if not logger.hasHandlers():
        file_handler = TimedRotatingFileHandler(
            log_file,
            when=rotation_when,
            backupCount=backup_count,
            encoding='utf-8'
        )
        file_formatter = logging.Formatter(
            '%(asctime)s — [%(levelname)s] — %(name)s — %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)

        console_handler = logging.StreamHandler()
        console_formatter = logging.Formatter('[%(levelname)s] %(message)s')
        console_handler.setFormatter(console_formatter)

        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    return logger
