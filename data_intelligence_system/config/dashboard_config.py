# config/dashboard_config.py

from data_intelligence_system.utils.config_handler import ConfigHandler
from data_intelligence_system.utils.logger import get_logger
from pathlib import Path

# ✅ إعداد اللوجر
logger = get_logger("dashboard_config")

# ✅ تحميل الإعدادات من ملف YAML
config_path = Path(__file__).resolve().parent / "config.yaml"
_config = ConfigHandler(str(config_path))

# 🎯 عنوان النظام
DASHBOARD_TITLE = "لوحة تحكم تحليل البيانات العام – GDIF"

# 🌐 إعدادات الواجهة من الملف
DEFAULT_LANGUAGE = _config.get("project.language", default="ar")
DEFAULT_THEME = _config.get("dashboard.theme", default="dark")
REFRESH_INTERVAL = _config.get("dashboard.refresh_interval", default=60)
MAX_RECORDS_DISPLAY = _config.get("dashboard.max_records", default=500)

# 📦 إعدادات مؤشرات الأداء الرئيسية (KPIs)
_KPI_LIST = _config.get("kpis", default=[])
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
