import pytest
from config.config_loader import CONFIG
import os

@pytest.fixture(scope="module")
def config():
    """Fixture مشترك لاستخدام CONFIG في كل الاختبارات"""
    return CONFIG


def test_paths_config(config):
    """✅ اختبار وجود وتكامل إعدادات المسارات"""
    assert hasattr(config.paths, "RAW_DATA_DIR")
    assert hasattr(config.paths, "PROCESSED_DATA_DIR")
    assert hasattr(config.paths, "EXTERNAL_DATA_DIR")
    assert hasattr(config.paths, "DATA_PROFILES_DIR")

    assert str(config.paths.PROCESSED_DATA_DIR).replace("\\", "/").endswith("data/processed")
    assert str(config.paths.RAW_DATA_DIR).replace("\\", "/").endswith("data/raw")


def test_model_config(config):
    """✅ التحقق من إعدادات النماذج"""
    assert hasattr(config.models, "CLASSIFICATION_MODELS")
    assert isinstance(config.models.CLASSIFICATION_MODELS, dict)
    assert "random_forest" in config.models.CLASSIFICATION_MODELS
    assert "xgboost" in config.models.CLASSIFICATION_MODELS

    if hasattr(config.models, "TIME_SERIES_MODELS"):
        assert "prophet" in config.models.TIME_SERIES_MODELS
        assert "arima" in config.models.TIME_SERIES_MODELS


def test_report_config(config):
    """✅ التحقق من إعدادات التقارير"""
    assert hasattr(config.reports, "REPORT_TITLE")
    assert "تحليل البيانات" in config.reports.REPORT_TITLE

    assert hasattr(config.reports, "TEMPLATE_PATH")
    template_path_str = str(config.reports.TEMPLATE_PATH).replace("\\", "/")
    # السماح بأن يكون TEMPLATE_PATH إما مجلد templates أو ملف داخل هذا المجلد
    assert (
        template_path_str.endswith("reports/generators/templates")
        or template_path_str.endswith("reports/generators/templates/base_report.html")
    )

    assert hasattr(config.reports, "OUTPUT_FORMATS")
    assert isinstance(config.reports.OUTPUT_FORMATS, list)
    assert "pdf" in config.reports.OUTPUT_FORMATS
    assert "html" in config.reports.OUTPUT_FORMATS


def test_dashboard_config(config):
    """✅ التحقق من إعدادات لوحة التحكم"""
    assert hasattr(config.dashboard, "KPI_SETTINGS")
    assert isinstance(config.dashboard.KPI_SETTINGS, dict)

    assert hasattr(config.dashboard, "REFRESH_INTERVAL")
    assert isinstance(config.dashboard.REFRESH_INTERVAL, int)


def test_env_config(config, monkeypatch):
    """✅ التحقق من إعدادات البيئة وتغيراتها"""

    assert hasattr(config.env, "DEBUG_MODE")
    assert isinstance(config.env.DEBUG_MODE, bool)

    # تغيير مؤقت للغة البيئة
    monkeypatch.setenv("APP_LANGUAGE", "en")
    lang = getattr(config.env, "LANGUAGE", None)
    assert lang in ["ar", "en"], f"لغة البيئة يجب أن تكون ar أو en وليس {lang}"

    assert hasattr(config.env, "DATABASE_URL")
    # تعديل هنا ليقبل postgresql أو sqlite
    assert config.env.DATABASE_URL.startswith(("postgresql://", "sqlite://"))

    # تجربة تغيير اللغة مرة أخرى
    monkeypatch.setenv("APP_LANGUAGE", "ar")
    lang2 = getattr(config.env, "LANGUAGE", None)
    assert lang2 in ["ar", "en"]


def test_config_integrity(config):
    """✅ التأكد من وجود كل الأقسام في CONFIG"""
    required_sections = ["paths", "models", "reports", "dashboard", "env"]
    for section in required_sections:
        assert hasattr(config, section), f"❌ config يفتقد القسم: {section}"
