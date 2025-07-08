import json
import configparser
from pathlib import Path
import logging

from data_intelligence_system.utils.logger import get_logger

try:
    import yaml
    _HAS_YAML = True
except ImportError:
    _HAS_YAML = False

logger = get_logger(name="ConfigHandler")


def convert_ini_value(value: str):
    """
    تحويل قيمة نصية من ملف ini إلى النوع المناسب (int, float, bool, أو str).
    """
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


class ConfigHandler:
    """
    فئة لتحميل وتفسير ملفات الإعدادات من JSON, YAML, INI.

    Usage:
        config = ConfigHandler('config.yaml')
        value = config.get('section.key', default=None)
    """

    def __init__(self, filepath: str, encoding: str = 'utf-8', lazy_load: bool = False):
        self.filepath = Path(filepath)
        self.encoding = encoding
        self.config_data = {}
        if not lazy_load:
            self._load()

    def _load(self):
        if not self.filepath.exists():
            raise FileNotFoundError(f"ملف الإعدادات غير موجود: {self.filepath}")

        ext = self.filepath.suffix.lower()

        try:
            if ext in ['.yaml', '.yml']:
                if not _HAS_YAML:
                    raise ImportError("مكتبة PyYAML غير مثبتة. قم بتثبيتها باستخدام 'pip install pyyaml'")
                with self.filepath.open('r', encoding=self.encoding) as f:
                    self.config_data = yaml.safe_load(f)

            elif ext == '.json':
                with self.filepath.open('r', encoding=self.encoding) as f:
                    self.config_data = json.load(f)

            elif ext == '.ini':
                parser = configparser.ConfigParser()
                parser.read(self.filepath, encoding=self.encoding)
                self.config_data = {
                    section: {k: convert_ini_value(v) for k, v in parser.items(section)}
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
        if not isinstance(self.config_data, dict):
            logger.warning(f"⚠️ بيانات الإعدادات ليست من نوع dict، لا يمكن الوصول للمفتاح '{key}'.")
            return default

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
