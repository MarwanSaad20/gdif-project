from pathlib import Path
from data_intelligence_system.utils.config_handler import ConfigHandler
from data_intelligence_system.utils.logger import get_logger

"""
Dashboard configuration module.
Loads and manages dashboard settings for the GDIF project.
"""

logger = get_logger("dashboard_config")

# Load configuration
config_path = Path(__file__).resolve().parent / "config.yaml"
try:
    _config = ConfigHandler(str(config_path))
    logger.info(f"✅ Loaded dashboard settings from: {config_path}")
except Exception as e:
    logger.warning(f"⚠️ Failed to load dashboard settings: {e}")
    _config = None

def get_config_value(key, default):
    return _config.get(key, default) if _config else default

# Dashboard settings
DASHBOARD_TITLE = "لوحة تحكم تحليل البيانات العام – GDIF"
DEFAULT_LANGUAGE = get_config_value("project.language", "ar")
DEFAULT_THEME = get_config_value("dashboard.theme", "dark")
REFRESH_INTERVAL = get_config_value("dashboard.refresh_interval", 60)
MAX_RECORDS_DISPLAY = get_config_value("dashboard.max_records", 500)

# KPI settings
_KPI_LIST = get_config_value("kpis", [])
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

# Layout sections
LAYOUT_SECTIONS = {
    "overview": "نظرة عامة",
    "exploration": "التحليل الاستكشافي",
    "models": "النماذج التنبؤية",
    "kpis": "مؤشرات الأداء",
    "reporting": "التقارير",
    "settings": "الإعدادات"
}

# Other general settings
DEFAULT_FONT = "Cairo"
ENABLE_EXPORT_BUTTONS = True
