import logging
import os
from typing import Optional
from sqlalchemy import create_engine
import uvicorn
from data_intelligence_system.config.env_config import env_namespace
from data_intelligence_system.utils.logger import setup_logger

# إعداد التسجيل
logger = setup_logger(__name__)

def load_uvicorn_config() -> dict:
    """
    تحميل إعدادات Uvicorn من env_namespace أو متغيرات البيئة مع التحقق من صحتها.

    Returns:
        dict: إعدادات Uvicorn (host, port, reload, log_level, workers).
    
    Raises:
        ValueError: إذا كانت الإعدادات غير صالحة.
    """
    try:
        config = {
            "host": os.getenv("API_HOST", env_namespace.get("API_HOST", "127.0.0.1")),
            "port": int(os.getenv("API_PORT", env_namespace.get("API_PORT", 8000))),
            "reload": os.getenv("API_RELOAD", env_namespace.get("API_RELOAD", "true")).lower() == "true",
            "log_level": os.getenv("API_LOG_LEVEL", env_namespace.get("API_LOG_LEVEL", "info")),
            "workers": int(os.getenv("API_WORKERS", env_namespace.get("API_WORKERS", 1)))
        }
        
        # التحقق من صحة الإعدادات
        if not isinstance(config["port"], int) or config["port"] < 1024 or config["port"] > 65535:
            raise ValueError("API_PORT يجب أن يكون عددًا صحيحًا بين 1024 و 65535")
        if config["log_level"] not in ["debug", "info", "warning", "error", "critical"]:
            raise ValueError("API_LOG_LEVEL يجب أن يكون أحد القيم: debug, info, warning, error, critical")
        if config["workers"] < 1:
            raise ValueError("API_WORKERS يجب أن يكون عددًا صحيحًا أكبر من 0")
        
        return config
    except (ValueError, TypeError) as e:
        logger.error(f"خطأ في تحميل إعدادات Uvicorn: {str(e)}")
        raise

def check_dependencies() -> None:
    """
    التحقق من توفر الاعتمادات الأساسية (مثل قاعدة البيانات) قبل تشغيل السيرفر.

    Raises:
        RuntimeError: إذا فشل التحقق من الاعتمادات.
    """
    try:
        db_url = env_namespace.get("DATABASE_URL")
        if db_url:
            engine = create_engine(db_url)
            with engine.connect() as connection:
                logger.info("الاتصال بقاعدة البيانات ناجح")
        else:
            logger.warning("لم يتم العثور على DATABASE_URL، قد لا تكون قاعدة البيانات مطلوبة")
    except Exception as e:
        logger.error(f"فشل التحقق من الاعتمادات: {str(e)}")
        raise RuntimeError(f"فشل التحقق من الاعتمادات: {str(e)}")

def main() -> None:
    """
    نقطة تشغيل تطبيق FastAPI باستخدام Uvicorn.
    يقوم بتحميل الإعدادات والتحقق من الاعتمادات قبل التشغيل.
    """
    try:
        # التحقق من الاعتمادات
        check_dependencies()
        
        # تحميل الإعدادات
        config = load_uvicorn_config()
        
        # تشغيل السيرفر
        logger.info(f"تشغيل تطبيق FastAPI على {config['host']}:{config['port']}")
        uvicorn.run(
            "data_intelligence_system.api.app:app",
            host=config["host"],
            port=config["port"],
            reload=config["reload"],
            log_level=config["log_level"],
            workers=config["workers"]
        )
    except (ValueError, RuntimeError) as e:
        logger.error(f"خطأ أثناء تشغيل التطبيق: {str(e)}")
        raise
    except Exception as e:
        logger.critical(f"خطأ غير متوقع أثناء تشغيل التطبيق: {str(e)}")
        raise

if __name__ == "__main__":
    main()