from pathlib import Path
import pandas as pd
import logging

# إعداد الـ Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)

logger = logging.getLogger(__name__)

# المسار الافتراضي لملف البيانات النظيفة
DEFAULT_CLEAN_DATA_PATH = Path("data") / "processed" / "clean_data.csv"


def load_clean_data(path: Path | str = DEFAULT_CLEAN_DATA_PATH, **kwargs) -> pd.DataFrame:
    """
    تحميل البيانات النظيفة من المسار المحدد.

    Args:
        path (Path | str): مسار ملف CSV.
        **kwargs: خيارات إضافية لتمريرها إلى pd.read_csv().

    Returns:
        pd.DataFrame: البيانات النظيفة كـ DataFrame.
    """
    path = Path(path)
    logger.info(f"📥 جاري تحميل البيانات من: {path}")

    if not path.exists():
        logger.error(f"❌ لم يتم العثور على الملف: {path}")
        raise FileNotFoundError(f"File not found: {path}")

    try:
        df = pd.read_csv(path, encoding='utf-8', **kwargs)

        # التحقق من أن البيانات ليست فارغة تمامًا
        if df.empty or df.shape[1] == 0:
            logger.error(f"⚠️ الملف موجود لكنه فارغ أو لا يحتوي على أعمدة: {path}")
            raise ValueError(f"Data file is empty or has no columns: {path}")

        logger.info(f"✅ تم تحميل البيانات بنجاح. الصفوف: {len(df)}, الأعمدة: {len(df.columns)}")
        return df

    except pd.errors.EmptyDataError:
        logger.error(f"⚠️ الملف فارغ تمامًا: {path}")
        raise ValueError(f"Data file is completely empty: {path}")

    except Exception as e:
        logger.exception("❌ حدث خطأ غير متوقع أثناء تحميل البيانات")
        raise e


def preview_dataframe(df: pd.DataFrame, rows: int = 5):
    """
    طباعة نظرة سريعة على البيانات.

    Args:
        df (pd.DataFrame): إطار البيانات.
        rows (int): عدد الصفوف لعرضها.
    """
    logger.info(f"🔍 عرض أول {rows} صفوف من البيانات:")
    print(df.head(rows))
    print(f"\n📐 الشكل: {df.shape}")


def select_columns(df: pd.DataFrame, columns: list) -> pd.DataFrame:
    """
    تحديد أعمدة محددة من إطار البيانات.

    Args:
        df (pd.DataFrame): إطار البيانات.
        columns (list): قائمة الأعمدة المطلوبة.

    Returns:
        pd.DataFrame: إطار بيانات بالأعمدة المختارة.
    """
    logger.info(f"📦 اختيار الأعمدة: {columns}")
    missing_cols = [col for col in columns if col not in df.columns]
    if missing_cols:
        logger.warning(f"⚠️ الأعمدة التالية غير موجودة: {missing_cols}")
    return df[[col for col in columns if col in df.columns]]
