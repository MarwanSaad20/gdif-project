"""
ملف التجميع الرئيسي لجميع مكونات لوحة التحكم (Components).

يتم فيه استيراد وتجهيز جميع مكونات الواجهة مثل: مؤشرات الأداء، الرسوم البيانية،
الفلاتر، الجداول، ورفع الملفات، بحيث يمكن استخدامها مباشرة داخل ملفات التخطيط أو التفاعلات.
"""

# ✅ مكونات رفع الملفات
from .upload_component import upload_csv_component, upload_section

# ✅ مكونات الرسوم البيانية
from .charts import create_pie_chart, create_bar_chart, create_line_chart

# ✅ مكونات الجداول
from .tables import create_data_table

# ✅ مكونات الفلاتر (Dropdown, Slider, DatePicker)
from .filters import create_dropdown, create_slider, create_date_picker

# ✅ مكونات مؤشرات الأداء (KPIs)
from .indicators import create_kpi_card


def register_components():
    """
    هذا الملف لا يحتوي على تسجيل مباشر مثل callbacks،
    بل يهدف إلى تسهيل عملية الاستيراد المركزي لجميع المكونات.
    """
    pass


__all__ = [
    "upload_csv_component",
    "upload_section",
    "create_pie_chart",
    "create_bar_chart",
    "create_line_chart",
    "create_data_table",
    "create_dropdown",
    "create_slider",
    "create_date_picker",
    "create_kpi_card",
]

# إزالة التكرار الغير ضروري
# إذا كنت بحاجة لدوال مثل kpi_cards أو stats_summary
# أنشئها هنا مع محتوى مناسب أو احذفها إذا غير مستخدمة.
