# tests/test_config.py

import os
from pathlib import Path
import pytest
from types import SimpleNamespace

# ✅ استيراد CONFIG والمكونات الرئيسية من config/
from data_intelligence_system.config import (
    config_loader,
    env_config,
    paths_config,
    model_config,
    report_config,
    dashboard_config
)


# ===================== CONFIG Loader & env_config =====================
def test_config_object_loaded():
    """تأكد من تحميل CONFIG كـ SimpleNamespace ويحتوي المفاتيح الرئيسية."""
    assert isinstance(config_loader.CONFIG, SimpleNamespace)
    expected_sections = ['paths', 'models', 'reports', 'dashboard', 'env', 'yaml']
    for section in expected_sections:
        assert hasattr(config_loader.CONFIG, section), f"CONFIG ينقصه القسم: {section}"


def test_env_namespace_values():
    """تأكد أن env_namespace يحتوي بيانات صحيحة."""
    env = env_config.env_namespace
    assert env.PROJECT_NAME, "PROJECT_NAME يجب ألا يكون فارغًا"
    assert env.DATABASE_URL.startswith(("sqlite", "postgresql", "mysql")), "DATABASE_URL غير صالح"
    assert isinstance(env.EMAIL_CONFIG, dict)
    assert "sender" in env.EMAIL_CONFIG
    assert isinstance(env.RAW_DATA_PATH, Path) and env.RAW_DATA_PATH.exists()
    assert isinstance(env.PROCESSED_DATA_PATH, Path) and env.PROCESSED_DATA_PATH.exists()


# ===================== paths_config =====================
def test_paths_config_directories_exist():
    """تأكد أن المسارات المهمة موجودة."""
    important_dirs = [
        paths_config.DATA_DIR,
        paths_config.RAW_DATA_DIR,
        paths_config.PROCESSED_DATA_DIR,
        paths_config.EDA_OUTPUT_DIR,
        paths_config.REPORT_OUTPUT_DIR,
        paths_config.ML_MODELS_DIR,
        paths_config.DASHBOARD_DIR,
        paths_config.REPORTS_DIR,
        paths_config.TESTS_DIR,
    ]
    for dir_path in important_dirs:
        assert dir_path.exists(), f"المسار مفقود: {dir_path}"


def test_paths_config_shortcuts_are_strings():
    """تأكد أن المسارات المختصرة موجودة كسلاسل نصية."""
    assert isinstance(paths_config.RAW_DIR, str)
    assert isinstance(paths_config.PROCESSED_DIR, str)


# ===================== model_config =====================
def test_model_config_basic_values():
    """تأكد من القيم الأساسية في model_config."""
    assert isinstance(model_config.RANDOM_STATE, int)
    assert isinstance(model_config.TEST_SIZE, (float, int))
    assert isinstance(model_config.VALIDATION_SPLIT, (float, int))
    assert isinstance(model_config.CROSS_VALIDATION_FOLDS, int)
    assert isinstance(model_config.SCALING_METHOD, str)


def test_model_config_models_are_dicts():
    """تأكد أن إعدادات النماذج عبارة عن قواميس."""
    assert isinstance(model_config.REGRESSION_MODELS, dict)
    assert "linear" in model_config.REGRESSION_MODELS
    assert isinstance(model_config.CLASSIFICATION_MODELS, dict)
    assert "logistic" in model_config.CLASSIFICATION_MODELS
    assert isinstance(model_config.CLUSTERING_MODELS, dict)
    assert "kmeans" in model_config.CLUSTERING_MODELS
    assert isinstance(model_config.TIME_SERIES_MODELS, dict)
    assert "arima" in model_config.TIME_SERIES_MODELS


# ===================== report_config =====================
def test_report_config_values():
    """تأكد من القيم الأساسية في report_config."""
    assert isinstance(report_config.REPORT_TITLE, str)
    assert isinstance(report_config.REPORT_DATE, str)
    assert isinstance(report_config.AUTHOR, str)
    assert isinstance(report_config.COLOR_SCHEME, dict)
    assert "primary" in report_config.COLOR_SCHEME
    assert isinstance(report_config.LOGO_PATH, Path)
    assert isinstance(report_config.FOOTER_BANNER_PATH, Path)
    assert isinstance(report_config.TEMPLATE_PATH, Path)
    assert isinstance(report_config.OUTPUT_DIR, Path)
    assert isinstance(report_config.REPORT_CONFIG, dict)
    assert "title" in report_config.REPORT_CONFIG


# ===================== dashboard_config =====================
def test_dashboard_config_values():
    """تأكد من القيم الأساسية في dashboard_config."""
    assert isinstance(dashboard_config.DASHBOARD_TITLE, str)
    assert isinstance(dashboard_config.DEFAULT_LANGUAGE, str)
    assert isinstance(dashboard_config.DEFAULT_THEME, str)
    assert isinstance(dashboard_config.REFRESH_INTERVAL, int)
    assert isinstance(dashboard_config.MAX_RECORDS_DISPLAY, int)
    assert isinstance(dashboard_config.KPI_SETTINGS, dict)
    assert isinstance(dashboard_config.LAYOUT_SECTIONS, dict)
    assert "overview" in dashboard_config.LAYOUT_SECTIONS


# ===================== yaml_config_handler + وظائف مساعدة =====================
def test_dictify_and_namespaceify():
    """اختبار دوال التحويل بين dict و namespace."""
    sample = SimpleNamespace(a=1, b=2)
    as_dict = config_loader.dictify(sample)
    assert isinstance(as_dict, dict)
    assert as_dict["a"] == 1

    back_to_ns = config_loader.namespaceify(as_dict)
    assert isinstance(back_to_ns, SimpleNamespace)
    assert back_to_ns.b == 2


def test_yaml_config_handler_load():
    """تأكد من أن CONFIG.yaml يمكنه تحميل بيانات من config.yaml."""
    yaml_handler = config_loader.CONFIG.yaml
    assert yaml_handler is not None
    db_url = yaml_handler.get("database.url")
    assert isinstance(db_url, str) or db_url is None


def test_safe_import_returns_namespace_for_invalid():
    """عند استيراد اسم موديول غير موجود، يجب أن يرجع SimpleNamespace فارغ بدون رفع استثناء."""
    module = config_loader.safe_import("non_existent_module_abc_xyz")
    assert isinstance(module, SimpleNamespace)


# ===================== وظائف إضافية env_config =====================
def test_email_port_and_language():
    """اختبار وظائف get_email_port و determine_language."""
    port = env_config.get_email_port()
    assert isinstance(port, int) and port > 0

    lang = env_config.determine_language("fr", "ar")
    assert lang == "ar", "يجب أن يرجع اللغة الافتراضية عند إدخال لغة غير مدعومة"


def test_setup_defaults_behavior(monkeypatch):
    """
    اختبر أن setup_defaults تضع القيم الافتراضية بشكل صحيح.
    هنا نستخدم CONFIG جديد لتجنب تعديل CONFIG الحقيقي.
    """
    dummy_config = SimpleNamespace(
        env=SimpleNamespace(LANGUAGE=None, DATABASE_URL=""),
        reports=SimpleNamespace()
    )
    monkeypatch.setenv("APP_LANGUAGE", "en")
    monkeypatch.setenv("DATABASE_URL", "sqlite:///test.db")

    config_loader.setup_defaults(dummy_config)

    assert dummy_config.env.LANGUAGE == "en"
    assert dummy_config.env.DATABASE_URL == "sqlite:///test.db"
    assert isinstance(dummy_config.reports.OUTPUT_FORMATS, list)
