import os
from pathlib import Path
from dotenv import load_dotenv
from types import SimpleNamespace

# ===================== تحميل ملف .env من الجذر =====================
BASE_DIR = Path(__file__).resolve().parent.parent
env_path = BASE_DIR / ".env"

if env_path.exists():
    load_dotenv(dotenv_path=env_path)
else:
    print("⚠️ ملف .env غير موجود. سيتم الاعتماد على متغيرات البيئة المباشرة.")

# ===================== إعدادات بيئة التشغيل =====================
ENV_MODE = os.getenv("ENV_MODE", "development").lower()  # development | production | testing
DEBUG_MODE = os.getenv("DEBUG_MODE", "true").lower() in ["1", "true", "yes"]

# ===================== إعدادات عامة =====================
DEFAULT_LANG = os.getenv("DEFAULT_LANG", "ar")
AUTHOR = os.getenv("AUTHOR", "Marwan Al_Jubouri")
PROJECT_NAME = os.getenv("PROJECT_NAME", "General Data Intelligence Framework")

# ===================== إعدادات أمنية =====================
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
if not SECRET_KEY or SECRET_KEY.strip() == "" or SECRET_KEY == "dev-secret-key":
    print("⚠️ تحذير: لم يتم تعيين SECRET_KEY بشكل آمن. تأكد من ضبطه في ملف البيئة .env.")

# ===================== إعدادات المسارات =====================
RAW_DATA_PATH = Path(os.getenv("RAW_DATA_PATH", BASE_DIR / "data" / "raw"))
PROCESSED_DATA_PATH = Path(os.getenv("PROCESSED_DATA_PATH", BASE_DIR / "data" / "processed"))
REPORTS_OUTPUT_PATH = Path(os.getenv("REPORTS_OUTPUT_PATH", BASE_DIR / "reports" / "output"))

for path in [RAW_DATA_PATH, PROCESSED_DATA_PATH, REPORTS_OUTPUT_PATH]:
    try:
        path.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        print(f"❌ فشل إنشاء المسار: {path} - {e}")

# ===================== إعدادات البريد =====================
EMAIL_CONFIG = {
    "sender": os.getenv("EMAIL_SENDER", "your@email.com"),
    "password": os.getenv("EMAIL_PASSWORD", ""),
    "smtp_server": os.getenv("EMAIL_SMTP", "smtp.gmail.com"),
    "port": int(os.getenv("EMAIL_PORT", 587)),
}

if not EMAIL_CONFIG["password"]:
    print("⚠️ تحذير: لم يتم تعيين كلمة مرور البريد الإلكتروني. لن تتمكن من إرسال تقارير عبر البريد.")

# ===================== إعداد اللغة =====================
_app_language = os.getenv("APP_LANGUAGE", DEFAULT_LANG).lower()
LANGUAGE = _app_language if _app_language in ["ar", "en"] else "ar"

# ===================== إضافة DATABASE_URL =====================
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///default.db")  # قيمة افتراضية لتجنب فشل الاختبارات

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
    DATABASE_URL=DATABASE_URL,  # أضفنا هذا السطر
)

# ================ لإمكانية الاستيراد كـ config.env =================
# عند استيراد هذا الملف، استورد env_namespace فقط
# في config_loader.py يمكنك عمل: env = config.env_config.env_namespace

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
