from pathlib import Path
import yaml

from data_intelligence_system.utils.logger import get_logger

# ✅ إعداد لوجر خاص
logger = get_logger("YAMLConfigHandler")

class YAMLConfigHandler:
    """
    معالج مخصص لتحميل إعدادات من ملفات YAML فقط.
    يشبه ConfigHandler ولكن مبسط ومخصص لـ YAML.
    """

    def __init__(self, config_path: str):
        path = Path(config_path)
        if not path.exists():
            logger.error(f"❌ ملف الإعدادات غير موجود: {config_path}")
            raise FileNotFoundError(f"ملف الإعدادات {config_path} غير موجود.")
        try:
            with open(path, "r", encoding="utf-8") as f:
                self.config = yaml.safe_load(f) or {}
            logger.info(f"✅ تم تحميل إعدادات YAML من: {config_path}")
        except yaml.YAMLError as e:
            logger.exception("❌ خطأ في قراءة ملف YAML.")
            raise ValueError(f"خطأ في قراءة ملف YAML: {e}")

    def get(self, key_path: str, default=None):
        """
        الوصول إلى الإعداد باستخدام dot notation (مثلاً: project.name).
        """
        keys = key_path.split(".")
        value = self.config
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                logger.warning(f"⚠️ المفتاح '{key_path}' غير موجود. سيتم استخدام القيمة الافتراضية.")
                return default
        return value

    def __getitem__(self, key):
        return self.config.get(key, None)

    def as_dict(self):
        return self.config
