import logging
from functools import lru_cache

# استيراد دالة اللوجر الموحدة من الجذر
from data_intelligence_system.utils.logger import get_logger as root_get_logger

@lru_cache(maxsize=None)
def get_logger(name: str = "api", level: int = logging.INFO) -> logging.Logger:
    """
    توفير لوجر موحد لجميع وحدات API باستخدام إعدادات logger العامة في utils/logger.py.
    تستخدم caching لمنع إنشاء مثيلات متعددة بنفس الاسم.

    :param name: اسم اللوجر.
    :param level: مستوى اللوجر (default: logging.INFO).
    :return: كائن logging.Logger موحد.
    """
    return root_get_logger(name=name, level=level)
