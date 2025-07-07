import logging
from typing import List, Tuple, Union

import numpy as np
import pandas as pd
from sklearn.preprocessing import LabelEncoder

from data_intelligence_system.data.processed.fill_missing import fill_missing
from data_intelligence_system.data.processed.scale_numericals import scale_numericals
from data_intelligence_system.etl.etl_utils import log_step  # ✅ تم تحديث الاستيراد ليكون من جذر المشروع

logger = logging.getLogger(__name__)


def unify_column_names(df: pd.DataFrame) -> pd.DataFrame:
    if df is None or df.empty:
        logger.warning("⚠️ DataFrame فارغ أو None في unify_column_names.")
        return df

    df = df.copy()
    df.columns = (
        df.columns.str.strip()
                  .str.lower()
                  .str.replace(r'[^\w]+', '_', regex=True)
                  .str.strip('_')
    )
    logger.info(f"✅ توحيد أسماء الأعمدة: {df.columns.tolist()}")
    return df


def encode_categorical_columns(df: pd.DataFrame, encode_type: str = 'label') -> pd.DataFrame:
    if df is None or df.empty:
        logger.warning("⚠️ DataFrame فارغ أو None في encode_categorical_columns.")
        return df

    df = df.copy()
    cat_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
    logger.info(f"🔍 الأعمدة الفئوية قبل الترميز: {cat_cols}")

    for col in cat_cols:
        df[col] = df[col].apply(lambda x: str(x) if isinstance(x, (list, dict)) else x)

    if encode_type == 'label':
        for col in cat_cols:
            try:
                le = LabelEncoder()
                df[col] = le.fit_transform(df[col].astype(str))
                logger.info(f"✅ تم ترميز {col} باستخدام LabelEncoder")
            except Exception as e:
                logger.error(f"❌ خطأ في ترميز {col}: {e}")

    elif encode_type == 'onehot':
        one_hot_cols = []
        skipped_cols = []

        for col in cat_cols:
            unique_vals = df[col].nunique()
            if unique_vals <= 1000:
                one_hot_cols.append(col)
            else:
                skipped_cols.append((col, unique_vals))
                logger.warning(f"⛔ تجاهل العمود '{col}' لاحتوائه على {unique_vals} قيمة فريدة (تجاوز الحد 1000)")

        try:
            if one_hot_cols:
                df = pd.get_dummies(df, columns=one_hot_cols, drop_first=True)
                logger.info(f"✅ تم تطبيق One-Hot Encoding على الأعمدة: {one_hot_cols}")
            else:
                logger.info("ℹ️ لا يوجد أعمدة مؤهلة لتطبيق One-Hot Encoding.")
        except Exception as e:
            logger.error(f"❌ فشل في تطبيق One-Hot Encoding: {e}")
            raise
    else:
        logger.warning(f"⚠️ نوع الترميز غير معروف: {encode_type}")

    return df


def remove_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    if df is None or df.empty:
        logger.warning("⚠️ DataFrame فارغ أو None في remove_duplicates.")
        return df

    df = df.copy()
    before = len(df)
    df = df.drop_duplicates()
    after = len(df)
    logger.info(f"✅ حذف التكرارات: {before - after} صفوف مكررة")
    return df


@log_step
def transform_datasets(
    datasets: List[Tuple[str, pd.DataFrame]],
    encode_type: str = 'label',
    scale_type: str = 'standard',
) -> List[Tuple[str, pd.DataFrame]]:
    transformed = []

    if not datasets:
        logger.warning("⚠️ قائمة datasets فارغة أو None في transform_datasets.")
        return transformed

    for name, df in datasets:
        if df is None or df.empty:
            logger.warning(f"⚠️ DataFrame فارغ أو None في transform_datasets للملف {name}.")
            continue

        logger.info(f"🚧 بدء التحويل: {name}")
        logger.info(f"📊 حجم البيانات الأصلية: {df.shape}")

        df = unify_column_names(df)
        df = fill_missing(df)
        df = encode_categorical_columns(df, encode_type=encode_type)
        df = scale_numericals(df)
        df = remove_duplicates(df)

        logger.info(f"✅ تم الانتهاء من تحويل: {name} | الحجم النهائي: {df.shape}")
        transformed.append((name, df))

    return transformed


@log_step
def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    return transform_datasets([("clean_data", df)], encode_type='label')[0][1]
