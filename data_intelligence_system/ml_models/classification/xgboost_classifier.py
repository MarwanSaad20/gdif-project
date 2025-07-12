import logging
import joblib
from pathlib import Path
from typing import Optional, List

from xgboost import XGBClassifier

# ✅ استيراد من جذر المشروع
from data_intelligence_system.config.paths_config import ML_MODELS_DIR
from data_intelligence_system.ml_models.base_model import BaseModel
from data_intelligence_system.ml_models.utils.model_evaluation import ClassificationMetrics
from data_intelligence_system.ml_models.utils.preprocessing import DataPreprocessor
from data_intelligence_system.utils.preprocessing import fill_missing_values
from data_intelligence_system.utils.feature_utils import generate_derived_features
from data_intelligence_system.utils.timer import Timer

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class XGBoostClassifierModel(BaseModel):
    """
    نموذج XGBoost لتصنيف البيانات باستخدام scikit-learn.
    """

    def __init__(
        self,
        model_params: Optional[dict] = None,
        scaler_type: str = "standard"
    ):
        super().__init__(model_name="xgboost_classifier", model_dir=ML_MODELS_DIR)
        self.model_params = model_params if model_params else {}
        self.model = XGBClassifier(use_label_encoder=False, eval_metric='logloss', **self.model_params)
        self.preprocessor = DataPreprocessor(scaler_type=scaler_type)
        self.is_fitted = False

    def _prepare_features(self, X, categorical_cols: Optional[List[str]] = None):
        """
        تنظيف وتحضير الميزات للتنبؤ أو التدريب.
        """
        if X is None or X.empty:
            raise ValueError("❌ بيانات الإدخال فارغة أو None.")
        X = fill_missing_values(X)
        X = generate_derived_features(X)
        if categorical_cols:
            X = self.preprocessor.encode_labels(X.copy(), categorical_cols)
        return self.preprocessor.transform_scaler(X)

    @Timer("تدريب نموذج XGBoost")
    def fit(self, X, y, categorical_cols: Optional[List[str]] = None):
        """
        تدريب النموذج مع تقسيم البيانات، وإرجاع مقاييس التقييم.

        Raises
        ------
        ValueError: إذا كانت البيانات غير متناسقة أو فارغة.
        """
        if X is None or y is None:
            raise ValueError("❌ بيانات التدريب أو الهدف فارغة.")
        if len(X) != len(y):
            raise ValueError("❌ عدد العينات في X و y غير متطابق.")

        X_processed = self._prepare_features(X, categorical_cols)

        if categorical_cols:
            df = X_processed.assign(target=y)
            X_train, X_test, y_train, y_test = self.preprocessor.preprocess(
                df, target_col="target", categorical_cols=categorical_cols, scale=True
            )
        else:
            X_train, X_test, y_train, y_test = self.preprocessor.split(X_processed, y)

        try:
            self.model.fit(X_train, y_train)
            self.is_fitted = True
            logger.info("✅ تم تدريب نموذج XGBoost.")
        except Exception as e:
            logger.error(f"❌ خطأ أثناء تدريب النموذج: {e}")
            raise

        y_pred = self.model.predict(X_test)

        avg_method = "binary" if len(set(y)) == 2 else "weighted"

        return ClassificationMetrics.all_metrics(y_test, y_pred, average=avg_method)

    def predict(self, X, categorical_cols: Optional[List[str]] = None):
        """
        التنبؤ بالفئات باستخدام النموذج المدرب.
        """
        self._check_is_fitted()
        X_prepared = self._prepare_features(X, categorical_cols)
        return self.model.predict(X_prepared)

    def predict_proba(self, X, categorical_cols: Optional[List[str]] = None):
        """
        التنبؤ باحتمالات الفئات.
        """
        self._check_is_fitted()
        X_prepared = self._prepare_features(X, categorical_cols)
        return self.model.predict_proba(X_prepared)

    def evaluate(self, X, y, categorical_cols: Optional[List[str]] = None):
        """
        تقييم النموذج باستخدام بيانات الاختبار.
        """
        self._check_is_fitted()
        if X is None or y is None:
            raise ValueError("❌ بيانات التقييم أو الهدف فارغة.")

        X_prepared = self._prepare_features(X, categorical_cols)
        y_pred = self.model.predict(X_prepared)

        avg_method = "binary" if len(set(y)) == 2 else "weighted"

        return ClassificationMetrics.all_metrics(y, y_pred, average=avg_method)

    def save(self):
        """
        حفظ النموذج والإعدادات.
        """
        if self.model is None:
            raise ValueError("❌ لا يوجد نموذج لحفظه.")
        try:
            self.model_path.parent.mkdir(parents=True, exist_ok=True)
            joblib.dump({
                "model": self.model,
                "preprocessor": self.preprocessor,
                "is_fitted": self.is_fitted
            }, self.model_path)
            logger.info(f"💾 تم حفظ النموذج في: {self.model_path}")
        except Exception as e:
            logger.error(f"❌ خطأ أثناء حفظ النموذج: {e}")
            raise

    def load(self):
        """
        تحميل النموذج والإعدادات.
        """
        if not self.model_path.exists():
            raise FileNotFoundError(f"❌ لم يتم العثور على ملف النموذج: {self.model_path}")
        try:
            data = joblib.load(self.model_path)
            self.model = data["model"]
            self.preprocessor = data["preprocessor"]
            self.is_fitted = data["is_fitted"]
            logger.info(f"📥 تم تحميل النموذج من: {self.model_path}")
        except Exception as e:
            logger.error(f"❌ خطأ أثناء تحميل النموذج: {e}")
            raise
