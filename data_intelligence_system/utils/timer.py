import time
from contextlib import ContextDecorator
from functools import wraps

from data_intelligence_system.utils.logger import get_logger

logger = get_logger("Timer")


class Timer(ContextDecorator):
    """
    Context manager و decorator لحساب وقت تنفيذ قطعة كود.

    الاستخدام:
    1. كـ with block:
        with Timer("وصف المهمة"):
            # كود هنا

    2. كـ decorator للدوال:
        @Timer("تشغيل الدالة")
        def my_func():
            pass
    """

    def __init__(self, task_name: str = "Execution", logger_enabled: bool = True):
        self.task_name = task_name
        self.logger_enabled = logger_enabled
        self.start_time = None
        self.end_time = None
        self.elapsed = None

    def __enter__(self):
        self.start_time = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = time.perf_counter()
        self.elapsed = self.end_time - self.start_time
        self._log(self.elapsed, exc_type)
        return False  # لا نمنع الاستثناءات

    def _log(self, elapsed: float, exc_type=None):
        msg = f"[{self.task_name}] انتهى التنفيذ في {elapsed:.4f} ثانية."
        if exc_type:
            msg += f" ⚠️ (استثناء: {exc_type.__name__})"
        if self.logger_enabled:
            logger.info(msg)
        else:
            print(msg)


def timeit(func=None, *, task_name=None, logger_enabled=True):
    """
    Decorator بسيط لقياس وقت تنفيذ الدوال.

    المعاملات:
        task_name: اسم المهمة في اللوج (افتراضي اسم الدالة)
        logger_enabled: تفعيل/تعطيل تسجيل اللوج (إذا False، يطبع فقط)
    """
    def decorator_timeit(f):
        name = task_name or f.__name__

        @wraps(f)
        def wrapper(*args, **kwargs):
            start = time.perf_counter()
            try:
                result = f(*args, **kwargs)
                return result
            finally:
                end = time.perf_counter()
                elapsed = end - start
                msg = f"[{name}] انتهى التنفيذ في {elapsed:.4f} ثانية."
                if logger_enabled:
                    logger.info(msg)
                else:
                    print(msg)

        return wrapper

    return decorator_timeit(func) if func else decorator_timeit
