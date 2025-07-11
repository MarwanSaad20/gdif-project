import importlib
import logging
import os
from types import SimpleNamespace
from typing import Any, Dict

# إعداد اللوجينغ المحلي
logger = logging.getLogger(__name__)
if not logger.hasHandlers():
    logging.basicConfig(level=logging.INFO)
    logger.setLevel(logging.INFO)

# 🧩 أسماء ملفات الإعداد المتوقعة داخل مجلد config/
CONFIG_MODULE_PATHS = {
    "paths": "data_intelligence_system.config.paths_config",
    "models": "data_intelligence_system.config.model_config",
    "reports": "data_intelligence_system.config.report_config",
    "dashboard": "data_intelligence_system.config.dashboard_config",
    "env": "data_intelligence_system.config.env_config"
}

def dictify(obj: Any) -> Dict[str, Any]:
    """تحويل كائن module أو Namespace إلى dict قابل للعرض والتعديل."""
    if isinstance(obj, dict):
        return obj
    return {
        key: getattr(obj, key)
        for key in dir(obj)
        if not key.startswith("__") and not callable(getattr(obj, key))
    }

def namespaceify(d: Dict[str, Any]) -> SimpleNamespace:
    """تحويل dict إلى كائن يمكن الوصول له بالنقطة dot access."""
    return SimpleNamespace(**d)

def safe_import(module_name: str) -> Any:
    """استيراد آمن لموديول إعدادات مع تسجيل الخطأ."""
    try:
        module = importlib.import_module(module_name)
        logger.info(f"✅ تم تحميل إعدادات: {module_name}")
        return module
    except Exception as e:
        logger.warning(f"⚠️ فشل تحميل إعدادات {module_name}: {e}")
        return SimpleNamespace()  # كائن فارغ لتفادي الانهيار

def setup_app_language(config_env: SimpleNamespace) -> None:
    """تعيين لغة التطبيق بناءً على متغير البيئة."""
    app_lang = os.getenv("APP_LANGUAGE", "ar").lower()
    if app_lang not in ["ar", "en"]:
        app_lang = "ar"
    setattr(config_env, "LANGUAGE", app_lang)

def setup_database_url(config_env: SimpleNamespace) -> None:
    """تعيين رابط قاعدة البيانات إذا لم يكن موجودًا."""
    if not hasattr(config_env, "DATABASE_URL"):
        default_db_url = os.getenv("DATABASE_URL", "sqlite:///default.db")
        setattr(config_env, "DATABASE_URL", default_db_url)

def setup_default_report_formats(config_reports: SimpleNamespace) -> None:
    """تعيين صيغ التقارير الافتراضية إذا لم تكن موجودة."""
    if not hasattr(config_reports, "OUTPUT_FORMATS"):
        setattr(config_reports, "OUTPUT_FORMATS", ["pdf", "html", "excel"])

# 📦 تحميل جميع الإعدادات في كائن مركزي CONFIG
CONFIG = SimpleNamespace()
for key, module_path in CONFIG_MODULE_PATHS.items():
    module_obj = safe_import(module_path)
    setattr(CONFIG, key, namespaceify(dictify(module_obj)))

# ⚙️ إعدادات إضافية
setup_app_language(CONFIG.env)
setup_database_url(CONFIG.env)
setup_default_report_formats(CONFIG.reports)

# 📌 للاستخدام المباشر:
# from config.config_loader import CONFIG
# print(CONFIG.paths.DATA_DIR)
