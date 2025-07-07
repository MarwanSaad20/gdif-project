# config/dashboard_config.py

# 🎯 عنوان النظام
DASHBOARD_TITLE = "لوحة تحكم تحليل البيانات العام – GDIF"

# 🌐 اللغة الافتراضية
DEFAULT_LANGUAGE = "ar"

# 🎨 الثيم العام (light/dark/custom)
DEFAULT_THEME = "dark"

# 📦 إعدادات مؤشرات الأداء الرئيسية (KPIs)
KPI_SETTINGS = {
    "revenue": {
        "label": "الإيرادات",
        "unit": "$",
        "color": "#27AE60",   # أخضر
        "icon": "💰"
    },
    "growth": {
        "label": "معدل النمو",
        "unit": "%",
        "color": "#2980B9",   # أزرق
        "icon": "📈"
    },
    "churn_rate": {
        "label": "معدل التسرب",
        "unit": "%",
        "color": "#E74C3C",   # أحمر
        "icon": "⚠️"
    },
    "customer_count": {
        "label": "عدد العملاء",
        "unit": "",
        "color": "#8E44AD",   # بنفسجي
        "icon": "👥"
    }
}

# 🗂️ إعدادات أقسام الواجهة (Navigation / Tabs)
LAYOUT_SECTIONS = {
    "overview": "نظرة عامة",
    "exploration": "التحليل الاستكشافي",
    "models": "النماذج التنبؤية",
    "kpis": "مؤشرات الأداء",
    "reporting": "التقارير",
    "settings": "الإعدادات"
}

# 🔧 إعدادات عامة إضافية
REFRESH_INTERVAL = 60  # تحديث البيانات كل 60 ثانية (Dashboard auto-refresh)
DEFAULT_FONT = "Cairo"
MAX_RECORDS_DISPLAY = 500
ENABLE_EXPORT_BUTTONS = True

# ======== ملاحظات ومراجعة ========
# 1. DEFAULT_FONT: تأكد من توفر خط "Cairo" في بيئة التشغيل أو توفير بديل بديناميكية.
# 2. REFRESH_INTERVAL: 60 ثانية جيد لتحديث تلقائي، لكن قد يؤثر على الأداء حسب حجم البيانات والعمليات.
# 3. KPI_SETTINGS: القيم ثابتة وجيدة، لكن يمكن جعلها قابلة للتعديل ديناميكياً (مثلاً من ملف إعدادات خارجي أو لوحة تحكم).
# 4. LAYOUT_SECTIONS: التسمية جيدة ومنظمة، يجب التأكد أن أسماء المفاتيح تتطابق مع الـ callbacks والروابط في الواجهة.
# 5. يفضل إضافة إعدادات للغات أخرى إذا تم دعم تعدد اللغات مستقبلًا.
# 6. يفضل توفير إعدادات ثيم مخصصة (custom) بشكل أوضح، أو دعم ملفات CSS خارجية للثيمات.
# 7. عدم وجود مسارات في هذا الملف يعني أنه لا يحتوي على مشاكل مسار واضحة.

