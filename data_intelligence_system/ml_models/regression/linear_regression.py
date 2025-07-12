import logging
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error

from data_intelligence_system.config.paths_config import ML_MODELS_DIR
from data_intelligence_system.ml_models.base_model import BaseModel
from data_intelligence_system.ml_models.utils.preprocessing import DataPreprocessor
from data_intelligence_system.utils.preprocessing import fill_missing_values
from data_intelligence_system.data.processed.scale_numericals import scale_numericals
from data_intelligence_system.utils.timer import Timer

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class LinearRegressionModel(BaseModel):
    """
    نموذج انحدار خطي مبني على scikit-learn، مع دعم تحجيم البيانات.
    """

    def __init__(
        self,
        model_name="linear_regression",
        model_dir=ML_MODELS_DIR,
        scaler_type="standard",
    ):
        super().__init__(model_name, model_dir)
        self.model = LinearRegression()
        self.scaler_type = scaler_type
        self.preprocessor = DataPreprocessor(scaler_type=scaler_type) if scaler_type else None
        self.is_fitted = False

    def _prepare_data(self, X, y=None, scale=True):
        """تحويل المدخلات إلى DataFrame/Series، تعبئة القيم المفقودة، وتحجيم البيانات إذا scale=True."""
        if X is None:
            raise ValueError("المدخل X لا يمكن أن يكون None")
        if isinstance(X, pd.DataFrame):
            X = X.copy()
        else:
            X = pd.DataFrame(X)

        X = fill_missing_values(X)

        if scale:
            X = scale_numericals(X)

        if y is not None:
            if isinstance(y, (pd.Series, np.ndarray)):
                y = pd.Series(y)
            else:
                y = pd.Series(y)

            y = fill_missing_values(y)
            if scale:
                y = scale_numericals(pd.DataFrame(y)).squeeze()

            if X.shape[0] != y.shape[0]:
                raise ValueError("❌ عدد الصفوف في X و y غير متطابق")

            return X, y

        return X

    @Timer("تدريب نموذج الانحدار الخطي")
    def fit(self, X, y):
        """تدريب النموذج بعد التحقق من المدخلات"""
        X, y = self._prepare_data(X, y, scale=True)

        self.model.fit(X, y)
        self.is_fitted = True
        logger.info("✅ تم تدريب نموذج الانحدار الخطي.")
        return self  # لتمكين method chaining إذا رغبت

    def predict(self, X, inverse_transform=True):
        """توليد التنبؤات"""
        self._check_is_fitted()
        X = self._prepare_data(X, scale=True)

        y_pred = self.model.predict(X)

        if inverse_transform and self.preprocessor:
            try:
                y_pred = self.preprocessor.inverse_transform_scaler(y_pred.reshape(-1, 1)).flatten()
            except Exception as e:
                logger.warning(f"⚠️ فشل التحويل العكسي للتنبؤات: {e}")

        return y_pred

    def evaluate(self, X, y, inverse_transform=True):
        """تقييم النموذج باستخدام MSE و R² و MAE"""
        X, y = self._prepare_data(X, y, scale=True)

        predictions = self.predict(X, inverse_transform=inverse_transform)
        mse = mean_squared_error(y, predictions)
        mae = mean_absolute_error(y, predictions)
        r2 = r2_score(y, predictions)

        logger.info(f"[📊] تقييم النموذج:\n - MAE: {mae:.4f}\n - MSE: {mse:.4f}\n - R² Score: {r2:.4f}")
        return {"mae": mae, "mse": mse, "r2": r2}
