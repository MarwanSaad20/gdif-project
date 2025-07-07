import schedule
import time
import subprocess
from pathlib import Path
import sys
from datetime import datetime
import os

# 📁 إعداد المسارات
BASE_DIR = Path(__file__).resolve().parent
FETCH_API_SCRIPT = BASE_DIR / "fetch_api_data.py"
LOAD_FILES_SCRIPT = BASE_DIR / "load_external_files.py"
LOG_FILE = BASE_DIR / "update_external_data.log"

def log(message: str, level: str = "INFO"):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] [{level}] {message}"
    print(log_entry)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(log_entry + "\n")

def run_script(script_path: Path):
    if not script_path.exists():
        log(f"❌ السكربت غير موجود: {script_path}", level="ERROR")
        return

    log(f"🚀 بدء تشغيل: {script_path.name}")
    try:
        result = subprocess.run(
            [sys.executable, str(script_path)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            encoding="utf-8",
            timeout=300
        )
        if result.returncode == 0:
            log(f"✅ تم تنفيذ {script_path.name} بنجاح.")
        else:
            log(f"❌ خطأ في {script_path.name}:\n{result.stderr}", level="ERROR")
    except subprocess.TimeoutExpired:
        log(f"⏰ السكربت {script_path.name} تجاوز الوقت المحدد.", level="WARNING")
    except Exception as e:
        log(f"⚠️ استثناء غير متوقع في {script_path.name}: {e}", level="ERROR")

def job():
    log("🔄 بدء عملية تحديث البيانات الخارجية")
    run_script(FETCH_API_SCRIPT)
    if LOAD_FILES_SCRIPT.exists():
        run_script(LOAD_FILES_SCRIPT)
    else:
        log("⚠️ ملف load_external_files.py غير موجود - تم التخطي", level="WARNING")
    log("✅ انتهاء عملية التحديث الخارجية\n" + "-" * 50)

def main():
    update_time = os.getenv("EXTERNAL_UPDATE_TIME", "02:00")
    schedule.every().day.at(update_time).do(job)
    log(f"📅 تم جدولة عملية التحديث اليومية الساعة {update_time}")

    # تنفيذ مباشر أول مرة
    job()

    while True:
        schedule.run_pending()
        time.sleep(30)

if __name__ == "__main__":
    main()
