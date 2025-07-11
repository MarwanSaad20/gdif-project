from pathlib import Path
from data_intelligence_system.utils.config_handler import ConfigHandler
from data_intelligence_system.utils.logger import get_logger

# ✅ إعداد اللوجر
logger = get_logger("PathsConfig")

# ===================== تحميل إعدادات من config.yaml =====================
CONFIG_FILE = Path(__file__).resolve().parent / "config.yaml"
config = None

try:
    config = ConfigHandler(str(CONFIG_FILE))
    logger.info(f"✅ تم تحميل الإعدادات من: {CONFIG_FILE}")
except Exception as e:
    logger.warning(f"⚠️ فشل تحميل إعدادات المسارات من {CONFIG_FILE}: {e}")

# ===================== الجذر الرئيسي للمشروع =====================
PROJECT_ROOT = Path(__file__).resolve().parent.parent
SYSTEM_ROOT = PROJECT_ROOT

# ===================== إعداد المسارات من config إن وجد =====================
def get_path_from_config(key: str, fallback: Path) -> Path:
    value = config.get(key) if config else None
    return Path(value) if value else fallback

# ===================== مسارات البيانات =====================
DATA_DIR = SYSTEM_ROOT / "data"
RAW_DATA_DIR = get_path_from_config("paths.raw_data", DATA_DIR / "raw")
PROCESSED_DATA_DIR = get_path_from_config("paths.processed_data", DATA_DIR / "processed")
EXTERNAL_DATA_DIR = DATA_DIR / "external"
EXTERNAL_DOWNLOADED_DIR = EXTERNAL_DATA_DIR / "downloaded"

RAW_DATA_PATHS = [RAW_DATA_DIR, EXTERNAL_DOWNLOADED_DIR]
SUPPORTED_EXTENSIONS = {'.csv', '.json', '.xlsx'}

# ===================== توصيف البيانات والتحليل الاستكشافي =====================
DATA_PROFILES_DIR = SYSTEM_ROOT / "data_profiles"
EDA_OUTPUT_DIR = DATA_PROFILES_DIR / "eda_output"

# ===================== وحدات ETL =====================
ETL_DIR = SYSTEM_ROOT / "etl"

# ===================== التحليلات =====================
ANALYSIS_DIR = SYSTEM_ROOT / "analysis"

# ===================== النماذج =====================
ML_MODELS_DIR = get_path_from_config("paths.models", SYSTEM_ROOT / "ml_models")

# ===================== الواجهة =====================
DASHBOARD_DIR = SYSTEM_ROOT / "dashboard"
DASHBOARD_ASSETS_DIR = DASHBOARD_DIR / "assets"

# ===================== التقارير =====================
REPORTS_DIR = SYSTEM_ROOT / "reports"
REPORT_GENERATORS_DIR = REPORTS_DIR / "generators"
REPORT_TEMPLATES_DIR = REPORT_GENERATORS_DIR / "templates"
REPORT_OUTPUT_DIR = get_path_from_config("paths.reports", REPORTS_DIR / "output")
STATIC_ASSETS_DIR = REPORTS_DIR / "static_assets"

# ===================== دفاتر ومساعدات =====================
NOTEBOOKS_DIR = SYSTEM_ROOT / "notebooks"
UTILS_DIR = SYSTEM_ROOT / "utils"
CONFIG_DIR = SYSTEM_ROOT / "config"
TESTS_DIR = SYSTEM_ROOT / "tests"

# ===================== ملفات رئيسية =====================
CLEAN_DATA_FILE = PROCESSED_DATA_DIR / "clean_data.csv"
MAIN_SCRIPT = SYSTEM_ROOT / "main.py"
REQUIREMENTS_FILE = PROJECT_ROOT.parent / "requirements.txt"
DOCKERFILE = PROJECT_ROOT.parent / "Dockerfile"

# ===================== إنشاء المجلدات =====================
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

# ===================== ثوابت مختصرة للتكامل مع باقي النظام =====================
RAW_DIR = str(RAW_DATA_DIR)                # مسار raw كـ string
PROCESSED_DIR = str(PROCESSED_DATA_DIR)    # مسار processed كـ string
