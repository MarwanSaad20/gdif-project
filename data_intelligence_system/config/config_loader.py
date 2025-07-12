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
    """تحويل module أو Namespace إلى dict."""
    try:
        return vars(obj)
    except TypeError:
        return {
            key: getattr(obj, key)
            for key in dir(obj)
            if not key.startswith("__") and not callable(getattr(obj, key))
        }

def namespaceify(d: Dict[str, Any]) -> SimpleNamespace:
    """تحويل dict إلى Namespace لإتاحة dot access."""
    return SimpleNamespace(**d)

def safe_import(module_name: str) -> Any:
    """استيراد آمن لموديول إعدادات مع تسجيل الخطأ."""
    try:
        module = importlib.import_module(module_name)
        logger.info(f"✅ تم تحميل إعدادات: {module_name}")
        return module
    except Exception as e:
        logger.warning(f"⚠️ فشل تحميل إعدادات {module_name}: {e}", exc_info=True)
        return SimpleNamespace()

def setup_defaults(config: SimpleNamespace) -> None:
    """تعيين الإعدادات الافتراضية العامة."""
    # لغة التطبيق
    app_lang = os.getenv("APP_LANGUAGE", "ar").strip().lower()
    if app_lang not in {"ar", "en"}:
        app_lang = "ar"
    setattr(config.env, "LANGUAGE", app_lang)

    # قاعدة البيانات
    db_url = os.getenv("DATABASE_URL", "sqlite:///default.db").strip()
    if not getattr(config.env, "DATABASE_URL", "").strip():
        setattr(config.env, "DATABASE_URL", db_url)

    # صيغ التقارير
    if not hasattr(config.reports, "OUTPUT_FORMATS"):
        setattr(config.reports, "OUTPUT_FORMATS", ["pdf", "html", "excel"])

# 📦 تحميل جميع الإعدادات في كائن مركزي CONFIG
CONFIG = SimpleNamespace()
for key, module_path in CONFIG_MODULE_PATHS.items():
    module_obj = safe_import(module_path)
    setattr(CONFIG, key, namespaceify(dictify(module_obj)))

# ⚙️ إعدادات إضافية
setup_defaults(CONFIG)

# 📌 للاستخدام المباشر:
# from config.config_loader import CONFIG
# print(CONFIG.paths.DATA_DIR)
