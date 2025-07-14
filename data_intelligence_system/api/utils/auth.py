import os
import time
from typing import Optional, Union
import jwt
from fastapi import HTTPException, status
from data_intelligence_system.utils.logger import get_logger

logger = get_logger("api.auth")

# إعدادات
SECRET_KEY = os.getenv("JWT_SECRET_KEY")
if not SECRET_KEY or SECRET_KEY == "your_secret_key_123":
    raise RuntimeError("⚠️ يجب تعيين متغير البيئة JWT_SECRET_KEY بقيمة آمنة في بيئة الإنتاج!")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_SECONDS = 3600  # 1 ساعة

# تحميل مفاتيح API من متغير بيئة (يمكن استبداله بقاعدة بيانات أو ملف خارجي)
VALID_API_KEYS = set(os.getenv("VALID_API_KEYS", "super_api_key_001,admin_key_2025").split(","))


def create_access_token(
    data: dict,
    expires_delta: Optional[Union[int, "time.timedelta"]] = None
) -> str:
    """
    إنشاء رمز JWT مع فترة صلاحية.

    :param data: البيانات المراد تضمينها في التوكن (مثل معرف المستخدم).
    :param expires_delta: مدة الصلاحية (يمكن timedelta أو ثواني).
    :return: رمز JWT مشفر.
    """
    now = int(time.time())
    to_encode = data.copy()

    if expires_delta is None:
        expire_time = now + ACCESS_TOKEN_EXPIRE_SECONDS
    elif hasattr(expires_delta, "total_seconds"):
        expire_time = now + int(expires_delta.total_seconds())
    else:
        expire_time = now + int(expires_delta)

    to_encode.update({"exp": expire_time})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    logger.info("🛡️ تم إنشاء توكن JWT جديد")
    return encoded_jwt


def verify_token(token: str) -> dict:
    """
    التحقق من صحة رمز JWT وإرجاع بياناته.
    يحول استثناءات jwt إلى HTTPException.

    :param token: رمز JWT.
    :return: بيانات التوكن إذا كان صالحًا.
    :raises HTTPException: في حالة انتهاء الصلاحية أو عدم الصلاحية.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        logger.info("🛡️ تم التحقق من صحة التوكن JWT")
        return payload
    except jwt.ExpiredSignatureError:
        logger.warning("🚨 انتهت صلاحية التوكن JWT")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="انتهت صلاحية التوكن. الرجاء تسجيل الدخول مجددًا."
        )
    except jwt.InvalidTokenError:
        logger.warning("🚨 توكن JWT غير صالح")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="توكن غير صالح."
        )


def verify_api_key(api_key: str) -> bool:
    """
    تحقق من صحة API Key.

    :param api_key: مفتاح API.
    :raises HTTPException: إذا كان المفتاح غير مصرح به.
    :return: True إذا كان المفتاح صالحًا.
    """
    if api_key not in VALID_API_KEYS:
        logger.warning(f"🚫 محاولة وصول باستخدام API Key غير مصرح به: {api_key}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="API Key غير مصرح به"
        )
    logger.info("✅ تم التحقق من صحة API Key")
    return True
