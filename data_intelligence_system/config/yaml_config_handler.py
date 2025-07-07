# config/yaml_config_handler.py

import yaml
from pathlib import Path

class ConfigHandler:
    def __init__(self, config_path: str):
        path = Path(config_path)
        if not path.exists():
            raise FileNotFoundError(f"ملف الإعدادات {config_path} غير موجود.")
        try:
            with open(path, "r", encoding="utf-8") as f:
                self.config = yaml.safe_load(f) or {}
        except yaml.YAMLError as e:
            raise ValueError(f"خطأ في قراءة ملف YAML: {e}")

    def get(self, key_path: str, default=None):
        """الوصول إلى الإعداد باستخدام dot notation (مثلاً: project.name)"""
        keys = key_path.split(".")
        value = self.config
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        return value

    def __getitem__(self, key):
        return self.config.get(key, None)

    def as_dict(self):
        return self.config
