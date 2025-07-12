import logging
import joblib
import numpy as np
from pathlib import Path
from statsmodels.tsa.arima.model import ARIMA
from sklearn.metrics import mean_squared_error, mean_absolute_error

from data_intelligence_system.config.paths_config import ML_MODELS_DIR
from data_intelligence_system.ml_models.base_model import BaseModel
from data_intelligence_system.ml_models.utils.preprocessing import DataPreprocessor
from data_intelligence_system.utils.preprocessing import fill_missing_values
from data_intelligence_system.utils.timer import Timer

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class ARIMAForecastingModel(BaseModel):
    def __init__(self, order=(1, 1, 1), scaler_type="standard"):
        """
        نموذج ARIMA للتنبؤ بالسلاسل الزمنية.
        """
        super().__init__(
            model_name="arima_forecast",
            model_dir=ML_MODELS_DIR
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
        series = np.asarray(series)
        if series.ndim != 1 or series.size == 0:
            raise ValueError("❌ يجب أن تكون البيانات الزمنية أحادية البعد وغير فارغة.")
        series = fill_missing_values(series)
        self.series_ = series
        if self.preprocessor:
            self.series_scaled_ = self.preprocessor.transform_scaler(series.reshape(-1, 1)).flatten()
        else:
            self.series_scaled_ = series

        self.model = ARIMA(self.series_scaled_, order=self.order)
        self.model_fit = self.model.fit()
        self.is_fitted = True
        logger.info("✅ تم تدريب نموذج ARIMA بنجاح.")
        return self

    def predict(self, steps=1, return_conf_int=False, alpha=0.05, inverse_transform=True):
        """
        توقع الخطوات المستقبلية مع خيار عرض فاصل الثقة.
        """
        self._check_is_fitted()
        forecast = self.model_fit.get_forecast(steps=steps)
        predicted = forecast.predicted_mean

        if inverse_transform and self.preprocessor:
            predicted = self.preprocessor.inverse_transform_scaler(predicted.reshape(-1, 1)).flatten()

        if return_conf_int:
            conf_int = forecast.conf_int(alpha=alpha)
            if inverse_transform and self.preprocessor:
                conf_int = self.preprocessor.inverse_transform_scaler(conf_int.to_numpy())
            return predicted, conf_int
        return predicted

    def evaluate(self, actual, predicted=None, inverse_transform=True):
        """
        تقييم النموذج على بيانات حقيقية.
        """
        actual = np.asarray(actual)
        if predicted is None:
            predicted = self.predict(steps=len(actual), inverse_transform=inverse_transform)
        mse = mean_squared_error(actual, predicted)
        mae = mean_absolute_error(actual, predicted)
        logger.info(f"📊 تقييم: MSE={mse:.4f}, MAE={mae:.4f}")
        return {"mse": mse, "mae": mae}

    def save(self):
        """
        حفظ النموذج.
        """
        if not self.is_fitted or self.model_fit is None:
            raise ValueError("❌ النموذج غير مدرب للحفظ.")
        self.model_path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump({
            "order": self.order,
            "model_fit": self.model_fit,
            "series": self.series_,
            "preprocessor": self.preprocessor,
            "is_fitted": self.is_fitted
        }, self.model_path)
        logger.info(f"💾 تم حفظ النموذج في: {self.model_path}")

    def load(self):
        """
        تحميل النموذج.
        """
        if not self.model_path.exists():
            raise FileNotFoundError(f"❌ لم يتم العثور على ملف النموذج: {self.model_path}")
        data = joblib.load(self.model_path)
        self.order = data["order"]
        self.series_ = data["series"]
        self.preprocessor = data.get("preprocessor")
        self.model = ARIMA(self.series_, order=self.order)
        self.model_fit = data["model_fit"]
        self.is_fitted = data["is_fitted"]
        logger.info(f"📥 تم تحميل النموذج بنجاح.")
        return self
