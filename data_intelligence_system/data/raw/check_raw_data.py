import os
import pandas as pd
import json
from datetime import datetime
import logging

# 🔧 المسارات الرئيسية
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
RAW_DIR = os.path.join(BASE_DIR, 'data', 'raw')
LOG_DIR = os.path.join(BASE_DIR, 'logs')
os.makedirs(LOG_DIR, exist_ok=True)

# 🔖 إعدادات السجل
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
CSV_LOG_PATH = os.path.join(LOG_DIR, f'raw_check_log_{timestamp}.csv')
TXT_LOG_PATH = os.path.join(LOG_DIR, 'raw_data_check.log')

# 🛠️ تهيئة السجلات
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(TXT_LOG_PATH, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("RawDataCheck")

SUPPORTED_EXTENSIONS = ['.csv', '.json', '.xlsx']

def log_entry(filename, status, message, rows=0, cols=0, missing=0):
    return {
        'filename': filename,
        'status': status,
        'message': message,
        'rows': rows,
        'columns': cols,
        'num_missing_values': missing,
        'checked_at': datetime.now().isoformat()
    }

def read_file(filepath):
    ext = os.path.splitext(filepath)[1].lower()
    try:
        if ext == '.csv':
            return pd.read_csv(filepath, encoding='utf-8')
        elif ext == '.json':
            try:
                return pd.read_json(filepath, lines=True)
            except ValueError:
                with open(filepath, encoding='utf-8') as f:
                    return pd.json_normalize(json.load(f))
        elif ext == '.xlsx':
            return pd.read_excel(filepath)
        else:
            raise ValueError(f"Unsupported file type: {ext}")
    except Exception as e:
        raise ValueError(f"Failed to read {ext} file: {e}")

def main():
    logger.info("🔍 بدء فحص ملفات البيانات الخام...")
    logs = []

    if not os.path.exists(RAW_DIR):
        logger.error(f"❌ مجلد البيانات الخام غير موجود: {RAW_DIR}")
        return

    for root, _, files in os.walk(RAW_DIR):
        for file in files:
            ext = os.path.splitext(file)[1].lower()
            path = os.path.join(root, file)

            if not os.path.isfile(path) or ext not in SUPPORTED_EXTENSIONS:
                logger.info(f"⏩ تجاهل ملف غير مدعوم أو غير ملف عادي: {file}")
                continue

            file_size = os.path.getsize(path)
            if file_size == 0:
                logger.warning(f"⚠️ الملف فارغ (0 بايت): {file}")
                logs.append(log_entry(file, 'EMPTY', 'Empty file (0 bytes)'))
                continue

            try:
                file_size_mb = file_size / (1024 * 1024)
                if file_size_mb > 100:
                    logger.warning(f"⚠️ الملف كبير جداً ({file_size_mb:.2f} MB): {file}")

                df = read_file(path)
                rows, cols = df.shape
                missing = df.isnull().sum().sum()

                logs.append(log_entry(file, 'OK', 'Loaded successfully', rows, cols, missing))
                logger.info(f"✅ {file} ({rows} صفوف، {cols} أعمدة، {missing} قيم مفقودة)")

            except Exception as e:
                logs.append(log_entry(file, 'FAIL', str(e)))
                logger.error(f"❌ فشل تحميل الملف {file}: {e}")

    try:
        pd.DataFrame(logs).to_csv(CSV_LOG_PATH, index=False, encoding='utf-8')
        logger.info(f"✅ تم حفظ سجل الفحص في: {CSV_LOG_PATH}")
    except Exception as e:
        logger.error(f"❌ فشل حفظ سجل الفحص: {e}")

if __name__ == "__main__":
    main()
