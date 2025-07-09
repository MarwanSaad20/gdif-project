"""
utils/preprocessing.py

وصف:
    دوال المعالجة الأولية للبيانات (Preprocessing)، تُستخدم قبل التحليل أو النمذجة.
    تشمل:
        - توحيد أسماء الأعمدة
        - معالجة القيم المفقودة
        - ترميز البيانات النوعية
        - موازنة وتوحيد البيانات الرقمية

الاستخدام:
    from utils.preprocessing import (
        normalize_column_names,
        fill_missing_values,
        encode_categoricals,
        scale_numericals
    )

    df = normalize_column_names(df)
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder, StandardScaler
from typing import Optional, Union
from data_intelligence_system.utils.logger import get_logger


logger = get_logger(name="Preprocessing")


def normalize_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """
    توحيد أسماء الأعمدة لتكون صغيرة وخالية من الفراغات والرموز الخاصة.

    Parameters
    ----------
    df : pd.DataFrame
        إطار بيانات الإدخال.

    Returns
    -------
    pd.DataFrame
        نسخة من DataFrame مع أسماء أعمدة موحدة.
    
    Raises
    ------
    ValueError
        إذا كان df None أو فارغ.
    """
    if df is None or df.empty:
        raise ValueError("Input DataFrame is None or empty.")

    logger.info("🔤 توحيد أسماء الأعمدة...")
    df = df.copy()
    df.columns = (
        df.columns.str.strip()
                  .str.lower()
                  .str.replace(r'[^\w]+', '_', regex=True)
                  .str.strip('_')
    )
    return df


def fill_missing_values(data, strategy: str = "mean"):
    """
    معالجة القيم المفقودة باستخدام استراتيجية محددة.
    
    Parameters
    ----------
    data : pd.DataFrame أو pd.Series
        إطار بيانات أو سلسلة بيانات.
    strategy : str, optional
        استراتيجية الملء، الخيارات: 'mean', 'median', 'mode', 'zero' (الافتراضي 'mean').

    Returns
    -------
    pd.DataFrame أو pd.Series
        نسخة بعد ملء القيم المفقودة.

    Raises
    ------
    ValueError
        إذا كانت الاستراتيجية غير مدعومة أو البيانات None أو فارغة.
    """
    if data is None or (isinstance(data, (pd.DataFrame, pd.Series)) and data.empty):
        raise ValueError("Input data is None or empty.")

    allowed_strategies = {"mean", "median", "mode", "zero"}
    if strategy not in allowed_strategies:
        raise ValueError(f"استراتيجية ملء غير مدعومة: {strategy}. الرجاء اختيار واحدة من {allowed_strategies}")

    logger.info(f"🧩 معالجة القيم المفقودة باستخدام: {strategy}")
    data = data.copy()

    if isinstance(data, pd.Series):
        if data.isnull().sum() > 0:
            try:
                if strategy == "mean" and pd.api.types.is_numeric_dtype(data):
                    if data.dropna().empty:
                        logger.warning("⚠️ السلسلة لا تحتوي على قيم صالحة لحساب المتوسط.")
                        return data
                    return data.fillna(data.mean())
                elif strategy == "median" and pd.api.types.is_numeric_dtype(data):
                    if data.dropna().empty:
                        logger.warning("⚠️ السلسلة لا تحتوي على قيم صالحة لحساب الوسيط.")
                        return data
                    return data.fillna(data.median())
                elif strategy == "mode":
                    mode_vals = data.mode()
                    if mode_vals.empty:
                        logger.warning("⚠️ السلسلة لا تحتوي على قيم صالحة لحساب الوضع (mode).")
                        return data
                    return data.fillna(mode_vals[0])
                elif strategy == "zero":
                    return data.fillna(0)
                else:
                    logger.warning(f"⚠️ لا يمكن تطبيق استراتيجية {strategy} على السلسلة.")
            except Exception as e:
                logger.error(f"❌ خطأ أثناء ملء السلسلة: {e}")
                raise
        return data

    elif isinstance(data, pd.DataFrame):
        for col in data.columns:
            if data[col].isnull().sum() > 0:
                try:
                    if strategy == "mean" and pd.api.types.is_numeric_dtype(data[col]):
                        if data[col].dropna().empty:
                            logger.warning(f"⚠️ العمود '{col}' لا يحتوي على قيم صالحة لحساب المتوسط.")
                            continue
                        data[col] = data[col].fillna(data[col].mean())
                    elif strategy == "median" and pd.api.types.is_numeric_dtype(data[col]):
                        if data[col].dropna().empty:
                            logger.warning(f"⚠️ العمود '{col}' لا يحتوي على قيم صالحة لحساب الوسيط.")
                            continue
                        data[col] = data[col].fillna(data[col].median())
                    elif strategy == "mode":
                        mode_vals = data[col].mode()
                        if mode_vals.empty:
                            logger.warning(f"⚠️ العمود '{col}' لا يحتوي على قيم صالحة لحساب الوضع (mode).")
                            continue
                        data[col] = data[col].fillna(mode_vals[0])
                    elif strategy == "zero":
                        data[col] = data[col].fillna(0)
                    else:
                        logger.warning(f"⚠️ لا يمكن تطبيق استراتيجية {strategy} على العمود '{col}'")
                except Exception as e:
                    logger.error(f"❌ خطأ أثناء ملء العمود '{col}': {e}")
                    raise
        return data
    else:
        raise TypeError("❌ نوع البيانات غير مدعوم. يجب أن يكون DataFrame أو Series.")



def encode_categoricals(df: pd.DataFrame, method: str = "label") -> pd.DataFrame:
    """
    ترميز الأعمدة النوعية (Categorical) باستخدام إما LabelEncoder أو OneHotEncoding.

    Parameters
    ----------
    df : pd.DataFrame
        إطار بيانات الإدخال.
    method : str, optional
        طريقة الترميز: 'label' أو 'onehot' (الافتراضي 'label').

    Returns
    -------
    pd.DataFrame
        نسخة من DataFrame بعد الترميز.

    Raises
    ------
    ValueError
        إذا لم توجد أعمدة نوعية أو طريقة الترميز غير مدعومة.
    """
    if df is None or df.empty:
        raise ValueError("Input DataFrame is None or empty.")

    df = df.copy()
    cat_cols = df.select_dtypes(include=['object', 'category']).columns

    if len(cat_cols) == 0:
        logger.warning("⚠️ لا توجد أعمدة نوعية (categorical) في البيانات للترميز.")
        return df  # مرونة أفضل من رفع استثناء

    logger.info(f"🔠 ترميز الأعمدة النوعية باستخدام: {method}")

    if method == "label":
        for col in cat_cols:
            try:
                le = LabelEncoder()
                df[col] = le.fit_transform(df[col].astype(str))
            except Exception as e:
                logger.error(f"❌ فشل ترميز العمود '{col}': {e}")
                raise

    elif method == "onehot":
        try:
            df = pd.get_dummies(df, columns=cat_cols, drop_first=True)
        except Exception as e:
            logger.error(f"❌ فشل OneHot Encoding: {e}")
            raise

    else:
        logger.warning(f"⚠️ طريقة ترميز غير معروفة: {method}")
        raise ValueError("طريقة الترميز غير مدعومة. استخدم 'label' أو 'onehot'.")

    return df


import logging
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from typing import Optional, Union

logger = logging.getLogger(__name__)

def scale_numericals(
    df: pd.DataFrame,
    scaler: Optional[Union[str, object]] = None
) -> pd.DataFrame:
    """
    موازنة الأعمدة الرقمية باستخدام StandardScaler أو scaler مخصص أو اختيار عبر سلسلة نصية.

    Parameters
    ----------
    df : pd.DataFrame
        إطار بيانات الإدخال.
    scaler : str or object, optional
        يمكن أن يكون:
        - None: يستخدم StandardScaler.
        - str: "standard" أو "minmax" لتحديد نوع الscaler.
        - كائن scaler (مثل StandardScaler)، يستخدم مباشرة.

    Returns
    -------
    pd.DataFrame
        نسخة من DataFrame بعد الموازنة.

    Raises
    ------
    Exception
        في حالة فشل عملية الموازنة.
    """
    if df is None or df.empty:
        raise ValueError("Input DataFrame is None or empty.")

    df = df.copy()
    num_cols = df.select_dtypes(include=[np.number]).columns

    if len(num_cols) == 0:
        logger.warning("⚠️ لا توجد أعمدة رقمية لموازنتها.")
        return df

    if scaler is None:
        scaler_obj = StandardScaler()
    elif isinstance(scaler, str):
        if scaler.lower() == "standard":
            scaler_obj = StandardScaler()
        elif scaler.lower() == "minmax":
            scaler_obj = MinMaxScaler()
        else:
            raise ValueError(f"نوع الscaler غير مدعوم: {scaler}")
    else:
        # نفترض أنه كائن scaler جاهز
        scaler_obj = scaler

    try:
        df[num_cols] = scaler_obj.fit_transform(df[num_cols])
    except Exception as e:
        logger.error(f"❌ فشل في موازنة الأعمدة الرقمية: {e}")
        raise

    return df

