import logging
import joblib
from pathlib import Path
import pandas as pd
from sklearn.cluster import DBSCAN

from data_intelligence_system.ml_models.base_model import BaseModel
from data_intelligence_system.utils.preprocessing import fill_missing_values
from data_intelligence_system.utils.feature_utils import generate_derived_features
from data_intelligence_system.utils.timer import Timer

logger = logging.getLogger(__name__)


class DBSCANClusteringModel(BaseModel):
    """
    نموذج تجميع باستخدام DBSCAN.
    """

    def __init__(self, model_params=None, scaler_type="standard"):
        """
        Parameters
        ----------
        model_params : dict, optional
            معلمات نموذج DBSCAN.
        scaler_type : str, optional
            نوع المقياس المستخدم قبل التدريب.
        """
        super().__init__(
            model_name="dbscan_clustering",
            model_dir="data_intelligence_system/ml_models/saved_models"
        )
        self.model_params = model_params or {}
        self.model = DBSCAN(**self.model_params)
        self.scaler_type = scaler_type
        self.is_fitted = False

    @Timer("تدريب نموذج DBSCAN")
    def fit(self, X: pd.DataFrame):
        """
        تدريب نموذج DBSCAN.
        """
        if X is None or X.empty:
            raise ValueError("❌ بيانات الإدخال فارغة أو None.")

        try:
            X = fill_missing_values(X)
            X = generate_derived_features(X)
        except Exception as e:
            logger.error(f"⚠️ خطأ أثناء معالجة البيانات قبل التدريب: {e}")
            raise

        self.model.fit(X)
        self.is_fitted = True
        logger.info("✅ تم تدريب نموذج DBSCAN بنجاح.")

    def predict(self, X: pd.DataFrame):
        """
        توقعات التجميع للمشاهد الجديدة.
        """
        self._check_is_fitted()

        if X is None or X.empty:
            raise ValueError("❌ بيانات الإدخال فارغة أو None.")

        try:
            X = fill_missing_values(X)
            X = generate_derived_features(X)
        except Exception as e:
            logger.error(f"⚠️ خطأ أثناء معالجة البيانات قبل التنبؤ: {e}")
            raise

        # DBSCAN لا يدعم predict للمشاهد الجديدة مباشرةً،
        # لذا نعيد fit_predict (مع العلم أن هذا يعيد تدريب النموذج)
        return self.model.fit_predict(X)

    def save(self):
        """
        حفظ النموذج إلى ملف.
        """
        if self.model is None:
            raise ValueError("❌ لا يوجد نموذج لحفظه.")

        self.model_path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump({
            "model": self.model,
            "scaler_type": self.scaler_type,
            "is_fitted": self.is_fitted
        }, self.model_path)
        logger.info(f"💾 تم حفظ نموذج DBSCAN في: {self.model_path}")

    def load(self):
        """
        تحميل النموذج من ملف.
        """
        if not self.model_path.exists():
            raise FileNotFoundError(f"❌ لم يتم العثور على ملف النموذج: {self.model_path}")

        data = joblib.load(self.model_path)
        self.model = data["model"]
        self.scaler_type = data.get("scaler_type", "standard")
        self.is_fitted = data["is_fitted"]
        logger.info(f"📥 تم تحميل نموذج DBSCAN من: {self.model_path}")
