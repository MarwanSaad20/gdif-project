from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session, declarative_base
from typing import Generator

from data_intelligence_system.config.env_config import env_namespace
from data_intelligence_system.utils.logger import get_logger

logger = get_logger("database.session")

DATABASE_URL = env_namespace.DATABASE_URL

if not DATABASE_URL:
    raise RuntimeError("❌ متغير البيئة DATABASE_URL غير معرف! يرجى تعيينه بشكل صحيح.")

# يمكن تعديل echo بناءً على بيئة التشغيل (تفعيل التطوير)
ECHO_SQL = False  # أو استخدم env var للتحكم

try:
    engine = create_engine(DATABASE_URL, echo=ECHO_SQL, pool_pre_ping=True, future=True)
    logger.info("✅ تم إنشاء محرك قاعدة البيانات بنجاح.")
except Exception as e:
    logger.error(f"❌ فشل في إنشاء محرك قاعدة البيانات: {e}", exc_info=True)
    raise

SessionLocal = scoped_session(
    sessionmaker(autocommit=False, autoflush=False, bind=engine)
)

Base = declarative_base()

def get_db_session() -> Generator:
    """
    توليد جلسة قاعدة بيانات لاستخدامها مع FastAPI أو أنظمة حقن التبعيات.
    تقوم بإرجاع الجلسة وإغلاقها تلقائياً بعد الاستخدام.

    مثال للاستخدام مع FastAPI:
        async def endpoint(db: Session = Depends(get_db_session)):
            # استخدام db هنا
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
