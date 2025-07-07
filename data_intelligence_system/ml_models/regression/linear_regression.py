import logging
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error

from data_intelligence_system.ml_models.base_model import BaseModel
from data_intelligence_system.ml_models.utils.preprocessing import DataPreprocessor
from data_intelligence_system.data.processed.fill_missing import fill_missing
from data_intelligence_system.data.processed.scale_numericals import scale_numericals  # ✅ جديد

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class LinearRegressionModel(BaseModel):
    """
    نموذج انحدار خطي مبني على scikit-learn، مع دعم تحجيم البيانات.
    """

    def __init__(self, model_name="linear_regression", model_dir=Path("ml_models/saved_models"), scaler_type="standard"):
        super().__init__(model_name, model_dir)
        self.model = LinearRegression()
        self.scaler_type = scaler_type
        self.preprocessor = DataPreprocessor(scaler_type=scaler_type) if scaler_type else None
        self.is_fitted = False

    def fit(self, X, y):
        """تدريب النموذج بعد التحقق من المدخلات"""
        if isinstance(X, pd.DataFrame):
            X = X.copy()
        else:
            X = pd.DataFrame(X)

        if isinstance(y, (pd.Series, np.ndarray)):
            y = pd.Series(y)
        else:
            y = pd.Series(y)

        X = fill_missing(X)
        y = fill_missing(y)

        assert not np.isnan(X).any().any(), "❌ توجد قيم مفقودة في X"
        assert not np.isnan(y).any(), "❌ توجد قيم مفقودة في y"
        assert X.shape[0] == y.shape[0], "❌ عدد الصفوف في X و y غير متطابق"

        X = scale_numericals(X)
        y = scale_numericals(pd.DataFrame(y)).squeeze()

        self.model.fit(X, y)
        self.is_fitted = True
        logger.info("✅ تم تدريب نموذج الانحدار الخطي.")

    def predict(self, X, inverse_transform=True):
        """توليد التنبؤات"""
        self._check_is_fitted()
        if isinstance(X, pd.DataFrame):
            X = X.copy()
        else:
            X = pd.DataFrame(X)

        X = fill_missing(X)
        X = scale_numericals(X)

        y_pred = self.model.predict(X)

        if inverse_transform and self.preprocessor:
            y_pred = self.preprocessor.inverse_transform_scaler(y_pred.reshape(-1, 1)).flatten()

        return y_pred

    def evaluate(self, X, y, inverse_transform=True):
        """تقييم النموذج باستخدام MSE و R² و MAE"""
        if isinstance(X, pd.DataFrame):
            X = X.copy()
        else:
            X = pd.DataFrame(X)

        if isinstance(y, (pd.Series, np.ndarray)):
            y = pd.Series(y)
        else:
            y = pd.Series(y)

        X = fill_missing(X)
        y = fill_missing(y)

        predictions = self.predict(X, inverse_transform=inverse_transform)
        mse = mean_squared_error(y, predictions)
        mae = mean_absolute_error(y, predictions)
        r2 = r2_score(y, predictions)

        logger.info(f"[📊] تقييم النموذج:\n - MAE: {mae:.4f}\n - MSE: {mse:.4f}\n - R² Score: {r2:.4f}")
        return {"mae": mae, "mse": mse, "r2": r2}
