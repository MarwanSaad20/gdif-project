import logging
import joblib
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.linear_model import Lasso
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error

from data_intelligence_system.ml_models.base_model import BaseModel
from data_intelligence_system.ml_models.utils.preprocessing import DataPreprocessor
from data_intelligence_system.utils.preprocessing import fill_missing_values
from data_intelligence_system.data.processed.scale_numericals import scale_numericals
from data_intelligence_system.utils.timer import Timer

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class LassoRegressionModel(BaseModel):
    def __init__(self, alpha=1.0, max_iter=1000, tol=1e-4, random_state=None, scaler_type="standard", **kwargs):
        """
        نموذج Lasso Regression مع دعم التحجيم المسبق.
        """
        super().__init__(model_name="lasso_regression", model_dir="data_intelligence_system/ml_models/saved_models")
        self.alpha = alpha
        self.max_iter = max_iter
        self.tol = tol
        self.random_state = random_state
        self.scaler_type = scaler_type
        self.model = Lasso(alpha=alpha, max_iter=max_iter, tol=tol,
                           random_state=random_state, **kwargs)
        self.preprocessor = DataPreprocessor(scaler_type=scaler_type) if scaler_type else None
        self.is_fitted = False

    @Timer("تدريب نموذج Lasso")
    def fit(self, X, y):
        """تدريب النموذج"""
        if isinstance(X, pd.DataFrame):
            X = X.copy()
        else:
            X = pd.DataFrame(X)

        if isinstance(y, (pd.Series, np.ndarray)):
            y = pd.Series(y)
        else:
            y = pd.Series(y)

        X = fill_missing_values(X)
        y = fill_missing_values(y)

        assert X.shape[0] == y.shape[0], "❌ عدد العينات في X و y غير متطابق"
        assert not np.isnan(X).any().any(), "❌ توجد قيم مفقودة في X"
        assert not np.isnan(y).any(), "❌ توجد قيم مفقودة في y"

        X = scale_numericals(X)
        y = scale_numericals(pd.DataFrame(y)).squeeze()

        self.model.fit(X, y)
        self.is_fitted = True
        logger.info("✅ تم تدريب نموذج Lasso.")

    def predict(self, X, inverse_transform=True):
        """توليد التنبؤات"""
        self._check_is_fitted()
        if isinstance(X, pd.DataFrame):
            X = X.copy()
        else:
            X = pd.DataFrame(X)

        X = fill_missing_values(X)
        X = scale_numericals(X)

        y_pred = self.model.predict(X)

        if inverse_transform and self.preprocessor:
            y_pred = self.preprocessor.inverse_transform_scaler(y_pred.reshape(-1, 1)).flatten()

        return y_pred

    def evaluate(self, X, y, inverse_transform=True):
        """تقييم النموذج"""
        self._check_is_fitted()

        if isinstance(X, pd.DataFrame):
            X = X.copy()
        else:
            X = pd.DataFrame(X)

        if isinstance(y, (pd.Series, np.ndarray)):
            y = pd.Series(y)
        else:
            y = pd.Series(y)

        X = fill_missing_values(X)
        y = fill_missing_values(y)

        predictions = self.predict(X, inverse_transform=inverse_transform)
        mae = mean_absolute_error(y, predictions)
        mse = mean_squared_error(y, predictions)
        r2 = r2_score(y, predictions)
        logger.info(f"[📊] تقييم Lasso:\n - MAE: {mae:.4f}\n - MSE: {mse:.4f}\n - R²: {r2:.4f}")
        return {"mae": mae, "mse": mse, "r2": r2}

    def save(self):
        """حفظ النموذج"""
        if self.model is None:
            raise ValueError("❌ لا يوجد نموذج لحفظه.")
        self.model_path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump({
            "model": self.model,
            "preprocessor": self.preprocessor,
            "is_fitted": self.is_fitted
        }, self.model_path)
        logger.info(f"💾 تم حفظ النموذج في: {self.model_path}")

    def load(self):
        """تحميل النموذج"""
        if not self.model_path.exists():
            raise FileNotFoundError(f"❌ لم يتم العثور على ملف النموذج: {self.model_path}")
        data = joblib.load(self.model_path)
        self.model = data["model"]
        self.preprocessor = data.get("preprocessor", None)
        self.is_fitted = data.get("is_fitted", False)
        logger.info(f"📥 تم تحميل النموذج من: {self.model_path}")
        return self
