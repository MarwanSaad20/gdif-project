from pathlib import Path
from data_intelligence_system.utils.config_handler import ConfigHandler
from data_intelligence_system.utils.logger import get_logger

logger = get_logger("PathsConfig")

# ===================== Load config.yaml =====================
CONFIG_FILE = Path(__file__).resolve().parent / "config.yaml"
try:
    config = ConfigHandler(str(CONFIG_FILE))
    config_cache = config._config if config else {}  # Cache loaded dict
    logger.info(f"✅ Loaded config from: {CONFIG_FILE}")
except Exception as e:
    logger.warning(f"⚠️ Failed to load config from {CONFIG_FILE}: {e}")
    config = None
    config_cache = {}

# ===================== Project root =====================
PROJECT_ROOT = Path(__file__).resolve().parent.parent
SYSTEM_ROOT = PROJECT_ROOT

# ===================== Helpers =====================
def get_path_from_config(key: str, fallback: Path) -> Path:
    """
    Get a path from config by key; fallback to default if missing.
    """
    value = config_cache.get(key) if config_cache else None
    if value is None:
        logger.warning(f"⚠️ Missing config key: {key}, using fallback: {fallback}")
    return Path(value) if value else fallback

# ===================== Data paths =====================
DATA_DIR = SYSTEM_ROOT / "data"
RAW_DATA_DIR = get_path_from_config("paths.raw_data", DATA_DIR / "raw")
PROCESSED_DATA_DIR = get_path_from_config("paths.processed_data", DATA_DIR / "processed")
EXTERNAL_DATA_DIR = DATA_DIR / "external"
EXTERNAL_DOWNLOADED_DIR = EXTERNAL_DATA_DIR / "downloaded"
RAW_DATA_PATHS = [RAW_DATA_DIR, EXTERNAL_DOWNLOADED_DIR]
SUPPORTED_EXTENSIONS = {'.csv', '.json', '.xlsx'}

# ===================== Data profiling =====================
DATA_PROFILES_DIR = SYSTEM_ROOT / "data_profiles"
EDA_OUTPUT_DIR = DATA_PROFILES_DIR / "eda_output"

# ===================== ETL / Analysis / Models =====================
ETL_DIR = SYSTEM_ROOT / "etl"
ANALYSIS_DIR = SYSTEM_ROOT / "analysis"
ML_MODELS_DIR = get_path_from_config("paths.models", SYSTEM_ROOT / "ml_models")

# ===================== Dashboard & Reports =====================
DASHBOARD_DIR = SYSTEM_ROOT / "dashboard"
DASHBOARD_ASSETS_DIR = DASHBOARD_DIR / "assets"

REPORTS_DIR = SYSTEM_ROOT / "reports"
REPORT_GENERATORS_DIR = REPORTS_DIR / "generators"
REPORT_TEMPLATES_DIR = REPORT_GENERATORS_DIR / "templates"
REPORT_OUTPUT_DIR = get_path_from_config("paths.reports", REPORTS_DIR / "output")
STATIC_ASSETS_DIR = REPORTS_DIR / "static_assets"

# ===================== Notebooks, utils, config, tests =====================
NOTEBOOKS_DIR = SYSTEM_ROOT / "notebooks"
UTILS_DIR = SYSTEM_ROOT / "utils"
CONFIG_DIR = SYSTEM_ROOT / "config"
TESTS_DIR = SYSTEM_ROOT / "tests"

# ===================== Core files =====================
CLEAN_DATA_FILE = PROCESSED_DATA_DIR / "clean_data.csv"
MAIN_SCRIPT = SYSTEM_ROOT / "main.py"
REQUIREMENTS_FILE = PROJECT_ROOT.parent / "requirements.txt"
DOCKERFILE = PROJECT_ROOT.parent / "Dockerfile"

# ===================== Ensure directories exist =====================
def ensure_directories_exist():
    """
    Create main directories if missing.
    """
    dirs_to_create = [
        DATA_DIR, RAW_DATA_DIR, PROCESSED_DATA_DIR,
        EXTERNAL_DATA_DIR, EXTERNAL_DOWNLOADED_DIR,
        DATA_PROFILES_DIR, EDA_OUTPUT_DIR,
        ETL_DIR, ANALYSIS_DIR, ML_MODELS_DIR,
        DASHBOARD_DIR, DASHBOARD_ASSETS_DIR,
        REPORTS_DIR, REPORT_GENERATORS_DIR, REPORT_TEMPLATES_DIR,
        REPORT_OUTPUT_DIR, STATIC_ASSETS_DIR,
        NOTEBOOKS_DIR, UTILS_DIR, CONFIG_DIR, TESTS_DIR,
    ]
    for directory in dirs_to_create:
        if not directory.exists():
            directory.mkdir(parents=True, exist_ok=True)
            logger.info(f"📁 Created directory: {directory}")

# ===================== Shortcuts for string paths =====================
RAW_DIR = str(RAW_DATA_DIR)
PROCESSED_DIR = str(PROCESSED_DATA_DIR)
