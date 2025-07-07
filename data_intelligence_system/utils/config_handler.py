import json
import configparser
import os

# ✅ استيراد اللوجر المحدث من جذر المشروع
from data_intelligence_system.utils.logger import get_logger

try:
    import yaml
    _HAS_YAML = True
except ImportError:
    _HAS_YAML = False

# ✅ لوجر موحد
logger = get_logger(name="ConfigHandler")


class ConfigHandler:
    """
    فئة لتحميل وتفسير ملفات الإعدادات من JSON, YAML, INI.

    الاستخدام:
        config = ConfigHandler('config.yaml')
        value = config.get('section.key', default=None)
    """

    def __init__(self, filepath: str):
        self.filepath = filepath
        self.config_data = {}
        self._load()

    def _load(self):
        if not os.path.exists(self.filepath):
            raise FileNotFoundError(f"ملف الإعدادات غير موجود: {self.filepath}")

        ext = os.path.splitext(self.filepath)[1].lower()

        try:
            if ext in ['.yaml', '.yml']:
                if not _HAS_YAML:
                    raise ImportError("مكتبة PyYAML غير مثبتة. قم بتثبيتها باستخدام 'pip install pyyaml'")
                with open(self.filepath, 'r', encoding='utf-8') as f:
                    self.config_data = yaml.safe_load(f)

            elif ext == '.json':
                with open(self.filepath, 'r', encoding='utf-8') as f:
                    self.config_data = json.load(f)

            elif ext == '.ini':
                parser = configparser.ConfigParser()
                parser.read(self.filepath, encoding='utf-8')

                def _convert_value(value):
                    for conv in (int, float):
                        try:
                            return conv(value)
                        except ValueError:
                            continue
                    low = value.lower()
                    if low in ('true', 'yes', 'on'):
                        return True
                    elif low in ('false', 'no', 'off'):
                        return False
                    return value

                self.config_data = {
                    section: {k: _convert_value(v) for k, v in parser.items(section)}
                    for section in parser.sections()
                }

            else:
                raise ValueError(f"نوع ملف الإعدادات غير مدعوم: {ext}")

            if not isinstance(self.config_data, dict):
                logger.warning(f"محتوى الإعدادات في {self.filepath} ليس dict. قد يحدث سلوك غير متوقع.")

            logger.info(f"✅ تم تحميل الإعدادات من: {self.filepath}")

        except Exception as e:
            logger.error(f"❌ خطأ أثناء تحميل الإعدادات: {e}")
            raise

    def get(self, key: str, default=None):
        """
        استرجاع قيمة من الإعدادات باستخدام مفتاح نصي مثل 'section.subsection.key'.
        إذا لم يُعثر على المفتاح، يعيد القيمة الافتراضية.
        """
        keys = key.split('.')
        data = self.config_data
        try:
            for k in keys:
                data = data[k]
            return data
        except (KeyError, TypeError):
            logger.warning(f"⚠️ المفتاح '{key}' غير موجود. إرجاع القيمة الافتراضية.")
            return default

    def get_all(self):
        """إرجاع كل بيانات الإعدادات."""
        return self.config_data

    def reload(self):
        """إعادة تحميل ملف الإعدادات."""
        self._load()
