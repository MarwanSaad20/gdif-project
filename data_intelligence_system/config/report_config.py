from datetime import datetime
from pathlib import Path
from data_intelligence_system.utils.config_handler import ConfigHandler
from data_intelligence_system.utils.logger import get_logger

# ✅ اللوجر
logger = get_logger("ReportConfig")

# ===================== تحميل الإعدادات =====================
CONFIG_FILE = Path(__file__).resolve().parent / "config.yaml"
config = None

try:
    config = ConfigHandler(str(CONFIG_FILE))
    logger.info(f"✅ تم تحميل الإعدادات من: {CONFIG_FILE}")
except Exception as e:
    logger.warning(f"⚠️ فشل تحميل إعدادات التقارير: {e}")

def get_config_value(key: str, default=None):
    return config.get(key, default) if config else default

# 📄 عنوان التقرير الأساسي
REPORT_TITLE = "تقرير تحليلي شامل - نظام تحليل البيانات العام"

# 📆 تاريخ التقرير
REPORT_DATE = datetime.now().strftime("%Y-%m-%d")

# 🏷️ بيانات المرسل
AUTHOR = get_config_value("project.author", "Marwan Al_Jubouri")
ORGANIZATION = "General Data Intelligence Framework - GDIF"

# 🎨 الألوان الأساسية
COLOR_SCHEME = {
    "primary": "#2E86C1",
    "secondary": "#1ABC9C",
    "danger": "#E74C3C",
    "text": "#2C3E50",
    "background": "#FDFEFE",
    "highlight": "#F1C40F"
}

# 📌 شعارات وصور
LOGO_PATH = Path("data_intelligence_system/reports/static_assets/logo.png")
FOOTER_BANNER_PATH = Path("data_intelligence_system/reports/static_assets/footer_banner.png")

# 📁 قالب HTML (Jinja2)
TEMPLATE_PATH = Path("data_intelligence_system/reports/generators/templates/base_report.html")

# ⚙️ الخطوط والتنسيق
FONT = "Cairo"
FONT_SIZE = 12
HEADER_FONT_SIZE = 18
LINE_SPACING = 1.5

# 📈 تنسيق الجداول
TABLE_STYLE = {
    "header_bg": "#34495E",
    "header_fg": "#ECF0F1",
    "row_bg": "#FFFFFF",
    "alt_row_bg": "#F9F9F9",
    "border_color": "#BDC3C7"
}

# 📄 إعدادات الحفظ
DEFAULT_FORMAT = "pdf"  # يمكن أن تكون: "pdf", "excel", "html"
OUTPUT_DIR = Path(get_config_value("paths.reports", "data_intelligence_system/reports/output"))

# ✅ تعريف OUTPUT_PATH المطلوب لاستيراده
OUTPUT_PATH = OUTPUT_DIR
