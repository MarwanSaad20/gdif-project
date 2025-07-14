from fastapi import Depends, Header, HTTPException, Request, status
from sqlalchemy.orm import Session
from typing import Generator, Dict, Optional, Any
import time

from data_intelligence_system.api.utils.auth import verify_token as verify_jwt_token, verify_api_key
from data_intelligence_system.database.session import get_db_session
from data_intelligence_system.utils.logger import get_logger

logger = get_logger("api.dependencies")


def get_db() -> Generator[Session, None, None]:
    """
    إنشاء جلسة قاعدة بيانات قابلة للاستخدام عبر yield.
    يغلق الجلسة تلقائيًا بعد الانتهاء.
    """
    db = get_db_session()
    try:
        yield db
    finally:
        db.close()


def get_current_user(authorization: Optional[str] = Header(None)) -> Dict[str, Any]:
    """
    استخراج بيانات المستخدم من توكن JWT في رأس Authorization.
    يتحقق من وجود وتنسيق التوكن.
    """
    if authorization is None:
        logger.warning("🛑 Authorization header missing")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header missing",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not authorization.startswith("Bearer "):
        logger.warning("🛑 Invalid authorization header format")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = authorization[len("Bearer "):]
    logger.info("🔐 محاولة التحقق من JWT Token")
    return verify_jwt_token(token)


rate_limit_store: Dict[str, list[int]] = {}


def rate_limiter(request: Request, max_requests: int = 100, window_seconds: int = 60) -> None:
    """
    تحديد معدل الوصول (rate limiting) مؤقت بالذاكرة.
    يحظر الطلبات بعد تجاوز الحد خلال النافذة الزمنية.

    :param request: طلب HTTP.
    :param max_requests: الحد الأقصى للطلبات المسموح بها.
    :param window_seconds: طول نافذة القياس بالثواني.
    :raises HTTPException: إذا تم تجاوز الحد.
    """
    client_ip = request.client.host
    current_time = int(time.time())

    if client_ip not in rate_limit_store:
        rate_limit_store[client_ip] = []

    # تنظيف الطلبات القديمة
    rate_limit_store[client_ip] = [
        t for t in rate_limit_store[client_ip] if current_time - t < window_seconds
    ]

    if len(rate_limit_store[client_ip]) >= max_requests:
        logger.warning(f"🚨 تم تجاوز الحد المسموح للطلبات من IP: {client_ip}")
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="🚫 تم تجاوز الحد المسموح من الطلبات"
        )

    rate_limit_store[client_ip].append(current_time)


def api_key_header(api_key: Optional[str] = Header(None)) -> str:
    """
    تحقق من صلاحية API Key الموجود في رأس الطلب.

    :param api_key: مفتاح API من الرأس.
    :raises HTTPException: إذا كان المفتاح غير موجود أو غير صالح.
    :return: المفتاح نفسه إذا كان صالحًا.
    """
    if api_key is None:
        logger.warning("🛑 API Key header missing")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API Key header missing"
        )
    logger.info("🔑 محاولة التحقق من API Key")
    verify_api_key(api_key)
    return api_key
