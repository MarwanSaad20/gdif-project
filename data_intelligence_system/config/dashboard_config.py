from pathlib import Path
from data_intelligence_system.utils.config_handler import ConfigHandler
from data_intelligence_system.utils.logger import get_logger

# ✅ إعداد اللوجر
logger = get_logger("dashboard_config")

# ✅ تحميل الإعدادات من ملف YAML
config_path = Path(__file__).resolve().parent / "config.yaml"
try:
    _config = ConfigHandler(str(config_path))
    logger.info(f"✅ تم تحميل إعدادات لوحة التحكم من: {config_path}")
except Exception as e:
    logger.warning(f"⚠️ فشل تحميل إعدادات لوحة التحكم: {e}")
    _config = None

# 🎯 عنوان النظام
DASHBOARD_TITLE = "لوحة تحكم تحليل البيانات العام – GDIF"

# 🌐 إعدادات الواجهة من الملف
DEFAULT_LANGUAGE = _config.get("project.language", default="ar") if _config else "ar"
DEFAULT_THEME = _config.get("dashboard.theme", default="dark") if _config else "dark"
REFRESH_INTERVAL = _config.get("dashboard.refresh_interval", default=60) if _config else 60
MAX_RECORDS_DISPLAY = _config.get("dashboard.max_records", default=500) if _config else 500

# 📦 إعدادات مؤشرات الأداء الرئيسية (KPIs)
_KPI_LIST = _config.get("kpis", default=[]) if _config else []
KPI_SETTINGS = {
    kpi["name"]: {
        "label": kpi.get("label", kpi["name"]),
        "unit": kpi.get("unit", ""),
        "color": kpi.get("color", "#000000"),
        "icon": kpi.get("icon", "📊"),
    }
    for kpi in _KPI_LIST
    if isinstance(kpi, dict) and "name" in kpi
}

# 🗂️ إعدادات أقسام الواجهة (Navigation / Tabs)
LAYOUT_SECTIONS = {
    "overview": "نظرة عامة",
    "exploration": "التحليل الاستكشافي",
    "models": "النماذج التنبؤية",
    "kpis": "مؤشرات الأداء",
    "reporting": "التقارير",
    "settings": "الإعدادات"
}

# 🔧 إعدادات عامة إضافية
DEFAULT_FONT = "Cairo"
ENABLE_EXPORT_BUTTONS = True
