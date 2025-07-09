import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder, StandardScaler
from typing import Optional
from data_intelligence_system.utils.logger import get_logger

logger = get_logger(name="Preprocessing")


def normalize_column_names(df: pd.DataFrame) -> pd.DataFrame:
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


def fill_missing_values(df: Union[pd.DataFrame, pd.Series], strategy: str = "mean") -> Union[pd.DataFrame, pd.Series]:
    if df is None or (isinstance(df, pd.DataFrame) and df.empty) or (isinstance(df, pd.Series) and df.empty):
        raise ValueError("Input is None or empty.")

    allowed_strategies = {"mean", "median", "mode", "zero"}
    if strategy not in allowed_strategies:
        raise ValueError(f"استراتيجية ملء غير مدعومة: {strategy}. الرجاء اختيار واحدة من {allowed_strategies}")

    logger.info(f"🧩 معالجة القيم المفقودة باستخدام: {strategy}")

    if isinstance(df, pd.Series):
        if df.isnull().sum() == 0:
            return df
        if strategy == "mean" and pd.api.types.is_numeric_dtype(df):
            return df.fillna(df.mean())
        elif strategy == "median" and pd.api.types.is_numeric_dtype(df):
            return df.fillna(df.median())
        elif strategy == "mode":
            mode_vals = df.mode()
            if not mode_vals.empty:
                return df.fillna(mode_vals[0])
            else:
                logger.warning("⚠️ السلسلة لا تحتوي على قيم صالحة لحساب الوضع (mode).")
                return df
        elif strategy == "zero":
            return df.fillna(0)
        else:
            logger.warning(f"⚠️ لا يمكن تطبيق استراتيجية {strategy} على السلسلة.")
            return df

    # التعامل مع DataFrame كالسابق
    df = df.copy()
    for col in df.columns:
        if df[col].isnull().sum() > 0:
            try:
                if strategy == "mean" and pd.api.types.is_numeric_dtype(df[col]):
                    if df[col].dropna().empty:
                        logger.warning(f"⚠️ العمود '{col}' لا يحتوي على قيم صالحة لحساب المتوسط.")
                        continue
                    df[col] = df[col].fillna(df[col].mean())
                elif strategy == "median" and pd.api.types.is_numeric_dtype(df[col]):
                    if df[col].dropna().empty:
                        logger.warning(f"⚠️ العمود '{col}' لا يحتوي على قيم صالحة لحساب الوسيط.")
                        continue
                    df[col] = df[col].fillna(df[col].median())
                elif strategy == "mode":
                    mode_vals = df[col].mode()
                    if mode_vals.empty:
                        logger.warning(f"⚠️ العمود '{col}' لا يحتوي على قيم صالحة لحساب الوضع (mode).")
                        continue
                    df[col] = df[col].fillna(mode_vals[0])
                elif strategy == "zero":
                    df[col] = df[col].fillna(0)
                else:
                    logger.warning(f"⚠️ لا يمكن تطبيق استراتيجية {strategy} على العمود '{col}'")
            except Exception as e:
                logger.error(f"❌ خطأ أثناء ملء العمود '{col}': {e}")
                raise
    return df


def encode_categoricals(df: pd.DataFrame, method: str = "label") -> pd.DataFrame:
    if df is None or df.empty:
        raise ValueError("Input DataFrame is None or empty.")

    df = df.copy()
    cat_cols = df.select_dtypes(include=['object', 'category']).columns

    if len(cat_cols) == 0:
        logger.warning("⚠️ لا توجد أعمدة نوعية (categorical) في البيانات للترميز.")
        return df

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


def scale_numericals(df: pd.DataFrame, scaler: Optional[object] = None) -> pd.DataFrame:
    if df is None or df.empty:
        raise ValueError("Input DataFrame is None or empty.")

    df = df.copy()
    num_cols = df.select_dtypes(include=[np.number]).columns

    if len(num_cols) == 0:
        logger.warning("⚠️ لا توجد أعمدة رقمية لموازنتها.")
        return df

    if scaler is None:
        scaler = StandardScaler()

    try:
        df[num_cols] = scaler.fit_transform(df[num_cols])
    except Exception as e:
        logger.error(f"❌ فشل في موازنة الأعمدة الرقمية: {e}")
        raise

    return df
