"""
ملف تعريف الثيم والمتغيرات اللونية العامة.
يستخدم لألوان متناسقة وخطوط ومساحات في التطبيق.
يمكن تعديل القيم بسهولة لتغيير الثيم العام.
"""

from typing import List, Dict
from data_intelligence_system.config.dashboard_config import DEFAULT_FONT  # ✅ جديد

class Theme:
    # الألوان الأساسية للتطبيق
    PRIMARY_COLOR: str = "#1E90FF"       # أزرق سماوي - اللون الأساسي
    SECONDARY_COLOR: str = "#FF4500"     # برتقالي داكن - لون ثانوي/تنبيهي
    SECONDARY_BG_COLOR: str = "#1F2937"  # خلفية ثانوية داكنة
    HOVER_COLOR: str = "#374151"         # لون hover (مثلاً للأزرار أو الروابط عند المرور عليها)

    BACKGROUND_COLOR: str = "#0A0F1A"    # خلفية داكنة جداً
    TEXT_COLOR: str = "#FFFFFF"          # نص أبيض واضح
    TEXT_MUTED_COLOR: str = "#A0A0A0"    # نص رمادي خافت للعناصر الثانوية
    TEXT_MUTED_COLOR_LIGHT: str = "#CCCCCC"  # نص رمادي فاتح (اختياري للاستخدامات الخفيفة)

    BORDER_COLOR: str = "#222E3D"        # حدود داكنة

    # ألوان إضافية للرسومات والواجهات
    SUCCESS_COLOR: str = "#28a745"        # أخضر للنجاحات والإشعارات الإيجابية
    WARNING_COLOR: str = "#ffc107"        # أصفر تحذيري
    DANGER_COLOR: str = "#dc3545"         # أحمر للأخطاء والتنبيهات الخطيرة
    INFO_COLOR: str = "#17a2b8"           # أزرق فاتح للمعلومات

    LINK_COLOR: str = PRIMARY_COLOR
    LINK_HOVER_COLOR: str = "#63b3ed"     # درجة أفتح من الأساسي للروابط عند المرور عليها

    BUTTON_ACTIVE_BG: str = "#2563eb"     # خلفية الزر النشط

    # ألوان درجات متدرجة يمكن استخدامها في الرسومات (Sequential و Diverging)
    COLOR_SCALE_SEQUENTIAL: List[str] = [
        "#0d47a1", "#1976d2", "#42a5f5", "#90caf9", "#bbdefb"
    ]

    COLOR_SCALE_DIVERGING: List[str] = [
        "#d32f2f", "#f44336", "#ffebee", "#bbdefb", "#1976d2", "#0d47a1"
    ]

    # خطوط عامة للتطبيق
    FONT_FAMILY: str = DEFAULT_FONT  # ✅ تم التبديل ليكون ديناميكيًا بدل القيمة الصلبة

    # الخطوط لأجزاء الكود أو النصوص المهيكلة (Monospace)
    MONOSPACE_FONT_FAMILY: str = "'Consolas', 'Courier New', monospace"

    # حجم الخطوط الشائع
    FONT_SIZES: Dict[str, str] = {
        "small": "0.8rem",
        "normal": "1rem",
        "large": "1.25rem",
        "xlarge": "1.5rem"
    }

    # ارتفاع الأسطر
    LINE_HEIGHT: float = 1.4

    # مساحة الحشوة (Padding) و الهوامش (Margin) الافتراضية بمستويات متعددة
    SPACING: Dict[str, str] = {
        "padding_small": "0.5rem",
        "padding_normal": "1rem",
        "padding_large": "1.5rem",
        "margin_small": "0.5rem",
        "margin_normal": "1rem",
        "margin_large": "1.5rem",
    }

    # ظلال خفيفة للأطر والبطاقات (مثال ظل أزرق شفاف)
    SHADOW_COLOR: str = "rgba(30, 144, 255, 0.25)"
