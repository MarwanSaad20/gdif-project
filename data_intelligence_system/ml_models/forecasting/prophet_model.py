import os
import joblib
import logging
from pathlib import Path
import pandas as pd
import plotly.graph_objects as go
from prophet import Prophet
from sklearn.metrics import mean_squared_error, mean_absolute_error

from data_intelligence_system.ml_models.base_model import BaseModel
from data_intelligence_system.ml_models.utils.preprocessing import DataPreprocessor
from data_intelligence_system.utils.preprocessing import fill_missing_values
from data_intelligence_system.utils.timer import Timer  # ⏱️ تم استيراده لدعم قياس الأداء

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class ProphetForecastingModel(BaseModel):
    def __init__(self, growth='linear', daily_seasonality=True, yearly_seasonality=True,
                 weekly_seasonality=True, scaler_type="standard", **kwargs):
        """
        نموذج Prophet للتنبؤ الزمني مع دعم التحجيم المسبق.
        """
        super().__init__(model_name="prophet_forecasting_model", model_dir="ml_models/saved_models")
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

    def _check_is_fitted(self):
        if not self.is_fitted or self.fitted_model is None:
            raise RuntimeError("❌ النموذج غير مدرب بعد. يرجى استدعاء fit أولاً.")

    @Timer("تدريب نموذج Prophet")  # ⏱️ ديكور لقياس زمن التدريب
    def fit(self, df: pd.DataFrame):
        if not {'ds', 'y'}.issubset(df.columns):
            raise ValueError("❌ يجب أن يحتوي DataFrame على الأعمدة ['ds', 'y']")
        df = df.copy()
        df['ds'] = pd.to_datetime(df['ds'])

        # ✅ معالجة القيم المفقودة في العمود y
        df['y'] = fill_missing_values(df['y'])

        if self.preprocessor:
            df['y'] = self.preprocessor.transform_scaler(df[['y']]).flatten()

        self.fitted_model = self.model.fit(df)
        self.is_fitted = True
        logger.info("✅ تم تدريب نموذج Prophet بنجاح.")
        return self

    def predict(self, periods: int, freq: str = 'D', inverse_transform: bool = True) -> pd.DataFrame:
        self._check_is_fitted()
        future = self.model.make_future_dataframe(periods=periods, freq=freq)
        forecast = self.fitted_model.predict(future)

        if inverse_transform and self.preprocessor:
            forecast['yhat'] = self.preprocessor.inverse_transform_scaler(forecast[['yhat']]).flatten()
            forecast['yhat_upper'] = self.preprocessor.inverse_transform_scaler(forecast[['yhat_upper']]).flatten()
            forecast['yhat_lower'] = self.preprocessor.inverse_transform_scaler(forecast[['yhat_lower']]).flatten()

        return forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']]

    def evaluate(self, df: pd.DataFrame, inverse_transform: bool = True):
        self._check_is_fitted()
        if not {'ds', 'y'}.issubset(df.columns):
            raise ValueError("❌ بيانات التقييم يجب أن تحتوي الأعمدة ['ds', 'y']")
        df = df.copy()
        df['ds'] = pd.to_datetime(df['ds'])
        actual_y = df['y'].values

        if self.preprocessor and not inverse_transform:
            actual_y = self.preprocessor.transform_scaler(df[['y']]).flatten()

        forecast = self.fitted_model.predict(df[['ds']])
        predicted_y = forecast['yhat'].values

        if inverse_transform and self.preprocessor:
            predicted_y = self.preprocessor.inverse_transform_scaler(predicted_y.reshape(-1, 1)).flatten()

        mse = mean_squared_error(actual_y, predicted_y)
        mae = mean_absolute_error(actual_y, predicted_y)
        logger.info(f"📊 تقييم النموذج: MSE={mse:.4f}, MAE={mae:.4f}")
        return {'mse': mse, 'mae': mae}

    def save(self, filepath: str = None):
        if filepath is None:
            filepath = Path(self.model_dir) / f"{self.model_name}.pkl"
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        joblib.dump({
            "model_params": self.model_params,
            "fitted_model": self.fitted_model,
            "preprocessor": self.preprocessor,
            "is_fitted": self.is_fitted
        }, filepath)
        logger.info(f"💾 تم حفظ نموذج Prophet في: {filepath}")

    def load(self, filepath: str = None):
        if filepath is None:
            filepath = Path(self.model_dir) / f"{self.model_name}.pkl"
        data = joblib.load(filepath)
        self.model_params = data.get("model_params", {})
        self.model = Prophet(**self.model_params)
        self.fitted_model = data["fitted_model"]
        self.preprocessor = data.get("preprocessor", None)
        self.is_fitted = data.get("is_fitted", False)
        logger.info(f"📥 تم تحميل نموذج Prophet من: {filepath}")
        return self

    def plot_forecast(self, forecast_df: pd.DataFrame) -> go.Figure:
        if forecast_df is None or forecast_df.empty:
            raise ValueError("❌ يجب توفير بيانات توقع صحيحة للرسم.")
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=forecast_df['ds'],
            y=forecast_df['yhat'],
            mode='lines',
            name='التوقع',
            line=dict(color='cyan')
        ))
        fig.add_trace(go.Scatter(
            x=forecast_df['ds'],
            y=forecast_df['yhat_upper'],
            mode='lines',
            name='الحد الأعلى',
            line=dict(width=0),
            showlegend=False
        ))
        fig.add_trace(go.Scatter(
            x=forecast_df['ds'],
            y=forecast_df['yhat_lower'],
            mode='lines',
            name='الحد الأدنى',
            fill='tonexty',
            line=dict(width=0),
            fillcolor='rgba(30,144,255,0.2)',
            showlegend=False
        ))
        fig.update_layout(
            title="توقعات زمنية باستخدام Prophet",
            plot_bgcolor="#0A0F1A",
            paper_bgcolor="#0A0F1A",
            font=dict(color="#FFFFFF"),
            margin=dict(l=40, r=40, t=40, b=40)
        )
        return fig
