import logging
import joblib
from pathlib import Path
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

from data_intelligence_system.utils.preprocessing import fill_missing_values, scale_numericals
from data_intelligence_system.ml_models.base_model import BaseModel
from data_intelligence_system.utils.timer import Timer

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class KMeansClusteringModel(BaseModel):
    def __init__(
        self,
        n_clusters: int = 3,
        init: str = 'k-means++',
        max_iter: int = 300,
        random_state: int = 42,
        scaler_type: str = "standard",
        **kwargs
    ):
        """
        نموذج KMeans للتجميع غير الخاضع للإشراف.

        Parameters
        ----------
        n_clusters : int
            عدد المجموعات.
        init : str
            طريقة التهيئة.
        max_iter : int
            أقصى عدد للتكرارات.
        random_state : int
            البذرة العشوائية لضمان التكرار.
        scaler_type : str
            نوع التحجيم المستخدم (مثلاً "standard").
        kwargs : dict
            معلمات إضافية لنموذج KMeans.
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
        self.X_train_ = None

    @Timer("تدريب نموذج KMeans")
    def fit(self, X):
        """
        تدريب النموذج بعد معالجة القيم المفقودة والتحجيم.

        Parameters
        ----------
        X : pd.DataFrame
            بيانات السمات.

        Returns
        -------
        self
        """
        if X is None or X.empty:
            raise ValueError("❌ بيانات الإدخال فارغة أو None.")
        X = fill_missing_values(X)
        # التعديل الأساسي هنا: استخدم scaler وليس method
        X_scaled = scale_numericals(X, scaler=self.scaler_type)
        self.model.fit(X_scaled)
        self.X_train_ = X_scaled
        self.is_fitted = True
        logger.info("✅ تم تدريب نموذج KMeans.")
        return self

    def predict(self, X):
        """
        توقع المجموعات للبيانات الجديدة.

        Parameters
        ----------
        X : pd.DataFrame
            بيانات السمات.

        Returns
        -------
        np.ndarray
            تسميات المجموعات المتوقعة.
        """
        self._check_is_fitted()
        if X is None or X.empty:
            raise ValueError("❌ بيانات الإدخال فارغة أو None.")
        X = fill_missing_values(X)
        X_scaled = scale_numericals(X, scaler=self.scaler_type)
        return self.model.predict(X_scaled)

    def get_cluster_centers(self):
        """
        عرض مراكز المجموعات.

        Returns
        -------
        np.ndarray
            مراكز المجموعات.
        """
        self._check_is_fitted()
        return self.model.cluster_centers_

    def evaluate(self, X=None):
        """
        تقييم جودة التجميع باستخدام مؤشر Silhouette Score.

        Parameters
        ----------
        X : pd.DataFrame, optional
            بيانات لتقييم التجميع عليها، إذا لم تقدم تستخدم بيانات التدريب.

        Returns
        -------
        float
            قيمة Silhouette Score.
        """
        self._check_is_fitted()
        if X is None:
            if self.X_train_ is None:
                raise ValueError("❌ لا توجد بيانات للتقييم.")
            X_eval = self.X_train_
        else:
            if X.empty:
                raise ValueError("❌ بيانات التقييم فارغة.")
            X_eval = fill_missing_values(X)
            X_eval = scale_numericals(X_eval, scaler=self.scaler_type)
        labels = self.model.predict(X_eval)
        score = silhouette_score(X_eval, labels)
        logger.info(f"📈 Silhouette Score: {score:.4f}")
        return score

    def save(self):
        """
        حفظ النموذج على المسار المحدد.
        """
        if self.model is None:
            raise ValueError("❌ لا يوجد نموذج لحفظه.")
        self.model_path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump({
            "model": self.model,
            "scaler_type": self.scaler_type,
            "is_fitted": self.is_fitted,
            "X_train_": self.X_train_,
        }, self.model_path)
        logger.info(f"💾 تم حفظ النموذج في: {self.model_path}")

    def load(self):
        """
        تحميل النموذج من المسار المحدد.
        """
        if not self.model_path.exists():
            raise FileNotFoundError(f"❌ لم يتم العثور على ملف النموذج: {self.model_path}")
        data = joblib.load(self.model_path)
        self.model = data["model"]
        self.scaler_type = data.get("scaler_type", "standard")
        self.is_fitted = data["is_fitted"]
        self.X_train_ = data.get("X_train_", None)
        logger.info(f"📥 تم تحميل النموذج من: {self.model_path}")
