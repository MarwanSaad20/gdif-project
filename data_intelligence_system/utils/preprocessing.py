import os
import json
import logging
from pathlib import Path
from typing import Optional

import pandas as pd

# ✅ تحديث الاستيراد لدالة الحفظ من utils.file_manager وليس etl.load
from data_intelligence_system.utils.file_manager import save_file
from data_intelligence_system.utils.preprocessing import fill_missing_values  # ✅ الصحيح

logger = logging.getLogger(__name__)

# ======== المسارات الرئيسية ========
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / 'data'
PROFILES_DIR = BASE_DIR / 'data_profiles'


# ======== تحويل DataFrame إلى JSON بصيغة Dash ========
def df_to_dash_json(df: Optional[pd.DataFrame], orient: str = "split") -> str:
    if df is None or df.empty:
        logger.warning("⚠️ DataFrame فارغ أو None عند التحويل إلى JSON.")
        return json.dumps({}, default=str)

    try:
        df_copy = df.copy()
        for col in df_copy.select_dtypes(include=["datetime", "datetimetz"]).columns:
            df_copy[col] = df_copy[col].dt.strftime("%Y-%m-%d")

        json_str = df_copy.to_json(orient=orient, date_format='iso', default_handler=str)
        logger.info("✅ تم تحويل DataFrame إلى JSON (orient=%s) بنجاح.", orient)
        return json_str
    except Exception as e:
        logger.error(f"❌ فشل تحويل DataFrame إلى JSON: {e}", exc_info=True)
        return json.dumps({}, default=str)


# ======== تحويل JSON إلى DataFrame ========
def json_to_df(data_json: Optional[str], parse_dates: bool = True) -> Optional[pd.DataFrame]:
    if not data_json or data_json.strip() in ('{}', ''):
        logger.warning("⚠️ JSON فارغ أو غير صالح.")
        return None

    try:
        df = pd.read_json(data_json, orient='split')
        if df.empty:
            logger.warning("⚠️ DataFrame الناتج فارغ بعد التحويل من JSON.")
            return None

        if parse_dates:
            for col in df.columns:
                if df[col].dtype == object:
                    converted = pd.to_datetime(df[col], errors='coerce')
                    if not converted.isnull().all():
                        df[col] = converted

        df = fill_missing_values(df)  # ✅ تم التصحيح هنا

        logger.info("✅ تم تحويل JSON إلى DataFrame (split) بنجاح.")
        return df
    except Exception as e:
        logger.error(f"❌ فشل تحويل JSON إلى DataFrame: {e}", exc_info=True)
        return None


# ======== تصفية DataFrame حسب التاريخ ========
def filter_data_by_date(
    df: pd.DataFrame,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    date_column: str = "date"
) -> pd.DataFrame:
    if date_column not in df.columns:
        logger.warning(f"⚠️ عمود التاريخ '{date_column}' غير موجود في DataFrame، سيتم إرجاع البيانات بدون فلترة.")
        return df

    df = df.copy()
    df[date_column] = pd.to_datetime(df[date_column], errors='coerce')

    if start_date:
        try:
            df = df[df[date_column] >= pd.to_datetime(start_date)]
        except Exception as e:
            logger.warning(f"⚠️ تاريخ بداية غير صالح '{start_date}': {e}")

    if end_date:
        try:
            df = df[df[date_column] <= pd.to_datetime(end_date)]
        except Exception as e:
            logger.warning(f"⚠️ تاريخ نهاية غير صالح '{end_date}': {e}")

    return df


# ======== قراءة ملف Excel أو CSV حسب الامتداد ========
def read_file(path: Path) -> pd.DataFrame:
    if not path.exists():
        logger.error(f"❌ الملف غير موجود: {path}")
        raise FileNotFoundError(f"❌ الملف غير موجود: {path}")

    try:
        if path.suffix.lower() == '.csv':
            try:
                return pd.read_csv(path, encoding='utf-8')
            except UnicodeDecodeError:
                return pd.read_csv(path, encoding='cp1256')
        elif path.suffix.lower() in ['.xlsx', '.xls']:
            return pd.read_excel(path)
        else:
            raise ValueError(f"❌ امتداد غير مدعوم: {path.suffix}")
    except Exception as e:
        logger.error(f"❌ فشل قراءة الملف {path}: {e}", exc_info=True)
        raise


# ======== تحميل البيانات الخام ========
def load_raw_data(filename: str) -> pd.DataFrame:
    return read_file(DATA_DIR / filename)


# ======== تحميل البيانات المعالجة المحفوظة مسبقًا ========
def load_saved_data(filename: str = "uploaded.csv") -> pd.DataFrame:
    return read_file(DATA_DIR / "processed" / filename)
