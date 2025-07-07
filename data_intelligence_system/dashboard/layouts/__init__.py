from .main_layout import get_layout

# لا تستورد kpi_card إن لم تكن موجودة في kpi_cards.py
# إذا تحتاج استخدام generate_kpi_cards_layout من callbacks، استوردها من هناك في مكان آخر (مثلاً main_layout.py)

from .charts_placeholders import line_chart, bar_chart, pie_chart, forecast_chart
from .stats_summary import stats_summary_card

__all__ = [
    "get_layout",
    # "kpi_card",  # علق أو احذف هذا السطر إذا لم يكن موجود فعلاً
    "line_chart",
    "bar_chart",
    "pie_chart",
    "forecast_chart",
    "stats_summary_card",  # بطاقة ملخص التحليل الإحصائي
]

def dashboard_layout():
    return None

def filters():
    return None
