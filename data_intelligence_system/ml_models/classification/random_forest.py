import logging
import joblib
from pathlib import Path
from sklearn.ensemble import RandomForestClassifier

from data_intelligence_system.ml_models.base_model import BaseModel
from data_intelligence_system.ml_models.utils.model_evaluation import ClassificationMetrics
from data_intelligence_system.ml_models.utils.preprocessing import DataPreprocessor
from data_intelligence_system.utils.preprocessing import fill_missing_values
from data_intelligence_system.utils.feature_utils import generate_derived_features
from data_intelligence_system.utils.timer import Timer

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class RandomForestModel(BaseModel):
    def __init__(self, model_params=None, scaler_type="standard"):
        super().__init__(model_name="random_forest", model_dir="ml_models/saved_models")
        self.model_params = model_params if model_params else {}
        self.model = RandomForestClassifier(**self.model_params)
        self.preprocessor = DataPreprocessor(scaler_type=scaler_type)
        self.is_fitted = False

    def _prepare_features(self, X, categorical_cols=None):
        X = fill_missing_values(X)
        if categorical_cols:
            X = self.preprocessor.encode_labels(X.copy(), categorical_cols)
        return self.preprocessor.transform_scaler(X)

    @Timer("تدريب نموذج Random Forest")
    def fit(self, X, y, categorical_cols=None):
        X = fill_missing_values(X)
        X = generate_derived_features(X)

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
        return ClassificationMetrics.all_metrics(y_test, y_pred, average="binary")

    def predict(self, X, categorical_cols=None):
        self._check_is_fitted()
        X = self._prepare_features(X, categorical_cols)
        return self.model.predict(X)

    def predict_proba(self, X, categorical_cols=None):
        self._check_is_fitted()
        X = self._prepare_features(X, categorical_cols)
        return self.model.predict_proba(X)

    def evaluate(self, X, y, categorical_cols=None):
        self._check_is_fitted()
        X = fill_missing_values(X)
        y_pred = self.predict(X, categorical_cols)
        return ClassificationMetrics.all_metrics(y, y_pred, average="binary")

    def save(self):
        if self.model is None:
            raise ValueError("❌ لا يوجد نموذج لحفظه.")
        self.model_path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump({
            "model": self.model,
            "preprocessor": self.preprocessor,
            "is_fitted": self.is_fitted
        }, self.model_path)
        logger.info(f"💾 تم حفظ النموذج في: {self.model_path}")

    def load(self):
        if not self.model_path.exists():
            raise FileNotFoundError(f"❌ لم يتم العثور على ملف النموذج: {self.model_path}")
        data = joblib.load(self.model_path)
        self.model = data["model"]
        self.preprocessor = data["preprocessor"]
        self.is_fitted = data["is_fitted"]
        logger.info(f"📥 تم تحميل النموذج من: {self.model_path}")
