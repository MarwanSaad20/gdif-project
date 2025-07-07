# ml_models/classification/random_forest.py

import os
import joblib
import logging
from pathlib import Path
import pandas as pd
from sklearn.ensemble import RandomForestClassifier

from data_intelligence_system.ml_models.base_model import BaseModel
from data_intelligence_system.ml_models.utils.model_evaluation import ClassificationMetrics
from data_intelligence_system.ml_models.utils.preprocessing import DataPreprocessor
from data_intelligence_system.data.processed.fill_missing import fill_missing  # ✅ تكامل مباشر مع تنظيف البيانات
from data_intelligence_system.utils.data_loader import load_data  # ✅ تحضير لاستيراد التحميل من جذر المشروع

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class RandomForestModel(BaseModel):
    def __init__(self, model_params=None, scaler_type="standard"):
        """
        نموذج تصنيف باستخدام Random Forest.
        """
        super().__init__(model_name="random_forest", model_dir="ml_models/saved_models")
        self.model_params = model_params if model_params else {}
        self.model = RandomForestClassifier(**self.model_params)
        self.preprocessor = DataPreprocessor(scaler_type=scaler_type)
        self.is_fitted = False

    def _prepare_features(self, X, categorical_cols=None):
        X = fill_missing(X)  # ✅ تنظيف القيم المفقودة
        if categorical_cols:
            X = self.preprocessor.encode_labels(X.copy(), categorical_cols)
        return self.preprocessor.transform_scaler(X)

    def fit(self, X, y, categorical_cols=None):
        X = fill_missing(X)  # ✅ تنظيف القيم المفقودة

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
        if not self.is_fitted:
            raise ValueError("❌ النموذج غير مدرب بعد.")
        X = self._prepare_features(X, categorical_cols)
        return self.model.predict(X)

    def predict_proba(self, X, categorical_cols=None):
        if not self.is_fitted:
            raise ValueError("❌ النموذج غير مدرب بعد.")
        X = self._prepare_features(X, categorical_cols)
        return self.model.predict_proba(X)

    def evaluate(self, X, y, categorical_cols=None):
        if not self.is_fitted:
            raise ValueError("❌ النموذج غير مدرب بعد.")
        X = fill_missing(X)  # ✅ تنظيف القيم المفقودة
        y_pred = self.predict(X, categorical_cols)
        return ClassificationMetrics.all_metrics(y, y_pred, average="binary")

    def save(self, filepath=None):
        if not filepath:
            filepath = Path(self.model_dir) / f"{self.model_name}.pkl"
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        joblib.dump({
            "model": self.model,
            "preprocessor": self.preprocessor,
            "is_fitted": self.is_fitted
        }, filepath)
        logger.info(f"💾 تم حفظ النموذج في: {filepath}")

    def load(self, filepath=None):
        if not filepath:
            filepath = Path(self.model_dir) / f"{self.model_name}.pkl"
        data = joblib.load(filepath)
        self.model = data["model"]
        self.preprocessor = data["preprocessor"]
        self.is_fitted = data["is_fitted"]
        logger.info(f"📥 تم تحميل النموذج من: {filepath}")
