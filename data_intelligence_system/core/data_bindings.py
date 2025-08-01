import json
from pathlib import Path
from typing import Optional
import pandas as pd
from io import StringIO  # استيراد StringIO لتحويل النص إلى كائن يشبه الملف
from data_intelligence_system.utils.preprocessing import fill_missing_values
from data_intelligence_system.utils.logger import get_logger  # ✅ توحيد نظام اللوجر

logger = get_logger(__name__)

# ======== المسارات الرئيسية ========
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / 'data'
PROFILES_DIR = BASE_DIR / 'data_profiles'


def df_to_dash_json(df: Optional[pd.DataFrame], orient: str = "split") -> str:
    if df is None or df.empty:
        logger.warning("⚠️ DataFrame فارغ أو None عند التحويل إلى JSON.")
        return json.dumps({"message": "لا توجد بيانات لعرضها."}, default=str)

    try:
        df_copy = df.copy()
        # تحديد الأعمدة التي تحتوي على تواريخ وتنسيقها
        datetime_cols = df_copy.select_dtypes(include=["datetime", "datetimetz"]).columns
        for col in datetime_cols:
            df_copy[col] = df_copy[col].dt.strftime("%Y-%m-%d")  # تنسيق التاريخ إلى (YYYY-MM-DD)

        json_str = df_copy.to_json(orient=orient, date_format='iso', default_handler=str)
        logger.info("✅ تم تحويل DataFrame إلى JSON (orient=%s) بنجاح.", orient)
        return json_str
    except Exception as e:
        logger.error(f"❌ فشل تحويل DataFrame إلى JSON: {e}", exc_info=True)
        return json.dumps({"message": "حدث خطأ أثناء التحويل إلى JSON."}, default=str)


def json_to_df(data_json: Optional[str], parse_dates: bool = True, date_format: str = "%Y-%m-%d") -> Optional[pd.DataFrame]:
    if not data_json or data_json.strip() in ('{}', ''):
        logger.warning("⚠️ JSON فارغ أو غير صالح.")
        return None

    try:
        # استخدام StringIO لتحويل نص JSON إلى كائن يشبه الملف
        json_file = StringIO(data_json)

        # قراءة البيانات من json_file باستخدام pandas
        df = pd.read_json(json_file, orient='split')
        if df.empty:
            logger.warning("⚠️ DataFrame الناتج فارغ بعد التحويل من JSON.")
            return None

        if parse_dates:
            obj_cols = df.select_dtypes(include=['object']).columns
            for col in obj_cols:
                # تحديد تنسيق التاريخ بشكل يدوي
                converted = pd.to_datetime(df[col], format=date_format, errors='coerce')
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
    date_column: str = "date",
    date_format: str = "%Y-%m-%d"  # إضافة معامل لتحديد تنسيق التاريخ
) -> pd.DataFrame:
    if date_column not in df.columns:
        logger.warning(f"⚠️ عمود التاريخ '{date_column}' غير موجود في DataFrame، سيتم إرجاع البيانات بدون فلترة.")
        return df

    df_filtered = df.copy()
    # تحديد تنسيق التاريخ بشكل يدوي أثناء تحويل العمود
    df_filtered[date_column] = pd.to_datetime(df_filtered[date_column], format=date_format, errors='coerce')

    if start_date:
        try:
            start = pd.to_datetime(start_date, format=date_format)
            df_filtered = df_filtered[df_filtered[date_column] >= start]
        except Exception as e:
            logger.warning(f"⚠️ تاريخ بداية غير صالح '{start_date}': {e}")

    if end_date:
        try:
            end = pd.to_datetime(end_date, format=date_format)
            df_filtered = df_filtered[df_filtered[date_column] <= end]
        except Exception as e:
            logger.warning(f"⚠️ تاريخ نهاية غير صالح '{end_date}': {e}")

    if df_filtered.empty:
        logger.warning("⚠️ البيانات بعد الفلترة حسب التاريخ فارغة.")
    return df_filtered


def read_file(path: Path) -> pd.DataFrame:
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
    return read_file(DATA_DIR / filename)


def load_saved_data(filename: str = "uploaded.csv") -> pd.DataFrame:
    return read_file(DATA_DIR / "processed" / filename)
