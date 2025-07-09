import logging
import joblib
from pathlib import Path
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

# ✅ استيرادات من جذر المشروع
from data_intelligence_system.utils.preprocessing import fill_missing_values, scale_numericals
from data_intelligence_system.ml_models.base_model import BaseModel
from data_intelligence_system.utils.timer import Timer

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class KMeansClusteringModel(BaseModel):
    def __init__(
        self,
        n_clusters=3,
        init='k-means++',
        max_iter=300,
        random_state=None,
        scaler_type="standard",
        **kwargs
    ):
        """
        نموذج KMeans للتجميع غير الخاضع للإشراف.
        """
        super().__init__(model_name="kmeans_clustering", model_dir="data_intelligence_system/ml_models/saved_models")
        self.model = KMeans(
            n_clusters=n_clusters,
            init=init,
            max_iter=max_iter,
            random_state=random_state,
            **kwargs
        )
        self.scaler_type = scaler_type
        self.is_fitted = False

    @Timer("تدريب نموذج KMeans")
    def fit(self, X):
        """
        تدريب النموذج بعد التحجيم.
        """
        X = fill_missing_values(X)
        X_scaled = scale_numericals(X, method=self.scaler_type)
        self.model.fit(X_scaled)
        self.X_train_ = X_scaled
        self.is_fitted = True
        logger.info("✅ تم تدريب نموذج KMeans.")
        return self

    def predict(self, X):
        """
        توقع المجموعات.
        """
        self._check_is_fitted()
        X = fill_missing_values(X)
        X_scaled = scale_numericals(X, method=self.scaler_type)
        return self.model.predict(X_scaled)

    def get_cluster_centers(self):
        """
        عرض مراكز المجموعات.
        """
        self._check_is_fitted()
        return self.model.cluster_centers_

    def evaluate(self, X=None):
        """
        تقييم جودة التجميع باستخدام Silhouette Score.
        """
        self._check_is_fitted()
        if X is None and hasattr(self, "X_train_"):
            X = self.X_train_
        else:
            X = fill_missing_values(X)
            X = scale_numericals(X, method=self.scaler_type)
        labels = self.model.predict(X)
        score = silhouette_score(X, labels)
        logger.info(f"📈 Silhouette Score: {score:.4f}")
        return score

    def save(self):
        """
        حفظ النموذج.
        """
        if self.model is None:
            raise ValueError("❌ لا يوجد نموذج لحفظه.")
        self.model_path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump({
            "model": self.model,
            "scaler_type": self.scaler_type,
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
        self.model = data["model"]
        self.scaler_type = data.get("scaler_type", "standard")
        self.is_fitted = data["is_fitted"]
        logger.info(f"📥 تم تحميل النموذج من: {self.model_path}")
