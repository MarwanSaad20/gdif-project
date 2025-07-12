import logging
import joblib
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.linear_model import Lasso
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error

from data_intelligence_system.config.paths_config import ML_MODELS_DIR
from data_intelligence_system.ml_models.base_model import BaseModel
from data_intelligence_system.ml_models.utils.preprocessing import DataPreprocessor
from data_intelligence_system.utils.preprocessing import fill_missing_values
from data_intelligence_system.utils.timer import Timer
from data_intelligence_system.data.processed.scale_numericals import scale_numericals

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class LassoRegressionModel(BaseModel):
    def __init__(self, alpha=1.0, max_iter=1000, tol=1e-4, random_state=None, scaler_type="standard", **kwargs):
        """
        نموذج Lasso Regression مع دعم التحجيم المسبق.
        """
        super().__init__(model_name="lasso_regression", model_dir=ML_MODELS_DIR)
        self.alpha = alpha
        self.max_iter = max_iter
        self.tol = tol
        self.random_state = random_state
        self.scaler_type = scaler_type
        self.model = Lasso(alpha=alpha, max_iter=max_iter, tol=tol,
                           random_state=random_state, **kwargs)
        self.preprocessor = DataPreprocessor(scaler_type=scaler_type) if scaler_type else None
        self.is_fitted = False

    def _prepare_data(self, X, y=None):
        """تحضير البيانات (تعبئة القيم، تحجيم)"""
        if not isinstance(X, pd.DataFrame):
            X = pd.DataFrame(X)
        X = fill_missing_values(X)

        if y is not None:
            if not isinstance(y, (pd.Series, np.ndarray)):
                y = pd.Series(y)
            y = fill_missing_values(y)
            if X.shape[0] != y.shape[0]:
                raise ValueError("❌ عدد العينات في X و y غير متطابق")
        else:
            y = None

        if np.isnan(X).any().any():
            raise ValueError("❌ توجد قيم مفقودة في X بعد التعبئة")
        if y is not None and np.isnan(y).any():
            raise ValueError("❌ توجد قيم مفقودة في y بعد التعبئة")

        X_scaled = scale_numericals(X)
        y_scaled = scale_numericals(pd.DataFrame(y)).squeeze() if y is not None else None
        return X_scaled, y_scaled

    @Timer("تدريب نموذج Lasso")
    def fit(self, X, y):
        """تدريب النموذج"""
        X_scaled, y_scaled = self._prepare_data(X, y)
        self.model.fit(X_scaled, y_scaled)
        self.is_fitted = True
        logger.info(f"✅ تم تدريب نموذج Lasso: alpha={self.alpha}, max_iter={self.max_iter}")

    def predict(self, X, inverse_transform=True):
        """توليد التنبؤات"""
        self._check_is_fitted()

        if X is None or (hasattr(X, "empty") and X.empty):
            raise ValueError("❌ بيانات الإدخال فارغة في predict")

        if not isinstance(X, pd.DataFrame):
            X = pd.DataFrame(X)
        X = fill_missing_values(X)
        if np.isnan(X).any().any():
            raise ValueError("❌ توجد قيم مفقودة في X بعد التعبئة في predict")

        X_scaled = scale_numericals(X)
        y_pred = self.model.predict(X_scaled)

        if inverse_transform and self.preprocessor:
            y_pred = self.preprocessor.inverse_transform_scaler(y_pred.reshape(-1, 1)).flatten()

        return y_pred

    def evaluate(self, X, y, inverse_transform=True):
        """تقييم النموذج"""
        self._check_is_fitted()

        if X is None or y is None:
            raise ValueError("❌ بيانات الإدخال أو الهدف فارغة في evaluate")

        X_scaled, y_scaled = self._prepare_data(X, y)
        predictions = self.predict(X, inverse_transform=inverse_transform)
        mae = mean_absolute_error(y_scaled if inverse_transform else y, predictions)
        mse = mean_squared_error(y_scaled if inverse_transform else y, predictions)
        r2 = r2_score(y_scaled if inverse_transform else y, predictions)

        logger.info(f"[📊] تقييم Lasso:\n - MAE: {mae:.4f}\n - MSE: {mse:.4f}\n - R²: {r2:.4f}")
        return {"mae": mae, "mse": mse, "r2": r2}

    def save(self):
        """حفظ النموذج"""
        if self.model is None:
            raise ValueError("❌ لا يوجد نموذج لحفظه.")
        try:
            self.model_path.parent.mkdir(parents=True, exist_ok=True)
            joblib.dump({
                "model": self.model,
                "preprocessor": self.preprocessor,
                "is_fitted": self.is_fitted
            }, self.model_path)
            logger.info(f"💾 تم حفظ النموذج '{self.model_name}' في: {self.model_path}")
        except Exception as e:
            logger.error(f"❌ خطأ أثناء حفظ النموذج: {e}")
            raise

    def load(self):
        """تحميل النموذج"""
        if not self.model_path.exists():
            raise FileNotFoundError(f"❌ لم يتم العثور على ملف النموذج: {self.model_path}")
        try:
            data = joblib.load(self.model_path)
            self.model = data["model"]
            self.preprocessor = data.get("preprocessor", None)
            self.is_fitted = data.get("is_fitted", False)
            logger.info(f"📥 تم تحميل النموذج '{self.model_name}' من: {self.model_path}")
            return self
        except Exception as e:
            logger.error(f"❌ خطأ أثناء تحميل النموذج: {e}")
            raise
