"""
config.py

ملف إعدادات شامل يدعم:
- واجهة لوحة التحكم (Dashboard)
- إعدادات عامة وتحكم في البيئة
- تحميل متغيرات البيئة من .env
- دعم المسارات الديناميكية حسب بنية المشروع
- تحميل إعدادات API وأمان وتسجيل وتحكم
"""

import os
import logging
from pathlib import Path
from dotenv import load_dotenv

# --- تحميل متغيرات البيئة ---
load_dotenv()

# --- إعداد بيئة التشغيل ---
ENV = os.getenv("ENV", "development").lower()
IS_DEV = ENV == "development"
DEBUG = IS_DEV

# --- إعدادات عامة ---
DEFAULT_LANGUAGE = os.getenv("DEFAULT_LANGUAGE", "ar")
THEME = os.getenv("THEME", "dark")
APP_NAME = os.getenv("APP_NAME", "نظام تحليل البيانات العام - GDIF")

# --- إعدادات الحجوم ---
try:
    PAGE_SIZE = int(os.getenv("PAGE_SIZE", 20))
except ValueError:
    PAGE_SIZE = 20

# --- إعداد المسارات الأساسية باستخدام pathlib ---
ROOT_DIR = Path(__file__).resolve().parent.parent

def _safe_path(env_var_name: str, default: Path) -> Path:
    """تحويل آمن للمسار من env أو default إلى كائن Path."""
    raw_value = os.getenv(env_var_name)
    if raw_value:
        return Path(raw_value)
    return default

DATA_DIR = _safe_path("DATA_DIR", ROOT_DIR / "data")
OUTPUT_DIR = _safe_path("OUTPUT_DIR", ROOT_DIR / "reports" / "generated")
TEMPLATE_DIR = _safe_path("TEMPLATE_DIR", ROOT_DIR / "reports" / "templates")
LOG_DIR = _safe_path("LOG_DIR", ROOT_DIR / "logs")

# --- التأكد من وجود المجلدات ---
for path in [DATA_DIR, OUTPUT_DIR, TEMPLATE_DIR, LOG_DIR]:
    try:
        path.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        logging.error(f"❌ فشل إنشاء المجلد '{path}': {e}")

# --- إعدادات API ---
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:5000/api").rstrip('/')

API_ENDPOINTS = {
    "get_data": f"{API_BASE_URL}/data",
    "get_profile": f"{API_BASE_URL}/profile",
    "run_model": f"{API_BASE_URL}/model/run",
    "get_report": f"{API_BASE_URL}/report",
}

# --- تحميل مفاتيح API ---
API_KEYS = {
    key[len("API_KEY_"):].lower(): value
    for key, value in os.environ.items()
    if key.startswith("API_KEY_")
}

# --- خيارات واجهة المستخدم ---
FILTER_OPTIONS = {
    "date_range": True,
    "categorical_filters": True,
    "numeric_range": True,
}

DATE_FORMATS = [
    "%Y-%m-%d",
    "%d/%m/%Y",
    "%d-%m-%Y",
]

# --- إعدادات اللوجنغ ---
LOG_LEVEL = os.getenv("LOG_LEVEL", "DEBUG" if IS_DEV else "INFO").upper()
LOG_FORMAT = os.getenv("LOG_FORMAT", "%(asctime)s - %(levelname)s - %(message)s")
LOG_LEVEL_VALUE = getattr(logging, LOG_LEVEL, logging.INFO)

logging.basicConfig(
    level=LOG_LEVEL_VALUE,
    format=LOG_FORMAT,
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(LOG_DIR / "dashboard.log", encoding="utf-8")
    ]
)

# --- إعدادات إضافية ---
RELOAD_ON_CHANGE = os.getenv("RELOAD_ON_CHANGE", "True").lower() in ("true", "1", "yes")

try:
    DATA_REFRESH_INTERVAL = int(os.getenv("DATA_REFRESH_INTERVAL", 300))
except ValueError:
    DATA_REFRESH_INTERVAL = 300

# --- دوال مساعدة ---

def get_api_endpoint(name: str) -> str:
    endpoint = API_ENDPOINTS.get(name)
    if endpoint is None:
        logging.warning(f"Requested API endpoint '{name}' not found.")
        return ""
    return endpoint

def get_date_format_preference() -> str:
    return DATE_FORMATS[0] if DATE_FORMATS else "%Y-%m-%d"

def get_log_level() -> int:
    return LOG_LEVEL_VALUE

# --- معلومات عند التشغيل المباشر ---
if __name__ == "__main__":
    print("="*50)
    print(f"""
🧠 تطبيق: {APP_NAME}
🌐 بيئة التشغيل: {ENV}
🎨 ثيم الواجهة: {THEME}
📁 مجلد البيانات: {DATA_DIR}
📁 مجلد القوالب: {TEMPLATE_DIR}
📁 مجلد التقارير: {OUTPUT_DIR}
📁 مجلد السجلات: {LOG_DIR}
🔐 مفاتيح API الموجودة: {list(API_KEYS.keys()) if API_KEYS else 'لا يوجد'}
🧪 نقاط API المتاحة: {list(API_ENDPOINTS.keys())}
🕒 فاصل تحديث البيانات: {DATA_REFRESH_INTERVAL} ثانية
🔄 إعادة تحميل عند التغيير: {RELOAD_ON_CHANGE}
""")
    print("="*50)
