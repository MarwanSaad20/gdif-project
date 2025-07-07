import pandas as pd
from typing import List, Optional, Callable, Union
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("ExternalDataUtils")


def drop_empty_rows(df: pd.DataFrame) -> pd.DataFrame:
    """حذف الصفوف التي تحتوي على قيم NaN بالكامل."""
    if df.empty:
        logger.warning("⚠️ DataFrame فارغ في drop_empty_rows.")
        return df
    return df.dropna(how='all')


def drop_empty_columns(df: pd.DataFrame) -> pd.DataFrame:
    """حذف الأعمدة التي تحتوي على قيم NaN بالكامل."""
    if df.empty:
        logger.warning("⚠️ DataFrame فارغ في drop_empty_columns.")
        return df
    return df.dropna(axis=1, how='all')


def fill_missing_values(
    df: pd.DataFrame,
    strategy: Union[str, int, float] = "mean",
    columns: Optional[List[str]] = None
) -> pd.DataFrame:
    """
    تعبئة القيم المفقودة باستراتيجية:
    - mean / median / mode
    - قيمة ثابتة

    :param df: DataFrame
    :param strategy: "mean" | "median" | "mode" | قيمة ثابتة
    :param columns: الأعمدة المستهدفة
    :return: DataFrame بعد التعبئة
    """
    if df.empty:
        logger.warning("⚠️ DataFrame فارغ في fill_missing_values.")
        return df

    cols = columns if columns else df.columns

    for col in cols:
        if col not in df.columns:
            logger.warning(f"⚠️ العمود غير موجود: {col}")
            continue

        try:
            if strategy == "mean" and pd.api.types.is_numeric_dtype(df[col]):
                df[col] = df[col].fillna(df[col].mean())
            elif strategy == "median" and pd.api.types.is_numeric_dtype(df[col]):
                df[col] = df[col].fillna(df[col].median())
            elif strategy == "mode":
                mode_val = df[col].mode()
                if not mode_val.empty:
                    df[col] = df[col].fillna(mode_val[0])
                else:
                    df[col] = df[col].fillna(method='ffill')
            else:
                df[col] = df[col].fillna(strategy)
        except Exception as e:
            logger.error(f"❌ فشل تعبئة العمود '{col}': {e}")
    return df


def standardize_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """توحيد أسماء الأعمدة: lowercase + _ بدلاً من المسافات"""
    if df.empty:
        logger.warning("⚠️ DataFrame فارغ في standardize_column_names.")
        return df
    df.columns = [str(col).strip().lower().replace(" ", "_") for col in df.columns]
    return df


def remove_duplicates(df: pd.DataFrame, subset: Optional[List[str]] = None) -> pd.DataFrame:
    """إزالة الصفوف المكررة حسب أعمدة محددة أو الجدول الكامل"""
    if df.empty:
        logger.warning("⚠️ DataFrame فارغ في remove_duplicates.")
        return df
    return df.drop_duplicates(subset=subset)


def convert_column_types(df: pd.DataFrame, col_types: dict) -> pd.DataFrame:
    """
    تحويل أنواع البيانات لأعمدة معينة
    :param col_types: dict مثل {'year': int, 'price': float}
    :return: DataFrame بعد التحويل
    """
    if df.empty:
        logger.warning("⚠️ DataFrame فارغ في convert_column_types.")
        return df

    for col, dtype in col_types.items():
        if col in df.columns:
            try:
                df[col] = df[col].astype(dtype)
            except Exception as e:
                logger.warning(f"⚠️ فشل تحويل '{col}' إلى {dtype}: {e}")
        else:
            logger.warning(f"⚠️ العمود غير موجود: {col}")
    return df


def filter_rows_by_condition(df: pd.DataFrame, condition: Callable[[pd.DataFrame], pd.Series]) -> pd.DataFrame:
    """تصفية الصفوف بناءً على شرط"""
    if df.empty:
        logger.warning("⚠️ DataFrame فارغ في filter_rows_by_condition.")
        return df
    try:
        filtered = df.loc[condition(df)]
        return filtered
    except Exception as e:
        logger.error(f"❌ فشل تطبيق شرط التصفية: {e}")
        return df


def sample_data(df: pd.DataFrame, frac: float = 0.1, random_state: Optional[int] = None) -> pd.DataFrame:
    """أخذ عينة من البيانات بنسبة معينة"""
    if df.empty:
        logger.warning("⚠️ DataFrame فارغ في sample_data.")
        return df
    try:
        return df.sample(frac=frac, random_state=random_state)
    except Exception as e:
        logger.error(f"❌ فشل أخذ العينة: {e}")
        return df


def describe_data(df: pd.DataFrame) -> pd.DataFrame:
    """عرض إحصائيات وصفية عامة"""
    if df.empty:
        logger.warning("⚠️ DataFrame فارغ في describe_data.")
        return df
    return df.describe(include='all')
