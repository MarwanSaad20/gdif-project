import os
import joblib
from pathlib import Path
from abc import ABC, abstractmethod
from datetime import datetime
import logging

from data_intelligence_system.data.processed.fill_missing import fill_missing  # ✅ استيراد fill_missing لدعم التكامل مع تحديثات معالجة القيم الناقصة

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
if not logger.hasHandlers():
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter('%(asctime)s | %(levelname)s | %(message)s'))
    logger.addHandler(handler)

class BaseModel(ABC):
    """
    كلاس أساسي مجرد (abstract) لجميع نماذج تعلم الآلة.
    يوفر واجهة موحدة للوراثة تشمل التدريب، التنبؤ، التقييم، الحفظ والتحميل.
    """

    def __init__(self, model_name: str, model_dir: str = "ml_models/saved_models"):
        """
        Args:
            model_name (str): اسم النموذج، يستخدم في حفظ الملفات.
            model_dir (str): مسار حفظ النماذج.
        """
        self.model_name = model_name
        self.model_dir = Path(model_dir)
        self.model_path = self.model_dir / f"{self.model_name}.pkl"
        self.model = None  # النموذج الفعلي (مثل sklearn model أو Prophet model)
        self.is_fitted = False  # تتبع حالة التدريب

        # إنشاء مجلد الحفظ إذا لم يكن موجودًا
        os.makedirs(self.model_dir, exist_ok=True)

    @abstractmethod
    def fit(self, X, y=None):
        """تدريب النموذج. يجب تنفيذه في الفئات الفرعية."""
        # قبل التدريب: معالجة القيم المفقودة باستخدام fill_missing إذا كان X أو y من نوع مناسب
        if hasattr(fill_missing, "__call__"):
            if X is not None:
                try:
                    X = fill_missing(X)
                except Exception:
                    pass
            if y is not None:
                try:
                    y = fill_missing(y)
                except Exception:
                    pass
        raise NotImplementedError

    @abstractmethod
    def predict(self, X):
        """توليد التنبؤات. يجب تنفيذه في الفئات الفرعية."""
        raise NotImplementedError

    @abstractmethod
    def evaluate(self, X, y):
        """تقييم النموذج. يجب تنفيذه في الفئات الفرعية."""
        raise NotImplementedError

    def save(self):
        """حفظ النموذج إلى ملف باستخدام joblib."""
        if self.model is None:
            raise ValueError("لا يوجد نموذج لحفظه.")
        try:
            joblib.dump(self.model, self.model_path)
            logger.info(f"[✔] تم حفظ النموذج إلى: {self.model_path}")
        except Exception as e:
            logger.error(f"❌ خطأ أثناء حفظ النموذج: {e}")
            raise

    def load(self):
        """تحميل النموذج من ملف."""
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
        """تأكد أن النموذج مدرب قبل التنبؤ أو التقييم."""
        if not self.is_fitted:
            raise RuntimeError("النموذج لم يتم تدريبه بعد. الرجاء استدعاء fit() أولاً.")

    def info(self):
        """إظهار معلومات عامة عن النموذج."""
        exists = self.model_path.exists()
        info = {
            "model_name": self.model_name,
            "model_path": str(self.model_path),
            "is_fitted": self.is_fitted,
            "last_modified": datetime.fromtimestamp(self.model_path.stat().st_mtime).isoformat() if exists else "N/A"
        }
        return info
