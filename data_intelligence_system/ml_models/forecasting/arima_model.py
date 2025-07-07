import os
import joblib
import logging
import numpy as np
from pathlib import Path
from statsmodels.tsa.arima.model import ARIMA
from sklearn.metrics import mean_squared_error, mean_absolute_error

from data_intelligence_system.ml_models.base_model import BaseModel
from data_intelligence_system.ml_models.utils.preprocessing import DataPreprocessor
from data_intelligence_system.data.processed.fill_missing import fill_missing  # ✅ إضافة

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class ARIMAForecastingModel(BaseModel):
    def __init__(self, order=(1, 1, 1), scaler_type="standard"):
        """
        نموذج ARIMA للتنبؤ بالسلاسل الزمنية مع دعم التحجيم.
        """
        super().__init__(model_name="arima_forecast", model_dir="ml_models/saved_models")
        self.order = order
        self.model = None
        self.model_fit = None
        self.series_ = None
        self.series_scaled_ = None
        self.preprocessor = DataPreprocessor(scaler_type=scaler_type) if scaler_type else None
        self.is_fitted = False

    def fit(self, series):
        """
        تدريب النموذج على بيانات زمنية أحادية البعد.
        """
        if not isinstance(series, (list, np.ndarray)) or np.array(series).ndim != 1:
            raise ValueError("❌ يجب أن تكون البيانات الزمنية أحادية البعد (1D).")

        series = fill_missing(np.array(series))  # ✅ معالجة القيم المفقودة
        self.series_ = np.array(series)
        if self.preprocessor:
            self.series_scaled_ = self.preprocessor.transform_scaler(self.series_.reshape(-1, 1)).flatten()
        else:
            self.series_scaled_ = self.series_

        self.model = ARIMA(self.series_scaled_, order=self.order)
        self.model_fit = self.model.fit()
        self.is_fitted = True
        logger.info(f"✅ تم تدريب نموذج ARIMA بالمعاملات: order={self.order}")
        return self

    def predict(self, steps=1, return_conf_int=False, alpha=0.05, inverse_transform=True):
        """
        توقع الخطوات المستقبلية مع خيار عرض فاصل الثقة.
        """
        self._check_is_fitted()
        forecast = self.model_fit.get_forecast(steps=steps)

        predicted = np.array(forecast.predicted_mean)

        if inverse_transform and self.preprocessor:
            predicted = self.preprocessor.inverse_transform_scaler(predicted.reshape(-1, 1)).flatten()

        if return_conf_int:
            conf_int = forecast.conf_int(alpha=alpha)
            if inverse_transform and self.preprocessor:
                conf_int = self.preprocessor.inverse_transform_scaler(conf_int.to_numpy())
            logger.info("📈 تم توليد توقعات مع فاصل ثقة.")
            return predicted, conf_int
        else:
            return predicted

    def evaluate(self, actual, predicted=None, inverse_transform=True):
        """
        تقييم النموذج على بيانات حقيقية.
        """
        if predicted is None:
            predicted = self.predict(steps=len(actual), inverse_transform=inverse_transform)
        mse = mean_squared_error(actual, predicted)
        mae = mean_absolute_error(actual, predicted)
        logger.info(f"📊 تقييم النموذج:\n - MSE: {mse:.4f}\n - MAE: {mae:.4f}")
        return {"mse": mse, "mae": mae}

    def save(self, filepath=None):
        """
        حفظ النموذج ونتائجه باستخدام joblib.
        """
        if not filepath:
            filepath = Path(self.model_dir) / f"{self.model_name}.pkl"
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        joblib.dump({
            'order': self.order,
            'model_fit': self.model_fit,
            'series': self.series_,
            'preprocessor': self.preprocessor,
            'is_fitted': self.is_fitted
        }, filepath)
        logger.info(f"💾 تم حفظ نموذج ARIMA في: {filepath}")

    def load(self, filepath=None):
        """
        تحميل النموذج من ملف محفوظ.
        """
        if not filepath:
            filepath = Path(self.model_dir) / f"{self.model_name}.pkl"
        data = joblib.load(filepath)
        self.order = data['order']
        self.series_ = data['series']
        self.preprocessor = data.get('preprocessor', None)
        self.model = ARIMA(self.series_, order=self.order)
        self.model_fit = data['model_fit']
        self.is_fitted = data['is_fitted']
        logger.info(f"📥 تم تحميل نموذج ARIMA من: {filepath}")
        return self
