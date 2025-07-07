import os
import joblib
import logging
from pathlib import Path
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from data_intelligence_system.data.processed.fill_missing import fill_missing
from data_intelligence_system.data.processed.scale_numericals import scale_numericals  # ✅ جديد
from data_intelligence_system.ml_models.base_model import BaseModel

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class KMeansClusteringModel(BaseModel):
    def __init__(self, n_clusters=3, init='k-means++', max_iter=300, random_state=None, scaler_type="standard", **kwargs):
        """
        نموذج KMeans للتجميع غير الخاضع للإشراف.
        """
        super().__init__(model_name="kmeans_clustering", model_dir="ml_models/saved_models")
        self.model = KMeans(
            n_clusters=n_clusters,
            init=init,
            max_iter=max_iter,
            random_state=random_state,
            **kwargs
        )
        self.scaler_type = scaler_type  # للاحتفاظ لو احتجنا
        self.is_fitted = False

    def fit(self, X):
        """
        تدريب النموذج بعد التحجيم.
        """
        X = fill_missing(X)  # تنظيف القيم المفقودة
        X_scaled = scale_numericals(X)  # استخدام دالة التحجيم الموحدة
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
        X = fill_missing(X)
        X_scaled = scale_numericals(X)
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
            X = fill_missing(X)
            X = scale_numericals(X)
        labels = self.model.predict(X)
        score = silhouette_score(X, labels)
        logger.info(f"📈 Silhouette Score: {score:.4f}")
        return score

    def save(self, filepath=None):
        if not filepath:
            filepath = Path(self.model_dir) / f"{self.model_name}.pkl"
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        joblib.dump({
            "model": self.model,
            "scaler_type": self.scaler_type,
            "is_fitted": self.is_fitted
        }, filepath)
        logger.info(f"💾 تم حفظ النموذج في: {filepath}")

    def load(self, filepath=None):
        if not filepath:
            filepath = Path(self.model_dir) / f"{self.model_name}.pkl"
        data = joblib.load(filepath)
        self.model = data["model"]
        self.scaler_type = data.get("scaler_type", "standard")
        self.is_fitted = data["is_fitted"]
        logger.info(f"📥 تم تحميل النموذج من: {filepath}")
