# data_intelligence_system/api/utils/logger.py

import logging
import os
from logging.handlers import RotatingFileHandler

# ✅ استيراد اللوجر العام من جذر المشروع (utils.logger)
from data_intelligence_system.utils.logger import get_logger as root_get_logger

# ✅ إعداد واجهة محلية لاستخدام نفس اللوجر الموحد من utils/logger.py
def get_logger(name: str = "api", level: int = logging.INFO) -> logging.Logger:
    """
    توفير لوجر موحد لجميع وحدات API باستخدام إعدادات logger العامة في utils/logger.py.
    """
    return root_get_logger(name=name, level=level)
