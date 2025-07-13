from pathlib import Path
import yaml
from typing import Any, Optional
from functools import lru_cache

from data_intelligence_system.utils.logger import get_logger

logger = get_logger("YAMLConfigHandler")


class YAMLConfigHandler:
    """
    معالج مخصص لتحميل إعدادات من ملفات YAML فقط.
    يشبه ConfigHandler ولكن مبسط ومخصص لـ YAML.

    يوفر إمكانية الوصول إلى القيم باستخدام dot notation (مثلاً: "project.name").
    يدعم إعادة تحميل الملف وتحديث القيم داخليًا.
    """

    def __init__(self, config_path: str):
        """
        تهيئة المحلل وتحميل ملف الإعدادات.

        Args:
            config_path (str): مسار ملف YAML.

        Raises:
            FileNotFoundError: إذا لم يكن الملف موجودًا.
            ValueError: في حال وجود خطأ أثناء قراءة الملف.
        """
        self.config_path = Path(config_path)
        if not self.config_path.exists():
            logger.error(f"❌ ملف الإعدادات غير موجود: {config_path}")
            raise FileNotFoundError(f"ملف الإعدادات {config_path} غير موجود.")
        self.reload()

    def reload(self) -> None:
        """
        إعادة تحميل إعدادات YAML من الملف.
        """
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                self.config = yaml.safe_load(f) or {}
            logger.info(f"✅ تم تحميل إعدادات YAML من: {self.config_path}")
            self._clear_cache()
        except yaml.YAMLError as e:
            logger.exception("❌ خطأ في قراءة ملف YAML.")
            raise ValueError(f"خطأ في قراءة ملف YAML: {e}")

    def _clear_cache(self):
        # لمسح ذاكرة التخزين المؤقتة لدالة get
        try:
            self.get.cache_clear()
        except AttributeError:
            pass

    @lru_cache(maxsize=256)
    def get(self, key_path: str, default: Optional[Any] = None) -> Any:
        """
        الوصول إلى الإعداد باستخدام dot notation (مثلاً: "project.name").

        Args:
            key_path (str): المسار الكامل للمفتاح مفصول بنقاط.
            default (Any): القيمة الافتراضية إذا لم يوجد المفتاح.

        Returns:
            Any: القيمة المطلوبة أو القيمة الافتراضية.
        """
        if not key_path:
            logger.warning("⚠️ تم طلب مفتاح فارغ في get()، إعادة القاموس الكامل.")
            return self.config

        keys = key_path.split(".")
        value = self.config

        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                # أقل حدة في اللوجر لتقليل الضجيج، يمكن رفعها حسب الحاجة
                logger.debug(f"المفتاح '{key_path}' غير موجود، إعادة القيمة الافتراضية.")
                return default
        return value

    def set(self, key_path: str, value: Any) -> None:
        """
        تحديث قيمة في الإعدادات باستخدام dot notation.

        Args:
            key_path (str): المسار الكامل للمفتاح مفصول بنقاط.
            value (Any): القيمة الجديدة.
        """
        if not key_path:
            logger.error("❌ تعذر تعيين قيمة لمفتاح فارغ.")
            raise ValueError("المفتاح لا يمكن أن يكون فارغًا.")

        keys = key_path.split(".")
        d = self.config
        for key in keys[:-1]:
            if key not in d or not isinstance(d[key], dict):
                d[key] = {}
            d = d[key]
        d[keys[-1]] = value
        self._clear_cache()
        logger.info(f"✅ تم تعيين المفتاح '{key_path}' إلى القيمة: {value}")

    def __getitem__(self, key: str) -> Any:
        # دعم الوصول كقائمة (لكن بدون dot notation هنا)
        return self.config.get(key, None)

    def __contains__(self, key: str) -> bool:
        return key in self.config

    def as_dict(self) -> dict:
        """
        إرجاع نسخة من إعدادات YAML كقاموس.

        Returns:
            dict: نسخة من الإعدادات.
        """
        return self.config.copy()
