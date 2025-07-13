import os
import joblib
import logging
from pathlib import Path
from sklearn.linear_model import LogisticRegression

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


class LogisticRegressionModel(BaseModel):
    """
    نموذج الانحدار اللوجستي لتصنيف البيانات باستخدام scikit-learn.
    """

    def __init__(self, model_params=None, scaler_type="standard"):
        super().__init__(model_name="logistic_regression", model_dir=ML_MODELS_DIR)
        self.model_params = model_params if model_params else {}
        self.model = LogisticRegression(**self.model_params)
        self.preprocessor = DataPreprocessor(scaler_type=scaler_type)
        self.is_fitted = False
        self.categorical_cols = None

    def _prepare_features(self, X):
        """
        تجهيز البيانات: معالجة القيم المفقودة، الاشتقاق، التحجيم، الترميز.
        """
        X = fill_missing_values(X)
        X = generate_derived_features(X)
        if self.categorical_cols:
            X = self.preprocessor.encode_labels(X.copy(), self.categorical_cols)
        return self.preprocessor.transform_scaler(X)

    @Timer("تدريب نموذج الانحدار اللوجستي")
    def fit(self, X, y, categorical_cols=None):
        """
        تدريب النموذج على البيانات.
        """
        assert len(X) == len(y), "❌ عدد العينات غير متطابق بين X و y"
        if y is None or len(y) == 0:
            raise ValueError("❌ بيانات y فارغة.")

        self.categorical_cols = categorical_cols

        X = fill_missing_values(X)
        X = generate_derived_features(X)

        if categorical_cols:
            df = X.assign(target=y)
            X_train, X_test, y_train, y_test = self.preprocessor.preprocess(
                df, target_col="target", categorical_cols=categorical_cols, scale=True
            )
        else:
            X_train, X_test, y_train, y_test = self.preprocessor.split(X, y)

        X_train = self.preprocessor.unify_column_names(X_train)
        X_test = self.preprocessor.unify_column_names(X_test)

        self.model.fit(X_train, y_train)
        self.is_fitted = True
        logger.info("✅ تم تدريب نموذج الانحدار اللوجستي.")

        y_pred = self.model.predict(X_test)
        metrics = ClassificationMetrics.all_metrics(y_test, y_pred, average="binary")
        return metrics

    def predict(self, X):
        """
        توقع الفئات.
        """
        self._check_is_fitted()
        X_prepared = self._prepare_features(X)
        return self.model.predict(X_prepared)

    def predict_proba(self, X):
        """
        توقع الاحتمالات.
        """
        self._check_is_fitted()
        X_prepared = self._prepare_features(X)
        return self.model.predict_proba(X_prepared)

    def evaluate(self, X, y):
        """
        تقييم النموذج على بيانات جديدة.
        """
        self._check_is_fitted()
        X_prepared = self._prepare_features(X)
        y_pred = self.model.predict(X_prepared)
        return ClassificationMetrics.all_metrics(y, y_pred, average="binary")

    def save(self, filepath=None):
        """
        حفظ النموذج.
        """
        if self.model is None:
            raise ValueError("❌ لا يوجد نموذج لحفظه.")
        path = filepath or self.model_path
        os.makedirs(path.parent, exist_ok=True)
        joblib.dump({
            "model": self.model,
            "preprocessor": self.preprocessor,
            "is_fitted": self.is_fitted,
            "categorical_cols": self.categorical_cols
        }, path)
        logger.info(f"💾 تم حفظ النموذج في: {path}")

    def load(self, filepath=None):
        """
        تحميل النموذج.
        """
        path = filepath or self.model_path
        if not path.exists():
            raise FileNotFoundError(f"❌ لم يتم العثور على ملف النموذج: {path}")
        data = joblib.load(path)
        self.model = data["model"]
        self.preprocessor = data["preprocessor"]
        self.is_fitted = data["is_fitted"]
        self.categorical_cols = data.get("categorical_cols", None)
        logger.info(f"📥 تم تحميل النموذج من: {path}")
