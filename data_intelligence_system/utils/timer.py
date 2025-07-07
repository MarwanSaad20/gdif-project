import time
from contextlib import ContextDecorator
from functools import wraps

# ✅ استيراد لوجر المشروع من المسار الجذري
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

    def __enter__(self):
        self.start_time = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = time.perf_counter()
        self.elapsed = self.end_time - self.start_time
        msg = f"[{self.task_name}] انتهى التنفيذ في {self.elapsed:.4f} ثانية."
        if self.logger_enabled:
            logger.info(msg)
        else:
            print(msg)
        return False  # لا نمنع الاستثناءات


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
            result = f(*args, **kwargs)
            end = time.perf_counter()
            elapsed = end - start
            msg = f"[{name}] انتهى التنفيذ في {elapsed:.4f} ثانية."
            if logger_enabled:
                logger.info(msg)
            else:
                print(msg)
            return result

        return wrapper

    if func is None:
        return decorator_timeit
    else:
        return decorator_timeit(func)
