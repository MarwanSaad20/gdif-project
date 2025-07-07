# config/db_config.py

import os
from pathlib import Path
from dotenv import load_dotenv

# تحميل متغيرات البيئة من ملف .env (إذا كان موجودًا)
env_path = Path(__file__).resolve().parent.parent / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path)
else:
    print("⚠️ ملف .env غير موجود. سيتم الاعتماد على متغيرات البيئة المباشرة.")

# 🧠 تحديد نوع قاعدة البيانات المستخدمة
DB_TYPE = os.getenv("DB_TYPE", "sqlite").lower()  # الخيارات: "sqlite", "postgresql"

# 🔐 إعدادات اتصال PostgreSQL (تُستخدم إذا DB_TYPE = postgresql)
POSTGRES_CONFIG = {
    "host": os.getenv("POSTGRES_HOST", "localhost"),
    "port": int(os.getenv("POSTGRES_PORT", 5432)),
    "user": os.getenv("POSTGRES_USER", "postgres"),
    "password": os.getenv("POSTGRES_PASSWORD", "password"),
    "database": os.getenv("POSTGRES_DB", "data_system"),
}

# 📦 إعداد SQLite (بديل محلي بسيط)
SQLITE_PATH = Path(__file__).resolve().parent.parent / "data_intelligence_system" / "data" / "processed" / "clean_data.db"

# التأكد من وجود مجلد قاعدة بيانات SQLite
try:
    SQLITE_PATH.parent.mkdir(parents=True, exist_ok=True)
except Exception as e:
    print(f"❌ فشل إنشاء مجلد قاعدة بيانات SQLite: {e}")

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
        raise ValueError(f"نوع قاعدة البيانات غير مدعوم: {DB_TYPE}")

# 🧾 ملخص الإعدادات عند التشغيل المباشر
if __name__ == "__main__":
    print(f"🗄️ نوع قاعدة البيانات: {DB_TYPE}")
    print(f"🧩 URI الاتصال: {get_database_uri()}")
