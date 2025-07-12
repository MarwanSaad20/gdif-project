# data_intelligence_system/database/session.py

import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session, declarative_base

from data_intelligence_system.config.env_config import env_namespace

# ======================== إعدادات تسجيل الدخول ==========================
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

if not logger.hasHandlers():
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

# ======================== إعداد رابط قاعدة البيانات ==========================
DATABASE_URL = env_namespace.DATABASE_URL

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
