# ===== تهيئة مسارات النظام أولًا =====
import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
PROJECT_PARENT = PROJECT_ROOT.parent

# إضافة المسار الجذري للمشروع (حيث يوجد data_intelligence_system) لضمان التكامل مع الاستيرادات المطلقة
sys.path[:0] = [str(PROJECT_ROOT), str(PROJECT_PARENT)]

# ===== تحميل متغيرات البيئة =====
from dotenv import load_dotenv
load_dotenv()

# ===== إعداد اللوجر =====
import logging

def setup_logging():
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)]
    )

setup_logging()
logger = logging.getLogger("GDIF")

# ===== استيراد الوحدات الحيوية مع التعامل مع أخطاء الاستيراد =====
from data_intelligence_system.etl.pipeline import run_full_pipeline
from data_intelligence_system.utils.file_manager import get_latest_processed_file
from data_intelligence_system.dashboard.app import app

# ===== تشغيل لوحة التحكم =====
def run_dashboard(debug=True, port=8050, reload=False, open_browser=True):
    import threading
    import webbrowser
    import time
    import urllib.request

    url = f"http://127.0.0.1:{port}"

    def wait_and_open_browser():
        for _ in range(10):
            try:
                with urllib.request.urlopen(url):
                    break
            except:
                time.sleep(1)
        logger.info(f"🌐 فتح المتصفح على: {url}")
        webbrowser.open(url)

    if open_browser:
        threading.Thread(target=wait_and_open_browser, daemon=True).start()

    if app is None:
        logger.error("❌ تطبيق Dash غير معرف. لا يمكن تشغيل لوحة التحكم.")
        sys.exit(1)

    app.run(debug=debug, port=port, use_reloader=reload, host="127.0.0.1")

# ===== نقطة الدخول =====
if __name__ == "__main__":
    logger.info("🚀 بدء تشغيل نظام GDIF ...")

    processed_dir = PROJECT_ROOT / "data" / "processed"
    os.makedirs(processed_dir, exist_ok=True)

    try:
        latest_file = get_latest_processed_file(processed_dir)
    except Exception as e:
        logger.error(f"❌ خطأ في الحصول على أحدث ملف معالج: {e}", exc_info=True)
        latest_file = None

    if latest_file and os.path.getsize(latest_file) > 0:
        logger.info("✅ تم العثور على بيانات سابقة. الانتقال مباشرة إلى لوحة التحكم.")
    else:
        logger.info("⚠️ لا توجد بيانات جاهزة، تشغيل ETL.")
        try:
            run_full_pipeline()
            latest_file = get_latest_processed_file(processed_dir)
        except Exception as e:
            logger.error(f"❌ فشل تنفيذ ETL أو لم يتم العثور على بيانات: {e}", exc_info=True)
            sys.exit(1)

        if not latest_file or os.path.getsize(latest_file) == 0:
            logger.error("❌ البيانات بعد ETL غير صالحة أو مفقودة.")
            sys.exit(1)

    # قراءة الإعدادات من البيئة أو الافتراضات
    port = int(os.getenv("DASHBOARD_PORT", 8050))
    debug = os.getenv("DASHBOARD_DEBUG", "true").lower() == "true"
    reload_flag = os.getenv("DASHBOARD_RELOAD", "false").lower() == "true"
    open_browser = os.getenv("DASHBOARD_OPEN_BROWSER", "true").lower() == "true"

    run_dashboard(debug, port, reload_flag, open_browser)
