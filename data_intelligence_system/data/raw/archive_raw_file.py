import os
import shutil
from datetime import datetime
import logging

# المسارات
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
RAW_DIR = os.path.join(BASE_DIR, 'data', 'raw')
ARCHIVE_DIR = os.path.join(RAW_DIR, "archived")

# إعداد اللوجر
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("data.raw.archive")

def archive_single_file(file_path: str) -> bool:
    """
    يقوم بأرشفة ملف واحد إلى مجلد archived مع إضافة طابع زمني.
    """
    if not os.path.exists(file_path):
        logger.warning(f"⚠️ الملف غير موجود: {file_path}")
        return False

    os.makedirs(ARCHIVE_DIR, exist_ok=True)
    filename = os.path.basename(file_path)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    archived_name = f"{timestamp}_{filename}"
    archived_path = os.path.join(ARCHIVE_DIR, archived_name)

    try:
        shutil.move(file_path, archived_path)
        logger.info(f"📦 تم أرشفة: {filename} → {archived_name}")
        return True
    except Exception as e:
        logger.error(f"❌ فشل في أرشفة {filename}: {e}")
        return False

def archive_file_with_metadata(file_path: str):
    """
    يؤرشف الملف المحدد وملف البيانات الوصفية المرتبط به إن وجد.
    """
    if archive_single_file(file_path):
        metadata_path = file_path.replace(os.path.splitext(file_path)[1], ".metadata.json")
        if os.path.exists(metadata_path):
            archive_single_file(metadata_path)

def main():
    """
    يبحث في مجلد raw/ ويؤرشف جميع الملفات (عدا سكربتات بايثون والمخفية).
    """
    logger.info("📁 بدء أرشفة الملفات المعالجة...\n")
    try:
        files = os.listdir(RAW_DIR)
    except Exception as e:
        logger.error(f"❌ تعذر قراءة مجلد raw/: {e}")
        return

    for file in files:
        full_path = os.path.join(RAW_DIR, file)
        if os.path.isfile(full_path) and not file.endswith(".py") and not file.startswith("."):
            archive_file_with_metadata(full_path)

    logger.info("\n✅ اكتملت عملية الأرشفة.")

if __name__ == "__main__":
    main()
