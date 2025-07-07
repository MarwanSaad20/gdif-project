# إعدادات عامة لتقارير نظام تحليل البيانات العام (GDIF)

import os
from datetime import datetime

# الجذر الرئيسي للمشروع (اثنين مستويات للأعلى لتوافق الهيكلية)
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

# توقيت التوليد (موحد طوال مدة تشغيل البرنامج)
NOW = datetime.now()
NOW_STR = NOW.strftime("%Y-%m-%d %H:%M:%S")
DATE_ONLY = NOW.strftime("%Y-%m-%d")

# المسارات الهامة داخل المشروع
ASSETS_PATH = os.path.join(PROJECT_ROOT, "reports", "static_assets")
TEMPLATES_PATH = os.path.join(PROJECT_ROOT, "reports", "generators", "templates")
OUTPUT_PATH = os.path.join(PROJECT_ROOT, "reports", "output")

# الإعدادات العامة للتقارير
REPORT_CONFIG = {
    "report_title": "📊 تقرير تحليلي ذكي — General Data Intelligence Report",
    "subtitle": "نظرة تحليلية للبيانات المدخلة والنتائج المستخرجة",
    "author": "فريق تحليل البيانات - GDIF",
    "organization": "مشروع نظام تحليل البيانات العام (GDIF)",
    "generated_on": NOW_STR,
    "version": "v1.0",
    "language": "ar",
    "encoding": "utf-8",
    "theme": {
        "primary_color": "#2B7A78",
        "secondary_color": "#17252A",
        "accent_color": "#DEF2F1",
        "font": "Arial",
        "font_size": 12
    },
    "logo_path": os.path.join(ASSETS_PATH, "logo.png"),
    "footer_image": os.path.join(ASSETS_PATH, "footer_banner.png"),
    "default_template": os.path.join(TEMPLATES_PATH, "base_report.html")
}

# اسم التقرير الافتراضي يعتمد على التاريخ الحالي
DEFAULT_REPORT_NAME = f"report_{DATE_ONLY}.pdf"

# خيارات مرنة لتخصيص محتوى التقرير
REPORT_OPTIONS = {
    "include_kpis": True,
    "include_charts": True,
    "include_tables": True,
    "include_raw_data_summary": True,
    "include_model_performance": True,
    "compress_output": False
}

# تم إزالة الدالة REPORT_CONFIG واستبدالها بالقاموس الثابت REPORT_CONFIG
