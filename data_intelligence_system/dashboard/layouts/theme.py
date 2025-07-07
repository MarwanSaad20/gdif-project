"""
ملف تعريف الثيم والمتغيرات اللونية العامة
- يستخدم لألوان متناسقة عبر التطبيق
- يمكن تعديل القيم بسهولة لتغيير الثيم العام
"""

# الألوان الأساسية للتطبيق
PRIMARY_COLOR = "#1E90FF"       # أزرق سماوي - اللون الأساسي
SECONDARY_COLOR = "#FF4500"     # برتقالي داكن - لون ثانوي/تنبيهي
SECONDARY_BG_COLOR = "#1F2937"  # خلفية ثانوية داكنة
HOVER_COLOR = "#374151"         # لون hover (مثلاً للأزرار أو الروابط عند المرور عليها)

BACKGROUND_COLOR = "#0A0F1A"    # خلفية داكنة جداً
TEXT_COLOR = "#FFFFFF"          # نص أبيض واضح
TEXT_MUTED_COLOR = "#A0A0A0"    # نص رمادي خافت للعناصر الثانوية
TEXT_MUTED_COLOR_LIGHT = "#CCCCCC"  # نص رمادي فاتح (اختياري للاستخدامات الخفيفة)

BORDER_COLOR = "#222E3D"        # حدود داكنة

# ألوان إضافية للرسومات والواجهات
SUCCESS_COLOR = "#28a745"        # أخضر للنجاحات والإشعارات الإيجابية
WARNING_COLOR = "#ffc107"        # أصفر تحذيري
DANGER_COLOR = "#dc3545"         # أحمر للأخطاء والتنبيهات الخطيرة
INFO_COLOR = "#17a2b8"           # أزرق فاتح للمعلومات

LINK_COLOR = PRIMARY_COLOR
LINK_HOVER_COLOR = "#63b3ed"     # درجة أفتح من الأساسي للروابط عند المرور عليها

BUTTON_ACTIVE_BG = "#2563eb"     # خلفية الزر النشط

# ألوان درجات متدرجة يمكن استخدامها في الرسومات (Sequential و Diverging)
COLOR_SCALE_SEQUENTIAL = [
    "#0d47a1", "#1976d2", "#42a5f5", "#90caf9", "#bbdefb"
]

COLOR_SCALE_DIVERGING = [
    "#d32f2f", "#f44336", "#ffebee", "#bbdefb", "#1976d2", "#0d47a1"
]

# خطوط عامة للتطبيق
FONT_FAMILY = "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif"

# الخطوط لأجزاء الكود أو النصوص المهيكلة (Monospace)
MONOSPACE_FONT_FAMILY = "'Consolas', 'Courier New', monospace"

# حجم الخطوط الشائع
FONT_SIZES = {
    "small": "0.8rem",
    "normal": "1rem",
    "large": "1.25rem",
    "xlarge": "1.5rem"
}

# ارتفاع الأسطر
LINE_HEIGHT = 1.4

# مساحة الحشوة (Padding) و الهوامش (Margin) الافتراضية بمستويات متعددة
SPACING = {
    "padding_small": "0.5rem",
    "padding_normal": "1rem",
    "padding_large": "1.5rem",
    "margin_small": "0.5rem",
    "margin_normal": "1rem",
    "margin_large": "1.5rem",
}

# ظلال خفيفة للأطر والبطاقات (مثال ظل أزرق شفاف)
SHADOW_COLOR = "rgba(30, 144, 255, 0.25)"
