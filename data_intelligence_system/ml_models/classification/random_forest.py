import logging
from pathlib import Path
import joblib
from typing import Optional, List, Any
from sklearn.ensemble import RandomForestClassifier

# ✅ استيرادات من جذر المشروع
from data_intelligence_system.config.paths_config import ML_MODELS_DIR
from data_intelligence_system.ml_models.base_model import BaseModel
from data_intelligence_system.ml_models.utils.model_evaluation import ClassificationMetrics
from data_intelligence_system.ml_models.utils.preprocessing import DataPreprocessor
from data_intelligence_system.utils.preprocessing import fill_missing_values
from data_intelligence_system.utils.feature_utils import generate_derived_features
from data_intelligence_system.utils.timer import Timer

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class RandomForestModel(BaseModel):
    """
    نموذج Random Forest لتصنيف البيانات باستخدام scikit-learn.
    """

    def __init__(self, model_params: Optional[dict] = None, scaler_type: str = "standard") -> None:
        super().__init__(model_name="random_forest", model_dir=ML_MODELS_DIR)
        self.model_params = model_params or {}
        self.model = RandomForestClassifier(**self.model_params)
        self.preprocessor = DataPreprocessor(scaler_type=scaler_type)
        self.is_fitted: bool = False

    def _prepare_features(self, X, categorical_cols: Optional[List[str]] = None):
        if X is None or X.empty:
            raise ValueError("❌ بيانات الإدخال فارغة أو None.")
        X = fill_missing_values(X)
        X = generate_derived_features(X)
        if categorical_cols:
            X = self.preprocessor.encode_labels(X.copy(), categorical_cols)
        return self.preprocessor.transform_scaler(X)

    @Timer("تدريب نموذج Random Forest")
    def fit(self, X, y, categorical_cols=None):
        """
        تدريب النموذج وإرجاع مقاييس التقييم.
        """
        if X is None or y is None or len(X) == 0 or len(y) == 0:
            raise ValueError("❌ بيانات التدريب فارغة أو None.")
        if len(X) != len(y):
            raise ValueError("❌ عدد العينات غير متطابق بين X و y.")

        X = generate_derived_features(fill_missing_values(X))

        if categorical_cols:
            df = X.assign(target=y)
            X_train, X_test, y_train, y_test = self.preprocessor.preprocess(
                df, target_col="target", categorical_cols=categorical_cols, scale=True
            )
        else:
            X_train, X_test, y_train, y_test = self.preprocessor.split(X, y)

        self.model.fit(X_train, y_train)
        self.is_fitted = True
        logger.info("✅ تم تدريب نموذج Random Forest.")

        y_pred = self.model.predict(X_test)
        return ClassificationMetrics.all_metrics(y_test, y_pred, average="weighted")

    def predict(self, X, categorical_cols: Optional[List[str]] = None) -> Any:
        """
        تنفيذ التنبؤ باستخدام النموذج المدرب.
        """
        if not self.is_fitted:
            raise ValueError("❌ النموذج لم يتم تدريبه بعد. الرجاء استدعاء fit أولًا.")
        X_prepared = self._prepare_features(X, categorical_cols)
        return self.model.predict(X_prepared)

    def evaluate(self, X, y, categorical_cols: Optional[List[str]] = None) -> dict:
        """
        تقييم النموذج وإرجاع مقاييس التقييم.
        """
        if not self.is_fitted:
            raise ValueError("❌ النموذج لم يتم تدريبه بعد. الرجاء استدعاء fit أولًا.")
        X_prepared = self._prepare_features(X, categorical_cols)
        y_pred = self.model.predict(X_prepared)
        return ClassificationMetrics.all_metrics(y, y_pred, average="weighted")

    def save(self, filepath: Optional[str] = None) -> None:
        if self.model is None:
            raise ValueError("❌ لا يوجد نموذج لحفظه.")
        path = Path(filepath) if filepath else self.model_path
        path.parent.mkdir(parents=True, exist_ok=True)
        try:
            joblib.dump({
                "model": self.model,
                "preprocessor": self.preprocessor,
                "is_fitted": self.is_fitted
            }, path)
            logger.info(f"💾 تم حفظ النموذج في: {path}")
        except Exception as e:
            logger.error(f"❌ خطأ أثناء حفظ النموذج: {e}")

    def load(self, filepath: Optional[str] = None) -> None:
        path = Path(filepath) if filepath else self.model_path
        if not path.exists():
            raise FileNotFoundError(f"❌ لم يتم العثور على ملف النموذج: {path}")
        try:
            data = joblib.load(path)
            self.model = data["model"]
            self.preprocessor = data["preprocessor"]
            self.is_fitted = data["is_fitted"]
            logger.info(f"📥 تم تحميل النموذج من: {path}")
        except Exception as e:
            logger.error(f"❌ خطأ أثناء تحميل النموذج: {e}")
