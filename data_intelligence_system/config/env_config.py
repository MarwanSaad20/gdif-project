"""
ملف إعدادات البيئة (env_config.py)
تحميل متغيرات البيئة من ملف .env و config.yaml،
وتوفير إعدادات النظام بشكل مركزي لاستخدامها في النظام.
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from types import SimpleNamespace
from typing import Optional

from data_intelligence_system.utils.config_handler import ConfigHandler
from data_intelligence_system.utils.logger import get_logger

logger = get_logger("env_config")

BASE_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BASE_DIR / ".env"
CONFIG_PATH = BASE_DIR / "config" / "config.yaml"

if ENV_PATH.exists():
    load_dotenv(dotenv_path=ENV_PATH)
else:
    logger.warning("⚠️ ملف .env غير موجود. سيتم الاعتماد على متغيرات البيئة المباشرة.")

config = ConfigHandler(str(CONFIG_PATH)) if CONFIG_PATH.exists() else None


def get_env_var(key: str, default: Optional[str] = None, config_key: Optional[str] = None) -> str:
    """
    جلب قيمة من متغيرات البيئة أو من config.yaml مع قيمة افتراضية.
    """
    val = os.getenv(key)
    if val is not None:
        return val
    if config and config_key:
        val = config.get(config_key)
        if val is not None:
            return val
    return default


def ensure_path_exists(path: Path):
    try:
        path.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        logger.error(f"❌ فشل إنشاء المسار: {path} - {e}")


ENV_MODE = get_env_var("ENV_MODE", default="development", config_key="project.env_mode").lower()
DEBUG_MODE = get_env_var("DEBUG_MODE", default="true").lower() in ["1", "true", "yes"]

DEFAULT_LANG = get_env_var("DEFAULT_LANG", default="ar", config_key="project.language")
AUTHOR = get_env_var("AUTHOR", default="Marwan Al_Jubouri", config_key="project.author")
PROJECT_NAME = get_env_var("PROJECT_NAME", default="General Data Intelligence Framework", config_key="project.name")

SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
if not SECRET_KEY or SECRET_KEY.strip() == "" or SECRET_KEY == "dev-secret-key":
    logger.warning("⚠️ تحذير: لم يتم تعيين SECRET_KEY بشكل آمن. تأكد من ضبطه في ملف البيئة .env.")

RAW_DATA_PATH = Path(get_env_var("RAW_DATA_PATH", config_key="paths.raw_data", default=str(BASE_DIR / "data" / "raw")))
PROCESSED_DATA_PATH = Path(get_env_var("PROCESSED_DATA_PATH", config_key="paths.processed_data", default=str(BASE_DIR / "data" / "processed")))
REPORTS_OUTPUT_PATH = Path(get_env_var("REPORTS_OUTPUT_PATH", config_key="paths.reports", default=str(BASE_DIR / "reports" / "output")))

for p in [RAW_DATA_PATH, PROCESSED_DATA_PATH, REPORTS_OUTPUT_PATH]:
    ensure_path_exists(p)


def get_email_port() -> int:
    port_str = get_env_var("EMAIL_PORT", default="587")
    try:
        return int(port_str)
    except ValueError:
        logger.warning(f"⚠️ قيمة EMAIL_PORT غير صالحة '{port_str}'، سيتم استخدام 587 كافتراضي.")
        return 587


EMAIL_CONFIG = {
    "sender": get_env_var("EMAIL_SENDER", default="your@email.com"),
    "password": get_env_var("EMAIL_PASSWORD", default=""),
    "smtp_server": get_env_var("EMAIL_SMTP", default="smtp.gmail.com"),
    "port": get_email_port(),
}

if not EMAIL_CONFIG["password"]:
    logger.warning("⚠️ تحذير: لم يتم تعيين كلمة مرور البريد الإلكتروني. لن تتمكن من إرسال تقارير عبر البريد.")


def determine_language(app_lang: str, default_lang: str) -> str:
    lang = app_lang.lower()
    return lang if lang in ["ar", "en"] else default_lang.lower()


APP_LANGUAGE = os.getenv("APP_LANGUAGE", DEFAULT_LANG)
LANGUAGE = determine_language(APP_LANGUAGE, DEFAULT_LANG)

DATABASE_URL = get_env_var("DATABASE_URL", config_key="database.url", default="sqlite:///default.db")

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
