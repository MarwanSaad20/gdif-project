from pathlib import Path

# ===================== الجذر الرئيسي للمشروع =====================
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# 📄 ملف البيئة (.env)
ENV_FILE = PROJECT_ROOT / ".env"

# ===================== مجلد النظام الداخلي =====================
SYSTEM_ROOT = PROJECT_ROOT / "data_intelligence_system"

# ===================== مسارات البيانات =====================
DATA_DIR = SYSTEM_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
EXTERNAL_DATA_DIR = DATA_DIR / "external"
print("PROJECT_ROOT:", PROJECT_ROOT)
print("SYSTEM_ROOT:", SYSTEM_ROOT)
print("RAW DATA PATH:", SYSTEM_ROOT / "data" / "raw")
print("PROCESSED DATA PATH:", SYSTEM_ROOT / "data" / "processed")

# إضافة مجلد التنزيلات ضمن البيانات الخارجية (إن وجد)
EXTERNAL_DOWNLOADED_DIR = EXTERNAL_DATA_DIR / "downloaded"

# ===================== قائمة المسارات الخاصة ببيانات المصدر الخام والخارجية =====================
RAW_DATA_PATHS = [
    RAW_DATA_DIR,                # مجلد البيانات الخام
    EXTERNAL_DOWNLOADED_DIR      # مجلد البيانات الخارجية المنزّلة
]

# ===================== الامتدادات المدعومة للملفات =====================
SUPPORTED_EXTENSIONS = {'.csv', '.json', '.xlsx'}

# ===================== توصيف البيانات والتحليل الاستكشافي =====================
DATA_PROFILES_DIR = SYSTEM_ROOT / "data_profiles"
EDA_OUTPUT_DIR = DATA_PROFILES_DIR / "eda_output"

# ===================== وحدات ETL (استخراج - تحويل - تحميل) =====================
ETL_DIR = SYSTEM_ROOT / "etl"

# ===================== التحليلات الإحصائية والارتباطية =====================
ANALYSIS_DIR = SYSTEM_ROOT / "analysis"

# ===================== نماذج تعلم الآلة =====================
ML_MODELS_DIR = SYSTEM_ROOT / "ml_models"

# ===================== واجهة المستخدم (Dashboard باستخدام Dash) =====================
DASHBOARD_DIR = SYSTEM_ROOT / "dashboard"
DASHBOARD_ASSETS_DIR = DASHBOARD_DIR / "assets"

# ===================== التقارير وتوليدها =====================
REPORTS_DIR = SYSTEM_ROOT / "reports"
REPORT_GENERATORS_DIR = REPORTS_DIR / "generators"
REPORT_TEMPLATES_DIR = REPORT_GENERATORS_DIR / "templates"
REPORT_OUTPUT_DIR = REPORTS_DIR / "output"
STATIC_ASSETS_DIR = REPORTS_DIR / "static_assets"

# ===================== دفاتر Jupyter والمستندات التحليلية =====================
NOTEBOOKS_DIR = SYSTEM_ROOT / "notebooks"

# ===================== الأدوات والمكتبات المساعدة =====================
UTILS_DIR = SYSTEM_ROOT / "utils"

# ===================== إعدادات النظام =====================
CONFIG_DIR = SYSTEM_ROOT / "config"

# ===================== اختبارات النظام =====================
TESTS_DIR = SYSTEM_ROOT / "tests"

# ===================== ملفات مهمة =====================
CLEAN_DATA_FILE = PROCESSED_DATA_DIR / "clean_data.csv"
MAIN_SCRIPT = SYSTEM_ROOT / "main.py"
REQUIREMENTS_FILE = PROJECT_ROOT / "requirements.txt"
DOCKERFILE = PROJECT_ROOT / "Dockerfile"


def ensure_directories_exist():
    """
    تنشئ المجلدات الأساسية إذا لم تكن موجودة.
    """
    dirs_to_create = [
        DATA_DIR,
        RAW_DATA_DIR,
        PROCESSED_DATA_DIR,
        EXTERNAL_DATA_DIR,
        EXTERNAL_DOWNLOADED_DIR,
        DATA_PROFILES_DIR,
        EDA_OUTPUT_DIR,
        ETL_DIR,
        ANALYSIS_DIR,
        ML_MODELS_DIR,
        DASHBOARD_DIR,
        DASHBOARD_ASSETS_DIR,
        REPORTS_DIR,
        REPORT_GENERATORS_DIR,
        REPORT_TEMPLATES_DIR,
        REPORT_OUTPUT_DIR,
        STATIC_ASSETS_DIR,
        NOTEBOOKS_DIR,
        UTILS_DIR,
        CONFIG_DIR,
        TESTS_DIR,
    ]

    for directory in dirs_to_create:
        directory.mkdir(parents=True, exist_ok=True)

# يمكن استدعاء هذه الدالة عند بدء تشغيل المشروع لضمان وجود المجلدات:
# ensure_directories_exist()
