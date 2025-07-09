import logging
import joblib
import numpy as np
from pathlib import Path
from statsmodels.tsa.arima.model import ARIMA
from sklearn.metrics import mean_squared_error, mean_absolute_error

# ✅ استيرادات من جذر المشروع
from data_intelligence_system.ml_models.base_model import BaseModel
from data_intelligence_system.ml_models.utils.preprocessing import DataPreprocessor
from data_intelligence_system.utils.preprocessing import fill_missing_values
from data_intelligence_system.utils.timer import Timer

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class ARIMAForecastingModel(BaseModel):
    def __init__(self, order=(1, 1, 1), scaler_type="standard"):
        """
        نموذج ARIMA للتنبؤ بالسلاسل الزمنية مع دعم التحجيم.
        """
        super().__init__(
            model_name="arima_forecast",
            model_dir="data_intelligence_system/ml_models/saved_models"
        )
        self.order = order
        self.model = None
        self.model_fit = None
        self.series_ = None
        self.series_scaled_ = None
        self.preprocessor = DataPreprocessor(scaler_type=scaler_type) if scaler_type else None
        self.is_fitted = False

    @Timer("تدريب نموذج ARIMA")
    def fit(self, series):
        """
        تدريب النموذج على بيانات زمنية أحادية البعد.
        """
        if not isinstance(series, (list, np.ndarray)) or np.array(series).ndim != 1:
            raise ValueError("❌ يجب أن تكون البيانات الزمنية أحادية البعد (1D).")

        series = fill_missing_values(np.array(series))
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

    def save(self):
        """
        حفظ النموذج ونتائجه باستخدام joblib.
        """
        if self.model_fit is None:
            raise ValueError("❌ لا يوجد نموذج لحفظه.")
        self.model_path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump({
            'order': self.order,
            'model_fit': self.model_fit,
            'series': self.series_,
            'preprocessor': self.preprocessor,
            'is_fitted': self.is_fitted
        }, self.model_path)
        logger.info(f"💾 تم حفظ نموذج ARIMA في: {self.model_path}")

    def load(self):
        """
        تحميل النموذج من ملف محفوظ.
        """
        if not self.model_path.exists():
            raise FileNotFoundError(f"❌ لم يتم العثور على ملف النموذج: {self.model_path}")
        data = joblib.load(self.model_path)
        self.order = data['order']
        self.series_ = data['series']
        self.preprocessor = data.get('preprocessor', None)
        self.model = ARIMA(self.series_, order=self.order)
        self.model_fit = data['model_fit']
        self.is_fitted = data['is_fitted']
        logger.info(f"📥 تم تحميل نموذج ARIMA من: {self.model_path}")
        return self
