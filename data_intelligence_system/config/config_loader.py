import importlib
import logging
import os
from types import SimpleNamespace

# إعداد اللوجينغ المحلي
logger = logging.getLogger(__name__)
if not logger.handlers:
    logging.basicConfig(level=logging.INFO)
    logger.setLevel(logging.INFO)

# 🧩 أسماء ملفات الإعداد المتوقعة داخل مجلد config/
CONFIG_MODULES = {
    "paths": "config.paths_config",
    "models": "config.model_config",
    "reports": "config.report_config",
    "dashboard": "config.dashboard_config",
    "env": "config.env_config"
}

def dictify(obj: object) -> dict:
    """تحويل كائن module أو Namespace إلى dict قابل للعرض والتعديل."""
    if isinstance(obj, dict):
        return obj
    return {
        key: getattr(obj, key)
        for key in dir(obj)
        if not key.startswith("__") and not callable(getattr(obj, key))
    }

def namespaceify(d: dict) -> SimpleNamespace:
    """تحويل dict إلى كائن يمكن الوصول له بالنقطة dot access."""
    return SimpleNamespace(**d)

def safe_import(module_name: str):
    """استيراد آمن لموديول إعدادات مع تسجيل الخطأ."""
    try:
        module = importlib.import_module(module_name)
        logger.info(f"✅ تم تحميل إعدادات: {module_name}")
        return module
    except Exception as e:
        logger.warning(f"⚠️ فشل تحميل إعدادات {module_name}: {e}")
        return SimpleNamespace()  # كائن فارغ لتفادي الانهيار

# 📦 تحميل جميع الإعدادات في كائن مركزي CONFIG
CONFIG = SimpleNamespace()
for key, module_path in CONFIG_MODULES.items():
    module_obj = safe_import(module_path)
    setattr(CONFIG, key, namespaceify(dictify(module_obj)))

# === تعديل خاصية اللغة في CONFIG.env بناء على متغير البيئة APP_LANGUAGE ===
app_lang = os.getenv("APP_LANGUAGE", "ar").lower()
if app_lang not in ["ar", "en"]:
    app_lang = "ar"
setattr(CONFIG.env, "LANGUAGE", app_lang)

# === إضافة OUTPUT_FORMATS إذا لم تكن موجودة في CONFIG.reports ===
if not hasattr(CONFIG.reports, "OUTPUT_FORMATS"):
    setattr(CONFIG.reports, "OUTPUT_FORMATS", ["pdf", "html", "excel"])

# === إضافة DATABASE_URL بقيمة افتراضية إذا لم تكن موجودة في CONFIG.env ===
if not hasattr(CONFIG.env, "DATABASE_URL"):
    default_db_url = os.getenv("DATABASE_URL", "sqlite:///default.db")
    setattr(CONFIG.env, "DATABASE_URL", default_db_url)

# 📌 للاستخدام المباشر:
# from config.config_loader import CONFIG
# print(CONFIG.paths.DATA_DIR)
