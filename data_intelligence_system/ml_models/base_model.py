import os
import joblib
from pathlib import Path
from abc import ABC, abstractmethod
from datetime import datetime
import logging

from data_intelligence_system.utils.preprocessing import fill_missing_values
from data_intelligence_system.utils.timer import Timer

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
if not logger.hasHandlers():
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter('%(asctime)s | %(levelname)s | %(message)s'))
    logger.addHandler(handler)


class BaseModel(ABC):
    """
    كلاس أساسي مجرد لجميع نماذج تعلم الآلة.
    يوفر واجهة موحدة تشمل التدريب، التنبؤ، التقييم، الحفظ والتحميل.
    """

    def __init__(self, model_name: str, model_dir: str = "ml_models/saved_models"):
        self.model_name = model_name
        self.model_dir = Path(model_dir)
        self.model_path = self.model_dir / f"{self.model_name}.pkl"
        self.model = None
        self.is_fitted = False

        os.makedirs(self.model_dir, exist_ok=True)

    @abstractmethod
    def fit(self, X, y=None):
        """
        تدريب النموذج. يجب تنفيذه في الفئات الفرعية.
        """
        if hasattr(fill_missing_values, "__call__"):
            if X is not None:
                try:
                    X = fill_missing_values(X)
                except Exception:
                    pass
            if y is not None:
                try:
                    y = fill_missing_values(y)
                except Exception:
                    pass
        raise NotImplementedError

    @abstractmethod
    def predict(self, X):
        """
        توليد التنبؤات. يجب تنفيذه في الفئات الفرعية.
        """
        raise NotImplementedError

    @abstractmethod
    def evaluate(self, X, y):
        """
        تقييم النموذج. يجب تنفيذه في الفئات الفرعية.
        """
        raise NotImplementedError

    @Timer("💾 حفظ النموذج")
    def save(self):
        if self.model is None:
            raise ValueError("لا يوجد نموذج لحفظه.")
        try:
            joblib.dump(self.model, self.model_path)
            logger.info(f"[✔] تم حفظ النموذج إلى: {self.model_path}")
        except Exception as e:
            logger.error(f"❌ خطأ أثناء حفظ النموذج: {e}")
            raise

    @Timer("📥 تحميل النموذج")
    def load(self):
        if not self.model_path.exists():
            raise FileNotFoundError(f"لم يتم العثور على ملف النموذج: {self.model_path}")
        try:
            self.model = joblib.load(self.model_path)
            self.is_fitted = True
            logger.info(f"[✔] تم تحميل النموذج من: {self.model_path}")
            return self
        except Exception as e:
            logger.error(f"❌ خطأ أثناء تحميل النموذج: {e}")
            raise

    def _check_is_fitted(self):
        if not self.is_fitted:
            raise RuntimeError("النموذج لم يتم تدريبه بعد. الرجاء استدعاء fit() أولاً.")

    @Timer("📋 استعلام معلومات النموذج")
    def info(self):
        exists = self.model_path.exists()
        return {
            "model_name": self.model_name,
            "model_path": str(self.model_path),
            "is_fitted": self.is_fitted,
            "last_modified": datetime.fromtimestamp(self.model_path.stat().st_mtime).isoformat() if exists else "N/A"
        }

    def __repr__(self):
        return f"<BaseModel(name={self.model_name}, fitted={self.is_fitted})>"
