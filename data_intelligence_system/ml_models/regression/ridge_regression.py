import logging
import joblib
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error

from data_intelligence_system.config.paths_config import ML_MODELS_DIR
from data_intelligence_system.ml_models.base_model import BaseModel
from data_intelligence_system.ml_models.utils.preprocessing import DataPreprocessor
from data_intelligence_system.utils.preprocessing import fill_missing_values
from data_intelligence_system.data.processed.scale_numericals import scale_numericals
from data_intelligence_system.utils.timer import Timer

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class RidgeRegressionModel(BaseModel):
    def __init__(
        self,
        alpha: float = 1.0,
        max_iter: int | None = None,
        tol: float = 1e-4,
        random_state: int | None = None,
        solver: str = 'auto',
        scaler_type: str = "standard",
        **kwargs,
    ):
        """
        نموذج Ridge Regression مع دعم تحجيم البيانات.
        """
        super().__init__(model_name="ridge_regression", model_dir=ML_MODELS_DIR)
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

    def _prepare_inputs(self, X, y=None):
        """
        تحويل المدخلات إلى DataFrame/Series، وملء القيم المفقودة، والتأكد من صحة الأبعاد.
        """
        if not isinstance(X, pd.DataFrame):
            X = pd.DataFrame(X)
        else:
            X = X.copy()

        X = fill_missing_values(X)
        if y is not None:
            if not isinstance(y, (pd.Series, np.ndarray)):
                y = pd.Series(y)
            else:
                y = pd.Series(y)

            y = fill_missing_values(y)
            if X.shape[0] != y.shape[0]:
                raise ValueError("❌ عدد العينات في X و y غير متطابق")
            if np.isnan(X.values).any():
                raise ValueError("❌ توجد قيم مفقودة في X بعد المعالجة")
            if np.isnan(y.values).any():
                raise ValueError("❌ توجد قيم مفقودة في y بعد المعالجة")
            return X, y

        if np.isnan(X.values).any():
            raise ValueError("❌ توجد قيم مفقودة في X بعد المعالجة")
        return X

    @Timer("⏱️ تدريب نموذج Ridge Regression")
    def fit(self, X, y):
        """تدريب النموذج"""
        X, y = self._prepare_inputs(X, y)

        X = scale_numericals(X)
        y = scale_numericals(pd.DataFrame(y)).squeeze()

        self.model.fit(X, y)
        self.is_fitted = True
        logger.info("✅ تم تدريب نموذج Ridge.")

    def predict(self, X, inverse_transform=True):
        """تنبؤ"""
        self._check_is_fitted()
        X = self._prepare_inputs(X)

        predictions = self.model.predict(scale_numericals(X))

        if inverse_transform and self.preprocessor:
            predictions = self.preprocessor.inverse_transform_scaler(predictions.reshape(-1, 1)).flatten()

        return predictions

    def evaluate(self, X, y, inverse_transform=True):
        """تقييم النموذج"""
        X, y = self._prepare_inputs(X, y)
        self._check_is_fitted()

        predictions = self.predict(X, inverse_transform=inverse_transform)
        mse = mean_squared_error(y, predictions)
        mae = mean_absolute_error(y, predictions)
        r2 = r2_score(y, predictions)
        logger.info(f"[📊] تقييم Ridge:\n - MAE: {mae:.4f}\n - MSE: {mse:.4f}\n - R²: {r2:.4f}")
        return {"mae": mae, "mse": mse, "r2": r2}

    def save(self, filepath: Path | None = None):
        """حفظ النموذج"""
        if not filepath:
            filepath = self.model_path
        filepath.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump({
            "model": self.model,
            "preprocessor": self.preprocessor,
            "is_fitted": self.is_fitted
        }, filepath)
        logger.info(f"💾 تم حفظ النموذج في: {filepath}")

    def load(self, filepath: Path | None = None):
        """تحميل النموذج"""
        if not filepath:
            filepath = self.model_path
        if not filepath.exists():
            raise FileNotFoundError(f"❌ لم يتم العثور على ملف النموذج: {filepath}")
        data = joblib.load(filepath)
        self.model = data["model"]
        self.preprocessor = data.get("preprocessor", None)
        self.is_fitted = data.get("is_fitted", False)
        logger.info(f"📥 تم تحميل النموذج من: {filepath}")
        return self

    def __repr__(self):
        return (f"<RidgeRegressionModel(alpha={self.alpha}, max_iter={self.max_iter}, tol={self.tol}, "
                f"solver='{self.solver}', scaler_type='{self.scaler_type}', is_fitted={self.is_fitted})>")
