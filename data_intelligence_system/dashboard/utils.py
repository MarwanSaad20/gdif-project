"""
utils.py

وظائف مساعدة عامة للواجهة:
- تحويل وتنسيق التاريخ
- تنسيق الأرقام (عملات، نسب، آلاف...)
- تنسيق النصوص
- أدوات وقت وتاريخ
- أدوات مساعدة أخرى
"""

from datetime import datetime, timedelta
import locale
import logging

logger = logging.getLogger(__name__)

# تعيين اللغة وlocale (مثال للغة العربية)
try:
    locale.setlocale(locale.LC_ALL, 'ar_AE.utf8')  # أو 'ar_SA.utf8' حسب النظام
except locale.Error:
    # إذا لم يكن locale مدعوماً على النظام، تسجل تحذير بدلاً من التجاهل الصامت
    logger.warning("locale 'ar_AE.utf8' غير مدعوم على هذا النظام، استخدام الإعدادات الافتراضية.")


def format_datetime(dt: datetime, fmt: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    تحويل datetime إلى نص بتنسيق محدد.
    الافتراضي: 'YYYY-MM-DD HH:mm:ss'
    """
    if dt is None:
        return ""
    try:
        return dt.strftime(fmt)
    except Exception as e:
        logger.error(f"فشل في تنسيق التاريخ: {e}")
        return ""


from typing import Optional

def parse_datetime(date_str: str, fmt_list=None) -> Optional[datetime]:
    """
    تحويل نص تاريخ إلى datetime حسب قائمة تنسيقات.
    إذا لم يتم التحويل، يعيد None.
    """
    if not date_str:
        return None

    if fmt_list is None:
        fmt_list = [
            "%Y-%m-%d",
            "%d/%m/%Y",
            "%d-%m-%Y",
            "%Y-%m-%d %H:%M:%S",
            "%d/%m/%Y %H:%M",
            "%Y-%m-%dT%H:%M:%S",      # دعم ISO 8601 بدون المنطقة الزمنية
            "%Y-%m-%dT%H:%M:%SZ",     # ISO 8601 مع Zulu timezone
        ]

    for fmt in fmt_list:
        try:
            return datetime.strptime(date_str, fmt)
        except (ValueError, TypeError):
            continue

    logger.warning(f"تعذر تحويل النص '{date_str}' لأي من التنسيقات: {fmt_list}")
    return None


def format_number(value, decimals=2, use_commas=True) -> str:
    """
    تنسيق رقم بعلامات الفاصلة وفاصلة عشرية.
    - decimals: عدد الأرقام بعد الفاصلة العشرية
    - use_commas: استخدام فواصل الآلاف
    """
    try:
        if value is None:
            return ""
        if use_commas:
            formatted = f"{value:,.{decimals}f}"
        else:
            formatted = f"{value:.{decimals}f}"
        return formatted
    except Exception as e:
        logger.error(f"فشل في تنسيق الرقم '{value}': {e}")
        return str(value)


def format_currency(value, currency_symbol="د.ع", decimals=0, symbol_position="after") -> str:
    """
    تنسيق رقم كعملة مع رمز العملة.
    مثال: 15000 -> "15,000 د.ع"
    symbol_position: 'after' أو 'before' لتحديد موقع الرمز.
    """
    formatted_num = format_number(value, decimals=decimals, use_commas=True)
    if symbol_position == "before":
        return f"{currency_symbol} {formatted_num}"
    else:
        return f"{formatted_num} {currency_symbol}"


def format_percentage(value, decimals=2) -> str:
    """
    تنسيق رقم كنسبة مئوية مع علامة %.
    """
    try:
        if value is None:
            return ""
        return f"{value:.{decimals}f}%"
    except Exception as e:
        logger.error(f"فشل في تنسيق النسبة '{value}': {e}")
        return str(value)


def time_ago(dt: datetime) -> str:
    """
    تحويل datetime إلى نص يعبر عن الفترة الزمنية منذ ذلك الوقت حتى الآن.
    مثال: "قبل 5 دقائق"، "قبل ساعتين"
    """
    if not dt:
        return ""

    now = datetime.now()
    diff = now - dt

    seconds = diff.total_seconds()

    def arabic_time_unit(value, unit_singular, unit_dual, unit_plural):
        if value == 1:
            return unit_singular
        elif value == 2:
            return unit_dual
        elif 3 <= value <= 10:
            return unit_plural
        else:
            return unit_singular  # يمكن تعديل لجمع تكسير حسب الحاجة

    if seconds < 60:
        return "قبل ثوانٍ"
    elif seconds < 3600:
        minutes = int(seconds // 60)
        unit = arabic_time_unit(minutes, "دقيقة", "دقيقتين", "دقائق")
        return f"قبل {minutes} {unit}"
    elif seconds < 86400:
        hours = int(seconds // 3600)
        unit = arabic_time_unit(hours, "ساعة", "ساعتين", "ساعات")
        return f"قبل {hours} {unit}"
    elif seconds < 604800:
        days = int(seconds // 86400)
        unit = arabic_time_unit(days, "يوم", "يومين", "أيام")
        return f"قبل {days} {unit}"
    else:
        weeks = int(seconds // 604800)
        unit = arabic_time_unit(weeks, "أسبوع", "أسبوعين", "أسابيع")
        return f"قبل {weeks} {unit}"


def truncate_text(text: str, max_length=50, suffix="...") -> str:
    """
    تقصير النص إذا تجاوز الطول المحدد مع إضافة لاحقة.
    """
    if not text:
        return ""
    if len(text) <= max_length:
        return text
    return text[:max_length].rstrip() + suffix


# --- نقاط التحسين المحتملة ---
# - دعم إعدادات locale ديناميكية حسب المستخدم.
# - إضافة دوال لتحويل العملات حسب التنسيق المحلي.
# - دعم تحويل نصوص تاريخ مع مناطق زمنية.
# - تحسين رسائل اللوج لجعلها أكثر تفصيلاً.

if __name__ == "__main__":
    import sys

    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG, format='%(levelname)s:%(message)s')

    now = datetime.now()
    print("تاريخ ووقت الآن:", format_datetime(now))
    print("تحليل '2025-06-17' =>", parse_datetime("2025-06-17"))
    print("تحليل '17/06/2025' =>", parse_datetime("17/06/2025"))
    print("تحليل ISO '2025-06-17T15:30:00' =>", parse_datetime("2025-06-17T15:30:00"))
    print("تنسيق رقم:", format_number(1234567.89123))
    print("تنسيق عملة:", format_currency(1500000))
    print("تنسيق عملة مع رمز قبل الرقم:", format_currency(1500000, symbol_position="before"))
    print("تنسيق نسبة:", format_percentage(12.3456))
    print("قبل:", time_ago(now - timedelta(minutes=5)))
    print("تقصير نص:", truncate_text("هذه جملة طويلة جدا ونريد تقصيرها إلى حد معين", max_length=20))


def file_manager():
    return None
