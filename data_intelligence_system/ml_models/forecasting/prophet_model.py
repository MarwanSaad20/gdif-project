import logging
import joblib
from pathlib import Path
import pandas as pd
import plotly.graph_objects as go
from prophet import Prophet
from sklearn.metrics import mean_squared_error, mean_absolute_error

# ✅ استيرادات من جذر المشروع
from data_intelligence_system.ml_models.base_model import BaseModel
from data_intelligence_system.ml_models.utils.preprocessing import DataPreprocessor
from data_intelligence_system.utils.preprocessing import fill_missing_values
from data_intelligence_system.utils.timer import Timer

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class ProphetForecastingModel(BaseModel):
    def __init__(self, growth='linear', daily_seasonality=True, yearly_seasonality=True,
                 weekly_seasonality=True, scaler_type="standard", **kwargs):
        """
        نموذج Prophet للتنبؤ الزمني مع دعم التحجيم.
        """
        super().__init__(model_name="prophet_forecasting_model",
                         model_dir="data_intelligence_system/ml_models/saved_models")
        self.model_params = {
            "growth": growth,
            "daily_seasonality": daily_seasonality,
            "yearly_seasonality": yearly_seasonality,
            "weekly_seasonality": weekly_seasonality,
            **kwargs
        }
        self.model = Prophet(**self.model_params)
        self.fitted_model = None
        self.preprocessor = DataPreprocessor(scaler_type=scaler_type) if scaler_type else None
        self.is_fitted = False

    def _validate_df_columns(self, df: pd.DataFrame, required_cols=('ds', 'y')):
        if not set(required_cols).issubset(df.columns):
            raise ValueError(f"❌ يجب أن يحتوي DataFrame على الأعمدة: {required_cols}")

    @Timer("تدريب نموذج Prophet")
    def fit(self, df: pd.DataFrame):
        self._validate_df_columns(df)
        df = df.copy()
        df['ds'] = pd.to_datetime(df['ds'])
        df['y'] = fill_missing_values(df['y'])
        if self.preprocessor:
            df['y'] = self.preprocessor.transform_scaler(df[['y']]).flatten()
        try:
            self.fitted_model = self.model.fit(df)
            self.is_fitted = True
            logger.info("✅ تم تدريب نموذج Prophet بنجاح.")
        except Exception as e:
            logger.exception(f"❌ فشل تدريب نموذج Prophet: {e}")
            raise
        return self

    def predict(self, periods: int, freq: str = 'D', inverse_transform: bool = True) -> pd.DataFrame:
        self._check_is_fitted()
        if periods <= 0:
            raise ValueError("❌ يجب أن يكون عدد الفترات للتنبؤ أكبر من صفر.")
        future = self.model.make_future_dataframe(periods=periods, freq=freq)
        forecast = self.fitted_model.predict(future)
        if inverse_transform and self.preprocessor:
            for col in ['yhat', 'yhat_upper', 'yhat_lower']:
                forecast[col] = self.preprocessor.inverse_transform_scaler(forecast[[col]]).flatten()
        return forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']]

    def evaluate(self, df: pd.DataFrame, inverse_transform: bool = True):
        self._check_is_fitted()
        self._validate_df_columns(df)
        df = df.copy()
        df['ds'] = pd.to_datetime(df['ds'])
        actual_y = fill_missing_values(df['y']).values
        if self.preprocessor and not inverse_transform:
            actual_y = self.preprocessor.transform_scaler(df[['y']]).flatten()
        try:
            forecast = self.fitted_model.predict(df[['ds']])
            predicted_y = forecast['yhat'].values
            if inverse_transform and self.preprocessor:
                predicted_y = self.preprocessor.inverse_transform_scaler(predicted_y.reshape(-1, 1)).flatten()
            mse = mean_squared_error(actual_y, predicted_y)
            mae = mean_absolute_error(actual_y, predicted_y)
            logger.info(f"📊 تقييم النموذج: MSE={mse:.4f}, MAE={mae:.4f}")
            return {'mse': mse, 'mae': mae}
        except Exception as e:
            logger.exception(f"❌ خطأ أثناء تقييم النموذج: {e}")
            raise

    def save(self):
        if self.fitted_model is None:
            raise ValueError("❌ لا يوجد نموذج لحفظه.")
        self.model_path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump({
            "model_params": self.model_params,
            "fitted_model": self.fitted_model,
            "preprocessor": self.preprocessor,
            "is_fitted": self.is_fitted
        }, self.model_path)
        logger.info(f"💾 تم حفظ نموذج Prophet في: {self.model_path}")

    def load(self):
        if not self.model_path.exists():
            raise FileNotFoundError(f"❌ لم يتم العثور على ملف النموذج: {self.model_path}")
        data = joblib.load(self.model_path)
        self.model_params = data.get("model_params", {})
        self.model = Prophet(**self.model_params)
        self.fitted_model = data["fitted_model"]
        self.preprocessor = data.get("preprocessor", None)
        self.is_fitted = data.get("is_fitted", False)
        logger.info(f"📥 تم تحميل نموذج Prophet من: {self.model_path}")
        return self

    def plot_forecast(self, forecast_df: pd.DataFrame) -> go.Figure:
        if forecast_df is None or forecast_df.empty or not {'ds', 'yhat'}.issubset(forecast_df.columns):
            raise ValueError("❌ يجب توفير DataFrame يحتوي على الأعمدة ['ds', 'yhat'].")
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=forecast_df['ds'], y=forecast_df['yhat'],
                                 mode='lines', name='التوقع', line=dict(color='cyan')))
        fig.add_trace(go.Scatter(x=forecast_df['ds'], y=forecast_df['yhat_upper'],
                                 mode='lines', line=dict(width=0), showlegend=False))
        fig.add_trace(go.Scatter(x=forecast_df['ds'], y=forecast_df['yhat_lower'],
                                 mode='lines', fill='tonexty', fillcolor='rgba(30,144,255,0.2)',
                                 line=dict(width=0), showlegend=False))
        fig.update_layout(title="توقعات زمنية باستخدام Prophet",
                          plot_bgcolor="#0A0F1A", paper_bgcolor="#0A0F1A",
                          font=dict(color="#FFFFFF"), margin=dict(l=40, r=40, t=40, b=40))
        return fig
