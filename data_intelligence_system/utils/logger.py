# data_intelligence_system/utils/logger.py

import logging
from logging.handlers import TimedRotatingFileHandler
from typing import Optional
from pathlib import Path

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
    - يستخدم TimedRotatingFileHandler لتدوير السجلات يوميًا.
    - يسمح بعرض الرسائل في الكونسول أيضًا.
    - يدعم إعادة تهيئة اللوجر لمنع التكرار عند إعادة الاستيراد.
    """
    log_path = Path(log_dir).resolve()
    try:
        log_path.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        raise OSError(f"❌ فشل إنشاء مجلد السجلات '{log_path}': {e}") from e

    log_file = log_path / f"{name}.log"
    logger = logging.getLogger(name)

    if reset:
        logger.handlers.clear()

    logger.setLevel(level)
    logger.propagate = False  # ⛔️ لمنع التكرار في اللوجات

    if not logger.hasHandlers():
        # 📁 File Handler
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

        # 🖥 Console Handler
        console_handler = logging.StreamHandler()
        console_formatter = logging.Formatter('[%(levelname)s] %(message)s')
        console_handler.setFormatter(console_formatter)
        console_handler.setLevel(level)

        # 🧩 إضافة الـ Handlers
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    return logger
