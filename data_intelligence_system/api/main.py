import uvicorn
import os
from dotenv import load_dotenv

# تحميل متغيرات البيئة من ملف .env إن وجد
load_dotenv()

def main():
    """
    نقطة تشغيل تطبيق FastAPI باستخدام Uvicorn.
    يدعم التهيئة الديناميكية عبر متغيرات البيئة.
    """
    try:
        # إعدادات التشغيل مع قيم افتراضية
        host = os.getenv("API_HOST", "127.0.0.1")
        port = int(os.getenv("API_PORT", 8000))
        reload = os.getenv("API_RELOAD", "true").lower() == "true"
        log_level = os.getenv("API_LOG_LEVEL", "info")
        workers = int(os.getenv("API_WORKERS", 1))

        # تشغيل خادم Uvicorn مع الإعدادات
        uvicorn.run(
            "data_intelligence_system.api.app:app",  # مسار الاستيراد من جذر المشروع
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
