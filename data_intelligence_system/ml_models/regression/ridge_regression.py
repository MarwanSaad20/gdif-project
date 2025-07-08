import os
import joblib
import logging
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error

from data_intelligence_system.ml_models.base_model import BaseModel
from data_intelligence_system.ml_models.utils.preprocessing import DataPreprocessor
from data_intelligence_system.utils.preprocessing import fill_missing_values
from data_intelligence_system.data.processed.scale_numericals import scale_numericals
from data_intelligence_system.utils.timer import Timer  # ⏱️ تم التكامل مع ملف timer.py

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class RidgeRegressionModel(BaseModel):
    def __init__(self, alpha=1.0, max_iter=None, tol=1e-4, random_state=None, solver='auto',
                 scaler_type="standard", **kwargs):
        """
        نموذج Ridge Regression مع دعم تحجيم البيانات.
        """
        super().__init__(model_name="ridge_regression", model_dir="ml_models/saved_models")
        self.alpha = alpha
        self.max_iter = max_iter
        self.tol = tol
        self.random_state = random_state
        self.solver = solver
        self.scaler_type = scaler_type
        self.model = Ridge(alpha=alpha, max_iter=max_iter, tol=tol,
                           random_state=random_state, solver=solver, **kwargs)
        self.preprocessor = DataPreprocessor(scaler_type=scaler_type) if scaler_type else None
        self.is_fitted = False

    @Timer("⏱️ تدريب نموذج Ridge Regression")  # ✅ قياس زمن التدريب
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

        assert X.shape[0] == y.shape[0], "❌ عدد العينات غير متطابق بين X و y"
        assert not np.isnan(X).any().any(), "❌ توجد قيم مفقودة في X"
        assert not np.isnan(y).any(), "❌ توجد قيم مفقودة في y"

        X = scale_numericals(X)
        y = scale_numericals(pd.DataFrame(y)).squeeze()

        self.model.fit(X, y)
        self.is_fitted = True
        logger.info("✅ تم تدريب نموذج Ridge.")

    def predict(self, X, inverse_transform=True):
        """تنبؤ"""
        self._check_is_fitted()
        if isinstance(X, pd.DataFrame):
            X = X.copy()
        else:
            X = pd.DataFrame(X)

        X = fill_missing_values(X)
        X = scale_numericals(X)

        predictions = self.model.predict(X)

        if inverse_transform and self.preprocessor:
            predictions = self.preprocessor.inverse_transform_scaler(predictions.reshape(-1, 1)).flatten()

        return predictions

    def evaluate(self, X, y, inverse_transform=True):
        """تقييم النموذج"""
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

        self._check_is_fitted()
        predictions = self.predict(X, inverse_transform=inverse_transform)
        mse = mean_squared_error(y, predictions)
        mae = mean_absolute_error(y, predictions)
        r2 = r2_score(y, predictions)
        logger.info(f"[📊] تقييم Ridge:\n - MAE: {mae:.4f}\n - MSE: {mse:.4f}\n - R²: {r2:.4f}")
        return {"mae": mae, "mse": mse, "r2": r2}

    def save(self, filepath=None):
        """حفظ النموذج"""
        if not filepath:
            filepath = Path(self.model_dir) / f"{self.model_name}.pkl"
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        joblib.dump({
            "model": self.model,
            "preprocessor": self.preprocessor,
            "is_fitted": self.is_fitted
        }, filepath)
        logger.info(f"💾 تم حفظ النموذج في: {filepath}")

    def load(self, filepath=None):
        """تحميل النموذج"""
        if not filepath:
            filepath = Path(self.model_dir) / f"{self.model_name}.pkl"
        data = joblib.load(filepath)
        self.model = data["model"]
        self.preprocessor = data.get("preprocessor", None)
        self.is_fitted = data["is_fitted"]
        logger.info(f"📥 تم تحميل النموذج من: {filepath}")
        return self
