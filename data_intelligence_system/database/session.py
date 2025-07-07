# database/session.py

import os
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.orm import declarative_base

# ======================== إعدادات تسجيل الدخول ==========================
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

if not logger.hasHandlers():
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

# ======================== إعداد رابط قاعدة البيانات ==========================
# من الأفضل الاعتماد على ملف .env أو ملف إعدادات مركزي
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/gdif_db")

# ======================== إنشاء محرك قاعدة البيانات ==========================
try:
    engine = create_engine(DATABASE_URL, echo=False, pool_pre_ping=True)
    logger.info("✅ تم إنشاء محرك قاعدة البيانات بنجاح.")
except Exception as e:
    logger.error(f"❌ فشل في إنشاء محرك قاعدة البيانات: {e}", exc_info=True)
    raise

# ======================== إعداد الجلسة ==========================
SessionLocal = scoped_session(
    sessionmaker(autocommit=False, autoflush=False, bind=engine)
)

# ======================== تعريف قاعدة ORM ==========================
Base = declarative_base()

# ======================== دالة للحصول على الجلسة ==========================
def get_db_session():
    """
    Generator function تُعيد جلسة قاعدة بيانات وتُغلقها تلقائيًا بعد الاستخدام.
    مثالية في حالات FastAPI أو أي نظام يعتمد حقن التبعيات.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
