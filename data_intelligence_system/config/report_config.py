# config/report_config.py

from datetime import datetime
from pathlib import Path

# 📄 عنوان التقرير الأساسي
REPORT_TITLE = "تقرير تحليلي شامل - نظام تحليل البيانات العام"

# 📆 تاريخ التقرير (افتراضيًا وقت التشغيل)
REPORT_DATE = datetime.now().strftime("%Y-%m-%d")

# 🏷️ بيانات المرسل
AUTHOR = "Marwan Al_Jubouri"
ORGANIZATION = "General Data Intelligence Framework - GDIF"

# 🎨 الألوان الأساسية المستخدمة في الرسوم والتقارير
COLOR_SCHEME = {
    "primary": "#2E86C1",
    "secondary": "#1ABC9C",
    "danger": "#E74C3C",
    "text": "#2C3E50",
    "background": "#FDFEFE",
    "highlight": "#F1C40F"
}

# 📌 شعارات وصور للتقارير (تُستخدم في الـ PDF أو HTML)
LOGO_PATH = Path("data_intelligence_system/reports/static_assets/logo.png")
FOOTER_BANNER_PATH = Path("data_intelligence_system/reports/static_assets/footer_banner.png")

# 📁 قوالب HTML (Jinja2)
TEMPLATE_PATH = Path("data_intelligence_system/reports/generators/templates/base_report.html")

# ⚙️ إعدادات خطوط وتنسيق عام
FONT = "Cairo"
FONT_SIZE = 12
HEADER_FONT_SIZE = 18
LINE_SPACING = 1.5

# 📈 تنسيق جداول Excel أو HTML
TABLE_STYLE = {
    "header_bg": "#34495E",
    "header_fg": "#ECF0F1",
    "row_bg": "#FFFFFF",
    "alt_row_bg": "#F9F9F9",
    "border_color": "#BDC3C7"
}

# 📄 إعدادات الحفظ
DEFAULT_FORMAT = "pdf"  # يمكن أن تكون: "pdf", "excel", "html"
OUTPUT_DIR = Path("data_intelligence_system/reports/output")

# ======== الملاحظات والتوصيات ========
# 1. تأكد من وجود مجلد OUTPUT_DIR والمجلدات الأخرى المشار إليها في المسارات لتجنب أخطاء عدم وجود الملفات.
# 2. يمكن إضافة تحقق عند تحميل الصور والقوالب، مثلا:
#    if not LOGO_PATH.exists():
#        raise FileNotFoundError(f"شعار التقرير غير موجود في المسار: {LOGO_PATH}")
# 3. إذا كان المشروع يستخدم إعدادات مسارات مركزية (config/paths_config.py)، فمن الأفضل استيراد تلك المسارات بدلاً من كتابتها هنا كمسارات ثابتة.
# 4. خطوط مثل "Cairo" يجب التأكد من توفرها في بيئة التشغيل أو توفير بدائل مناسبة.
# 5. يمكن التفكير في دعم إعدادات أكثر ديناميكية مثل تغيير لغة التقرير، أو تخصيص الإخراج عبر متغيرات بيئية أو ملف إعدادات خارجي.
