import os
from pathlib import Path
from dotenv import load_dotenv
from types import SimpleNamespace

# ✅ استيراد ConfigHandler و logger
from data_intelligence_system.utils.config_handler import ConfigHandler
from data_intelligence_system.utils.logger import get_logger

logger = get_logger("env_config")

# ===================== تحميل ملف .env من الجذر =====================
BASE_DIR = Path(__file__).resolve().parent.parent
env_path = BASE_DIR / ".env"

if env_path.exists():
    load_dotenv(dotenv_path=env_path)
else:
    logger.warning("⚠️ ملف .env غير موجود. سيتم الاعتماد على متغيرات البيئة المباشرة.")

# ===================== تحميل إعدادات config.yaml إن وجد =====================
config_path = BASE_DIR / "config" / "config.yaml"
config = ConfigHandler(str(config_path)) if config_path.exists() else None

# ===================== إعدادات بيئة التشغيل =====================
ENV_MODE = os.getenv("ENV_MODE") or (config.get("project.env_mode", default="development") if config else "development")
ENV_MODE = ENV_MODE.lower()
DEBUG_MODE = (os.getenv("DEBUG_MODE") or "true").lower() in ["1", "true", "yes"]

# ===================== إعدادات عامة =====================
DEFAULT_LANG = os.getenv("DEFAULT_LANG") or (config.get("project.language", default="ar") if config else "ar")
AUTHOR = os.getenv("AUTHOR") or (config.get("project.author", default="Marwan Al_Jubouri") if config else "Marwan Al_Jubouri")
PROJECT_NAME = os.getenv("PROJECT_NAME") or (config.get("project.name", default="General Data Intelligence Framework") if config else "General Data Intelligence Framework")

# ===================== إعدادات أمنية =====================
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
if not SECRET_KEY or SECRET_KEY.strip() == "" or SECRET_KEY == "dev-secret-key":
    logger.warning("⚠️ تحذير: لم يتم تعيين SECRET_KEY بشكل آمن. تأكد من ضبطه في ملف البيئة .env.")

# ===================== إعدادات المسارات =====================
RAW_DATA_PATH = Path(os.getenv("RAW_DATA_PATH") or (config.get("paths.raw_data", default=BASE_DIR / "data" / "raw") if config else BASE_DIR / "data" / "raw"))
PROCESSED_DATA_PATH = Path(os.getenv("PROCESSED_DATA_PATH") or (config.get("paths.processed_data", default=BASE_DIR / "data" / "processed") if config else BASE_DIR / "data" / "processed"))
REPORTS_OUTPUT_PATH = Path(os.getenv("REPORTS_OUTPUT_PATH") or (config.get("paths.reports", default=BASE_DIR / "reports" / "output") if config else BASE_DIR / "reports" / "output"))

for path in [RAW_DATA_PATH, PROCESSED_DATA_PATH, REPORTS_OUTPUT_PATH]:
    try:
        path.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        logger.error(f"❌ فشل إنشاء المسار: {path} - {e}")

# ===================== إعدادات البريد =====================
EMAIL_CONFIG = {
    "sender": os.getenv("EMAIL_SENDER", "your@email.com"),
    "password": os.getenv("EMAIL_PASSWORD", ""),
    "smtp_server": os.getenv("EMAIL_SMTP", "smtp.gmail.com"),
    "port": int(os.getenv("EMAIL_PORT", 587)),
}

if not EMAIL_CONFIG["password"]:
    logger.warning("⚠️ تحذير: لم يتم تعيين كلمة مرور البريد الإلكتروني. لن تتمكن من إرسال تقارير عبر البريد.")

# ===================== إعداد اللغة =====================
_app_language = os.getenv("APP_LANGUAGE", DEFAULT_LANG).lower()
LANGUAGE = _app_language if _app_language in ["ar", "en"] else "ar"

# ===================== إعداد قاعدة البيانات =====================
DATABASE_URL = os.getenv("DATABASE_URL") or (config.get("database.url", default="sqlite:///default.db") if config else "sqlite:///default.db")

# ===================== تجهيز Namespace للإرجاع =====================
env_namespace = SimpleNamespace(
    ENV_MODE=ENV_MODE,
    DEBUG_MODE=DEBUG_MODE,
    DEFAULT_LANG=DEFAULT_LANG,
    LANGUAGE=LANGUAGE,
    AUTHOR=AUTHOR,
    PROJECT_NAME=PROJECT_NAME,
    SECRET_KEY=SECRET_KEY,
    RAW_DATA_PATH=RAW_DATA_PATH,
    PROCESSED_DATA_PATH=PROCESSED_DATA_PATH,
    REPORTS_OUTPUT_PATH=REPORTS_OUTPUT_PATH,
    EMAIL_CONFIG=EMAIL_CONFIG,
    DATABASE_URL=DATABASE_URL,
)

# ================ للإمكانية الاستيراد كـ config.env =================
if __name__ == "__main__":
    print("📌 إعدادات النظام الحالية:")
    print(f"📍 نمط البيئة: {ENV_MODE}")
    print(f"🧪 وضع التصحيح: {DEBUG_MODE}")
    print(f"🔑 مفتاح الأمان مضبوط: {'نعم' if SECRET_KEY and SECRET_KEY != 'dev-secret-key' else 'لا'}")
    print(f"🧾 اسم المشروع: {PROJECT_NAME}")
    print(f"📂 بيانات خام: {RAW_DATA_PATH}")
    print(f"📂 بيانات معالجة: {PROCESSED_DATA_PATH}")
    print(f"📂 تقارير: {REPORTS_OUTPUT_PATH}")
    print(f"📧 بريد الإرسال: {EMAIL_CONFIG['sender']} (مفتاح مفقود: {'نعم' if not EMAIL_CONFIG['password'] else 'لا'})")
    print(f"🌐 اللغة الحالية: {LANGUAGE}")
    print(f"🗄️ DATABASE_URL: {DATABASE_URL}")
