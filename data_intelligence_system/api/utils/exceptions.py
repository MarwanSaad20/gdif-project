# data_intelligence_system/api/utils/exceptions.py

from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from data_intelligence_system.utils.logger import get_logger

logger = get_logger("api.exceptions")


class CustomAppException(Exception):
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


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


def json_error_response(
    request: Request,
    status_code: int,
    detail: str,
    errors: dict | None = None
) -> JSONResponse:
    """
    دالة مساعدة لإنشاء ردود JSON متسقة عند الأخطاء.
    """
    content = {
        "detail": detail,
        "error": True,
        "path": str(request.url),
    }
    if errors:
        content["errors"] = errors

    return JSONResponse(
        status_code=status_code,
        content=content
    )


async def custom_exception_handler(request: Request, exc: CustomAppException) -> JSONResponse:
    logger.error(f"[{request.url}] ❌ {exc.message}")
    return json_error_response(
        request, exc.status_code, exc.message
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    logger.warning(f"[VALIDATION ERROR] {exc.errors()}")
    return json_error_response(
        request, 422, "❌ بيانات غير صالحة", errors=exc.errors()
    )


async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    logger.warning(f"[HTTP ERROR] {exc.detail}")
    return json_error_response(
        request, exc.status_code, exc.detail
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.error(f"[UNHANDLED EXCEPTION] {exc}", exc_info=True)
    return json_error_response(
        request, 500, "حدث خطأ غير متوقع في الخادم. الرجاء المحاولة لاحقًا."
    )
