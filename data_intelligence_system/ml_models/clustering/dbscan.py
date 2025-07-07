import os
import joblib
import logging
from pathlib import Path
import pandas as pd
from sklearn.cluster import DBSCAN

from data_intelligence_system.ml_models.base_model import BaseModel
from data_intelligence_system.data.processed.fill_missing import fill_missing
from data_intelligence_system.data.processed.scale_numericals import scale_numericals  # ✅ جديد

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class DBSCANClusteringModel(BaseModel):
    def __init__(self, model_params=None, scaler_type="standard"):
        """
        نموذج تجميع باستخدام DBSCAN.

        Args:
            model_params: dict - معلمات DBSCAN.
            scaler_type: نوع التحجيم (standard, minmax, robust, None).
        """
        super().__init__(model_name="dbscan_clustering", model_dir="ml_models/saved_models")
        self.model_params = model_params if model_params else {}
        self.model = DBSCAN(**self.model_params)
        self.scaler_type = scaler_type  # احتفظنا به لو احتاج لاحقًا
        self.is_fitted = False

    def fit(self, X: pd.DataFrame):
        """
        تدريب نموذج DBSCAN.

        Args:
            X: بيانات التدريب (pd.DataFrame)
        """
        X = fill_missing(X)
        X_scaled = scale_numericals(X)
        self.model.fit(X_scaled)
        self.is_fitted = True
        logger.info("✅ تم تدريب نموذج DBSCAN.")

    def predict(self, X: pd.DataFrame):
        """
        توقعات التجميع للمشاهد الجديدة.

        Args:
            X: بيانات جديدة (pd.DataFrame)

        Returns:
            Cluster labels
        """
        if not self.is_fitted:
            raise ValueError("❌ النموذج غير مدرب بعد.")
        X = fill_missing(X)
        X_scaled = scale_numericals(X)
        return self.model.fit_predict(X_scaled)

    def save(self, filepath=None):
        """
        حفظ النموذج إلى ملف.
        """
        if not filepath:
            filepath = Path(self.model_dir) / f"{self.model_name}.pkl"
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        joblib.dump({
            "model": self.model,
            "scaler_type": self.scaler_type,
            "is_fitted": self.is_fitted
        }, filepath)
        logger.info(f"💾 تم حفظ نموذج DBSCAN في: {filepath}")

    def load(self, filepath=None):
        """
        تحميل النموذج من ملف.
        """
        if not filepath:
            filepath = Path(self.model_dir) / f"{self.model_name}.pkl"
        data = joblib.load(filepath)
        self.model = data["model"]
        self.scaler_type = data.get("scaler_type", "standard")
        self.is_fitted = data["is_fitted"]
        logger.info(f"📥 تم تحميل نموذج DBSCAN من: {filepath}")
