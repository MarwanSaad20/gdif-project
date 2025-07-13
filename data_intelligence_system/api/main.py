import uvicorn
import os

# ✅ استيراد الإعدادات البيئية المركزية بدلًا من التحميل اليدوي
from data_intelligence_system.config.env_config import env_namespace

def main():
    """
    نقطة تشغيل تطبيق FastAPI باستخدام Uvicorn.
    يدعم التهيئة الديناميكية عبر env_namespace أو متغيرات البيئة مباشرة.
    """
    try:
        # إعدادات التشغيل مع قيم افتراضية
        host = os.getenv("API_HOST", "127.0.0.1")
        port = int(os.getenv("API_PORT", 8000))
        reload = os.getenv("API_RELOAD", "true").lower() == "true"
        log_level = os.getenv("API_LOG_LEVEL", "info")
        workers = int(os.getenv("API_WORKERS", 1))

        uvicorn.run(
            "data_intelligence_system.api.app:app",  # مسار الاستيراد المطلق
            host=host,
            port=port,
            reload=reload,
            log_level=log_level,
            workers=workers
        )
    except Exception as e:
        print(f"❌ خطأ أثناء تشغيل التطبيق: {e}")

if __name__ == "__main__":
    main()
