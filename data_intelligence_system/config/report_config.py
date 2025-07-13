from datetime import datetime
from pathlib import Path
from data_intelligence_system.utils.config_handler import ConfigHandler
from data_intelligence_system.utils.logger import get_logger

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
    """
    استرجاع قيمة من ملف الإعدادات.

    :param key: المفتاح في إعدادات YAML (مثال: 'project.author')
    :param default: القيمة الافتراضية في حال عدم وجود المفتاح أو فشل التحميل
    :return: القيمة المرتبطة بالمفتاح أو القيمة الافتراضية
    """
    if not hasattr(get_config_value, "_cache"):
        get_config_value._cache = {}

    if key in get_config_value._cache:
        return get_config_value._cache[key]

    value = config.get(key, default) if config else default
    get_config_value._cache[key] = value
    return value

# ===================== ثوابت التقرير =====================

# 📄 عنوان التقرير الأساسي
REPORT_TITLE = "تقرير تحليلي شامل - نظام تحليل البيانات العام"

# 📆 تاريخ التقرير الحالي (يتم تحديثه عند استيراد الملف)
REPORT_DATE = datetime.now().strftime("%Y-%m-%d")

# 🏷️ بيانات المرسل
AUTHOR = get_config_value("project.author", "Marwan Al_Jubouri")
ORGANIZATION = "General Data Intelligence Framework - GDIF"

# 🎨 ألوان التصميم الرئيسية
COLOR_SCHEME = {
    "primary": "#2E86C1",
    "secondary": "#1ABC9C",
    "danger": "#E74C3C",
    "text": "#2C3E50",
    "background": "#FDFEFE",
    "highlight": "#F1C40F"
}

# 📌 مسارات الشعارات والصور الثابتة
LOGO_PATH = Path("data_intelligence_system/reports/static_assets/logo.png").resolve()
FOOTER_BANNER_PATH = Path("data_intelligence_system/reports/static_assets/footer_banner.png").resolve()

# 📁 مسار قالب HTML (Jinja2)
TEMPLATE_PATH = Path("data_intelligence_system/reports/generators/templates/base_report.html").resolve()

# ⚙️ إعدادات الخطوط والتنسيق
FONT = "Cairo"
FONT_SIZE = 12
HEADER_FONT_SIZE = 18
LINE_SPACING = 1.5

# 📈 إعدادات تنسيق الجداول
TABLE_STYLE = {
    "header_bg": "#34495E",
    "header_fg": "#ECF0F1",
    "row_bg": "#FFFFFF",
    "alt_row_bg": "#F9F9F9",
    "border_color": "#BDC3C7"
}

# 📄 إعدادات الإخراج الافتراضية
DEFAULT_FORMAT = "pdf"  # الخيارات: "pdf", "excel", "html"
OUTPUT_DIR = Path(get_config_value("paths.reports", "data_intelligence_system/reports/output")).resolve()

# ✅ مسار حفظ التقرير النهائي
OUTPUT_PATH = OUTPUT_DIR
