# data_intelligence_system/api/utils/exceptions.py

from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

# ✅ استيراد اللوجر الموحد من الجذر
from data_intelligence_system.utils.logger import get_logger

# ✅ تهيئة اللوجر باسم مخصص للوحدة
logger = get_logger("api.exceptions")

# ✅ استثناء مخصص عام
class CustomAppException(Exception):
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(message)

# 📌 استثناءات محددة
class FileNotFoundAppException(CustomAppException):
    """استثناء عند عدم العثور على الملف"""
    def __init__(self, filename: str):
        super().__init__(f"❌ الملف غير موجود: {filename}", status_code=404)

class AnalysisFailedException(CustomAppException):
    """استثناء في حالة فشل تحليل البيانات"""
    def __init__(self, reason: str = "تحليل البيانات فشل"):
        super().__init__(f"⚠️ فشل التحليل: {reason}", status_code=500)

class AuthFailedException(CustomAppException):
    """استثناء فشل المصادقة"""
    def __init__(self):
        super().__init__("⚠️ المصادقة فشلت، تحقق من صلاحياتك", status_code=401)

# 🎯 معالج استثناءات عام
async def custom_exception_handler(request: Request, exc: CustomAppException) -> JSONResponse:
    logger.error(f"[{request.url}] ❌ {exc.message}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.message,
            "error": True,
            "path": str(request.url),
        }
    )

# 🧪 معالج استثناءات FastAPI الأصلية (مثل أخطاء التحقق)
async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    logger.warning(f"[VALIDATION ERROR] {exc.errors()}")
    return JSONResponse(
        status_code=422,
        content={
            "detail": "❌ بيانات غير صالحة",
            "errors": exc.errors(),
            "error": True,
            "path": str(request.url),
        }
    )

# 🧱 معالج HTTPExceptions الافتراضية
async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    logger.warning(f"[HTTP ERROR] {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "error": True,
            "path": str(request.url),
        }
    )

# 🛑 معالج استثناء عام غير متوقع (اختياري لكن موصى به)
async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.error(f"[UNHANDLED EXCEPTION] {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "حدث خطأ غير متوقع في الخادم",
            "error": True,
            "path": str(request.url),
        }
    )
