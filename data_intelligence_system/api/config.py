# config/config.py
import logging

import os
from datetime import timedelta
from dotenv import load_dotenv
from data_intelligence_system.utils.logger import get_logger  # تعديل الاستيراد

# تحميل متغيرات البيئة من ملف .env (إن وجد)
load_dotenv()

class Config:
    # إعدادات عامة
    APP_NAME = "General Data Intelligence Framework (GDIF)"
    DEBUG = os.getenv("DEBUG", "false").lower() == "true"
    ENV = os.getenv("ENV", "production")
    SECRET_KEY = os.getenv("SECRET_KEY", "you-must-change-this-in-env")

    # CORS إعدادات
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost,http://127.0.0.1").split(",")
    CORS_METHODS = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    CORS_ALLOW_HEADERS = ["Authorization", "Content-Type", "Accept"]

    # Rate Limiting
    RATE_LIMIT_DEFAULT = os.getenv("RATE_LIMIT_DEFAULT", "100/minute")
    RATE_LIMIT_STRATEGY = os.getenv("RATE_LIMIT_STRATEGY", "fixed-window")

    # أمان
    PASSWORD_HASH_ALGORITHM = "bcrypt"
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60))

    # OAuth2
    OAUTH2_CLIENT_ID = os.getenv("OAUTH2_CLIENT_ID", "")
    OAUTH2_CLIENT_SECRET = os.getenv("OAUTH2_CLIENT_SECRET", "")
    OAUTH2_TOKEN_URL = "/auth/token"

    # قاعدة البيانات
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./gdif_dev.db")

    # ملفات السجل
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
    LOG_FILE = os.getenv("LOG_FILE", "logs/api.log")

    @staticmethod
    def ensure_log_directory():
        log_path = os.path.dirname(Config.LOG_FILE)
        if log_path and not os.path.exists(log_path):
            os.makedirs(log_path)

# إنشاء مجلد السجل إن لم يكن موجودًا
Config.ensure_log_directory()

# تهيئة اللوجر باستخدام الدالة get_logger من utils.logger
logger = get_logger(
    name="api_logger",
    log_dir=os.path.dirname(Config.LOG_FILE),
    level=getattr(logging, Config.LOG_LEVEL.upper(), logging.INFO),
    reset=True
)

def get_config(env: str = None):
    if env is None:
        env = os.getenv("ENV", Config.ENV)

    if env == "development":
        class DevConfig(Config):
            DEBUG = True
            ENV = "development"
            RATE_LIMIT_DEFAULT = "1000/minute"
            SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret")
        return DevConfig()
    elif env == "testing":
        class TestConfig(Config):
            DEBUG = True
            ENV = "testing"
            RATE_LIMIT_DEFAULT = "10000/minute"
            SECRET_KEY = os.getenv("SECRET_KEY", "test-secret")
        return TestConfig()
    else:
        return Config()

# تحميل الإعدادات
config = get_config()
