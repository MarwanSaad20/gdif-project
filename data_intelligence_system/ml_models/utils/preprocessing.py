import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import (
    StandardScaler,
    MinMaxScaler,
    RobustScaler,
    LabelEncoder
)
import logging

from data_intelligence_system.utils.preprocessing import fill_missing_values  # ✅ محدث

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataPreprocessor:
    def __init__(self, scaler_type="standard", test_size=0.2, random_state=42):
        self.scaler_type = scaler_type
        self.test_size = test_size
        self.random_state = random_state
        self.scaler = None
        self.label_encoders = {}

    def fit_scaler(self, X):
        if self.scaler_type == "standard":
            self.scaler = StandardScaler()
        elif self.scaler_type == "minmax":
            self.scaler = MinMaxScaler()
        elif self.scaler_type == "robust":
            self.scaler = RobustScaler()
        else:
            logger.warning(f"نوع السكيلر '{self.scaler_type}' غير معروف. سيتم تجاهل السكيلينج.")
            self.scaler = None

        if self.scaler:
            self.scaler.fit(X)
        return self

    def transform_scaler(self, X):
        if self.scaler:
            try:
                return self.scaler.transform(X)
            except Exception as e:
                logger.error(f"خطأ أثناء تحويل البيانات بالسكيلر: {e}")
                raise
        return X

    def inverse_transform_scaler(self, X):
        if self.scaler:
            try:
                return self.scaler.inverse_transform(X)
            except Exception as e:
                logger.error(f"خطأ أثناء عكس التحويل بالسكيلر: {e}")
                raise
        return X

    def fit_transform_scaler(self, X):
        self.fit_scaler(X)
        return self.transform_scaler(X)

    def detect_categorical_columns(self, df):
        return df.select_dtypes(include=["object", "category"]).columns.tolist()

    def encode_labels(self, df, categorical_cols):
        for col in categorical_cols:
            if col not in self.label_encoders:
                le = LabelEncoder()
                df[col] = le.fit_transform(df[col].astype(str))
                self.label_encoders[col] = le
            else:
                le = self.label_encoders[col]
                try:
                    df[col] = le.transform(df[col].astype(str))
                except ValueError as e:
                    logger.error(f"قيم جديدة غير معروفة في العمود '{col}': {e}")
                    raise
        return df

    def decode_labels(self, df, categorical_cols):
        for col in categorical_cols:
            if col in self.label_encoders:
                le = self.label_encoders[col]
                try:
                    df[col] = le.inverse_transform(df[col])
                except Exception as e:
                    logger.error(f"خطأ أثناء فك الترميز في العمود '{col}': {e}")
                    raise
        return df

    def split(self, X, y=None):
        try:
            if y is not None and len(np.unique(y)) > 1:
                return train_test_split(
                    X, y,
                    test_size=self.test_size,
                    random_state=self.random_state,
                    stratify=y
                )
            elif y is not None:
                logger.warning("🚨 المتغير الهدف يحتوي على فئة واحدة فقط. سيتم التقسيم بدون stratify.")
                return train_test_split(
                    X, y,
                    test_size=self.test_size,
                    random_state=self.random_state
                )
            else:
                return train_test_split(
                    X,
                    test_size=self.test_size,
                    random_state=self.random_state
                )
        except Exception as e:
            logger.error(f"❌ فشل في تقسيم البيانات: {e}")
            raise

    def preprocess(self, df, target_col=None, categorical_cols=None, scale=True):
        df = df.copy()

        # ✅ معالجة القيم المفقودة باستخدام الدالة الموحدة
        df = fill_missing_values(df)

        initial_shape = df.shape
        df.dropna(axis=0, how='any', inplace=True)
        dropped_rows = initial_shape[0] - df.shape[0]
        if dropped_rows > 0:
            logger.info(f"تم حذف {dropped_rows} صفوف بسبب القيم الناقصة المتبقية بعد المعالجة.")

        if categorical_cols is None:
            categorical_cols = self.detect_categorical_columns(df)

        if categorical_cols:
            df = self.encode_labels(df, categorical_cols)

        if target_col and target_col in df.columns:
            X = df.drop(columns=[target_col])
            y = df[target_col].values
        else:
            X = df
            y = None

        categorical_cols = categorical_cols or []
        numeric_cols = [col for col in X.select_dtypes(include=[np.number]).columns if col not in categorical_cols]

        if scale and numeric_cols:
            self.fit_scaler(X[numeric_cols])
            X_scaled = self.transform_scaler(X[numeric_cols])
            X.loc[:, numeric_cols] = X_scaled

        if y is not None:
            return self.split(X, y)
        else:
            return self.split(X)


# اختبار تجريبي
if __name__ == "__main__":
    data = {
        "feature1": [10, 20, 30, 40, 50, None],
        "feature2": [0.1, 0.2, 0.3, None, 0.5, 0.6],
        "category": ["A", "B", "A", "B", "C", "C"],
        "target": [1, 0, 1, 0, 1, 0]
    }
    df = pd.DataFrame(data)

    preprocessor = DataPreprocessor(scaler_type="standard", test_size=0.4)
    X_train, X_test, y_train, y_test = preprocessor.preprocess(
        df,
        target_col="target",
        categorical_cols=None,  # اكتشاف تلقائي
        scale=True
    )

    print("X_train:\n", X_train)
    print("y_train:\n", y_train)
