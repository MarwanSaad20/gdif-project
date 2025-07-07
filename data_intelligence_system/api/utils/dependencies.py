from fastapi import Depends, Header, HTTPException, Request, status
from sqlalchemy.orm import Session
from typing import Generator, Dict, Optional
import time

# ✅ استيراد محدث من الجذر
from data_intelligence_system.api.utils.auth import verify_token as verify_jwt_token, verify_api_key
from data_intelligence_system.database.session import get_db_session
from data_intelligence_system.utils.logger import get_logger

# ✅ إعداد اللوقر الموحد
logger = get_logger("api.dependencies")

# ==========================
# قاعدة بيانات: جلسة DB
# ==========================
def get_db() -> Generator[Session, None, None]:
    db = get_db_session()
    try:
        yield db
    finally:
        db.close()

# ==========================
# استخراج المستخدم الحالي من JWT
# ==========================
def get_current_user(authorization: Optional[str] = Header(None)) -> Dict:
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

# ==========================
# تحديد معدل الوصول (مؤقت - لا يستخدم في الإنتاج)
# ==========================
rate_limit_store = {}

def rate_limiter(request: Request, max_requests: int = 100, window_seconds: int = 60):
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

# ==========================
# التحقق من API Key (استخدام دالة من auth.py)
# ==========================
def api_key_header(api_key: Optional[str] = Header(None)):
    if api_key is None:
        logger.warning("🛑 API Key header missing")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API Key header missing"
        )
    logger.info("🔑 محاولة التحقق من API Key")
    verify_api_key(api_key)
    return api_key
