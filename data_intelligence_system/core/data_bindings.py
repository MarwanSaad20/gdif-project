import json
import logging
from pathlib import Path
from typing import Optional

import pandas as pd

from data_intelligence_system.utils.preprocessing import fill_missing_values  # ✅ صحيح الاستخدام

logger = logging.getLogger(__name__)

# ======== المسارات الرئيسية ========
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / 'data'
PROFILES_DIR = BASE_DIR / 'data_profiles'


def df_to_dash_json(df: Optional[pd.DataFrame], orient: str = "split") -> str:
    """
    تحويل DataFrame إلى JSON مناسب لـ Dash.

    Args:
        df (Optional[pd.DataFrame]): إطار البيانات للتحويل.
        orient (str): طريقة تنظيم JSON (default "split").

    Returns:
        str: سلسلة JSON.
    """
    if df is None or df.empty:
        logger.warning("⚠️ DataFrame فارغ أو None عند التحويل إلى JSON.")
        return json.dumps({}, default=str)

    try:
        df_copy = df.copy()
        datetime_cols = df_copy.select_dtypes(include=["datetime", "datetimetz"]).columns
        for col in datetime_cols:
            df_copy[col] = df_copy[col].dt.strftime("%Y-%m-%d")

        json_str = df_copy.to_json(orient=orient, date_format='iso', default_handler=str)
        logger.info("✅ تم تحويل DataFrame إلى JSON (orient=%s) بنجاح.", orient)
        return json_str
    except Exception as e:
        logger.error(f"❌ فشل تحويل DataFrame إلى JSON: {e}", exc_info=True)
        return json.dumps({}, default=str)


def json_to_df(data_json: Optional[str], parse_dates: bool = True) -> Optional[pd.DataFrame]:
    """
    تحويل JSON (بصيغة split) إلى DataFrame.

    Args:
        data_json (Optional[str]): نص JSON.
        parse_dates (bool): محاولة تحويل الأعمدة إلى تواريخ (default True).

    Returns:
        Optional[pd.DataFrame]: DataFrame أو None إذا فشل.
    """
    if not data_json or data_json.strip() in ('{}', ''):
        logger.warning("⚠️ JSON فارغ أو غير صالح.")
        return None

    try:
        df = pd.read_json(data_json, orient='split')
        if df.empty:
            logger.warning("⚠️ DataFrame الناتج فارغ بعد التحويل من JSON.")
            return None

        if parse_dates:
            # محاولة تحويل الأعمدة التي تحتوي على نصوص إلى تواريخ دفعة واحدة
            obj_cols = df.select_dtypes(include=['object']).columns
            for col in obj_cols:
                converted = pd.to_datetime(df[col], errors='coerce')
                if not converted.isnull().all():
                    df[col] = converted

        df = fill_missing_values(df)
        logger.info("✅ تم تحويل JSON إلى DataFrame (split) بنجاح.")
        return df
    except Exception as e:
        logger.error(f"❌ فشل تحويل JSON إلى DataFrame: {e}", exc_info=True)
        return None


def filter_data_by_date(
    df: pd.DataFrame,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    date_column: str = "date"
) -> pd.DataFrame:
    """
    تصفية DataFrame حسب نطاق زمني محدد.

    Args:
        df (pd.DataFrame): إطار البيانات.
        start_date (Optional[str]): تاريخ البدء (ISO أو قابل للتحويل).
        end_date (Optional[str]): تاريخ النهاية (ISO أو قابل للتحويل).
        date_column (str): اسم عمود التاريخ (default "date").

    Returns:
        pd.DataFrame: نسخة مفلترة من DataFrame.
    """
    if date_column not in df.columns:
        logger.warning(f"⚠️ عمود التاريخ '{date_column}' غير موجود في DataFrame، سيتم إرجاع البيانات بدون فلترة.")
        return df

    df_filtered = df.copy()
    df_filtered[date_column] = pd.to_datetime(df_filtered[date_column], errors='coerce')

    if start_date:
        try:
            start = pd.to_datetime(start_date)
            df_filtered = df_filtered[df_filtered[date_column] >= start]
        except Exception as e:
            logger.warning(f"⚠️ تاريخ بداية غير صالح '{start_date}': {e}")

    if end_date:
        try:
            end = pd.to_datetime(end_date)
            df_filtered = df_filtered[df_filtered[date_column] <= end]
        except Exception as e:
            logger.warning(f"⚠️ تاريخ نهاية غير صالح '{end_date}': {e}")

    return df_filtered


def read_file(path: Path) -> pd.DataFrame:
    """
    قراءة ملف CSV أو Excel إلى DataFrame.

    Args:
        path (Path): مسار الملف.

    Raises:
        FileNotFoundError: إذا لم يوجد الملف.
        ValueError: إذا كان الامتداد غير مدعوم.
        Exception: أي خطأ آخر في القراءة.

    Returns:
        pd.DataFrame: البيانات المقروءة.
    """
    if not path.exists():
        logger.error(f"❌ الملف غير موجود: {path}")
        raise FileNotFoundError(f"❌ الملف غير موجود: {path}")

    try:
        suffix = path.suffix.lower()
        if suffix == '.csv':
            try:
                return pd.read_csv(path, encoding='utf-8')
            except UnicodeDecodeError:
                return pd.read_csv(path, encoding='cp1256')
        elif suffix in ['.xlsx', '.xls']:
            return pd.read_excel(path)
        else:
            raise ValueError(f"❌ امتداد غير مدعوم: {suffix}")
    except Exception as e:
        logger.error(f"❌ فشل قراءة الملف {path}: {e}", exc_info=True)
        raise


def load_raw_data(filename: str) -> pd.DataFrame:
    """
    تحميل بيانات خام من مجلد البيانات.

    Args:
        filename (str): اسم ملف البيانات.

    Returns:
        pd.DataFrame: البيانات المحملة.
    """
    return read_file(DATA_DIR / filename)


def load_saved_data(filename: str = "uploaded.csv") -> pd.DataFrame:
    """
    تحميل بيانات معالجة محفوظة مسبقًا.

    Args:
        filename (str): اسم الملف (افتراضي "uploaded.csv").

    Returns:
        pd.DataFrame: البيانات المحملة.
    """
    return read_file(DATA_DIR / "processed" / filename)
