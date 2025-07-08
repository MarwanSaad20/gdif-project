# config/db_config.py

import os
from pathlib import Path
from dotenv import load_dotenv

from data_intelligence_system.utils.config_handler import ConfigHandler
from data_intelligence_system.utils.logger import get_logger

logger = get_logger("db_config")

# تحميل متغيرات البيئة من ملف .env (إذا كان موجودًا)
env_path = Path(__file__).resolve().parent.parent / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path)
else:
    logger.warning("⚠️ ملف .env غير موجود. سيتم الاعتماد على متغيرات البيئة المباشرة.")

# تحميل إعدادات إضافية من config.yaml إن وُجد
config_path = Path(__file__).resolve().parent / "config.yaml"
config = ConfigHandler(str(config_path)) if config_path.exists() else None

# 🧠 تحديد نوع قاعدة البيانات
DB_TYPE = os.getenv("DB_TYPE") or (config.get("database.type", default="sqlite") if config else "sqlite")
DB_TYPE = DB_TYPE.lower()

# 🔐 إعدادات PostgreSQL
POSTGRES_CONFIG = {
    "host": os.getenv("POSTGRES_HOST") or (config.get("database.postgres.host", default="localhost") if config else "localhost"),
    "port": int(os.getenv("POSTGRES_PORT") or (config.get("database.postgres.port", default=5432) if config else 5432)),
    "user": os.getenv("POSTGRES_USER") or (config.get("database.postgres.user", default="postgres") if config else "postgres"),
    "password": os.getenv("POSTGRES_PASSWORD") or (config.get("database.postgres.password", default="password") if config else "password"),
    "database": os.getenv("POSTGRES_DB") or (config.get("database.postgres.database", default="data_system") if config else "data_system"),
}


# 📦 إعداد SQLite
SQLITE_PATH = Path(
    os.getenv("SQLITE_PATH") or
    (config.get("database.sqlite.path") if config else Path(__file__).resolve().parent.parent / "data_intelligence_system/data/processed/clean_data.db")
)

# التأكد من وجود مجلد قاعدة البيانات
try:
    SQLITE_PATH.parent.mkdir(parents=True, exist_ok=True)
except Exception as e:
    logger.error(f"❌ فشل إنشاء مجلد قاعدة بيانات SQLite: {e}")

# 🧪 URI للاتصال بحسب النوع
def get_database_uri():
    if DB_TYPE == "postgresql":
        return (
            f"postgresql://{POSTGRES_CONFIG['user']}:{POSTGRES_CONFIG['password']}@"
            f"{POSTGRES_CONFIG['host']}:{POSTGRES_CONFIG['port']}/{POSTGRES_CONFIG['database']}"
        )
    elif DB_TYPE == "sqlite":
        return f"sqlite:///{SQLITE_PATH.as_posix()}"
    else:
        raise ValueError(f"❌ نوع قاعدة البيانات غير مدعوم: {DB_TYPE}")

# 🧾 ملخص عند التشغيل المباشر
if __name__ == "__main__":
    logger.info(f"🗄️ نوع قاعدة البيانات: {DB_TYPE}")
    logger.info(f"🧩 URI الاتصال: {get_database_uri()}")
