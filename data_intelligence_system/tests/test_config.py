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
    assert isinstance(config_loader.CONFIG, SimpleNamespace)
    expected_sections = ['paths', 'models', 'reports', 'dashboard', 'env', 'yaml']
    for section in expected_sections:
        assert hasattr(config_loader.CONFIG, section)


def test_env_namespace_values():
    env = env_config.env_namespace
    assert env.PROJECT_NAME
    assert env.DATABASE_URL.startswith(("sqlite", "postgresql", "mysql"))
    assert isinstance(env.EMAIL_CONFIG, dict)
    assert isinstance(env.RAW_DATA_PATH, Path) and env.RAW_DATA_PATH.exists()
    assert isinstance(env.PROCESSED_DATA_PATH, Path) and env.PROCESSED_DATA_PATH.exists()


# ===================== paths_config =====================
def test_paths_config_directories_exist():
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
        assert dir_path.exists()


def test_paths_config_shortcuts_are_strings():
    assert isinstance(paths_config.RAW_DIR, str)
    assert isinstance(paths_config.PROCESSED_DIR, str)


# ===================== model_config =====================
def test_model_config_basic_values():
    assert isinstance(model_config.RANDOM_STATE, int)
    assert isinstance(model_config.TEST_SIZE, (float, int))
    assert isinstance(model_config.VALIDATION_SPLIT, (float, int))
    assert isinstance(model_config.CROSS_VALIDATION_FOLDS, int)
    assert isinstance(model_config.SCALING_METHOD, str)


def test_model_config_models_are_dicts():
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
    sample = SimpleNamespace(a=1, b=2)
    as_dict = config_loader.dictify(sample)
    assert isinstance(as_dict, dict)
    assert as_dict["a"] == 1

    back_to_ns = config_loader.namespaceify(as_dict)
    assert isinstance(back_to_ns, SimpleNamespace)
    assert back_to_ns.b == 2


def test_yaml_config_handler_load():
    yaml_handler = config_loader.CONFIG.yaml
    assert yaml_handler is not None
    db_url = yaml_handler.get("database.postgres.host")
    assert isinstance(db_url, str) or db_url is None


def test_safe_import_returns_namespace_for_invalid():
    module = config_loader.safe_import("non_existent_module_abc_xyz")
    assert isinstance(module, SimpleNamespace)


# ===================== وظائف إضافية env_config =====================
def test_email_port_and_language():
    port = env_config.get_email_port()
    assert isinstance(port, int) and port > 0

    lang = env_config.determine_language("fr", "ar")
    assert lang == "ar"


def test_setup_defaults_behavior(monkeypatch):
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


# ===================== ✅ اختبارات config.yaml =====================
def test_project_config_from_yaml():
    yaml = config_loader.CONFIG.yaml
    assert yaml.get("project.name") == "General Data Intelligence Framework"
    assert yaml.get("project.version") == "1.0.0"
    assert yaml.get("project.author") == "Marwan Al_Jubouri"
    assert yaml.get("project.language") in ("ar", "en")
    assert yaml.get("project.env_mode") == "development"


def test_paths_config_from_yaml():
    yaml = config_loader.CONFIG.yaml
    raw_path = yaml.get("paths.raw_data")
    processed_path = yaml.get("paths.processed_data")
    assert isinstance(raw_path, str) and raw_path.endswith("/")
    assert isinstance(processed_path, str)


def test_dashboard_config_from_yaml():
    yaml = config_loader.CONFIG.yaml
    assert yaml.get("dashboard.theme") in ("dark", "light")
    assert isinstance(yaml.get("dashboard.max_records"), int)
    assert isinstance(yaml.get("dashboard.refresh_interval"), int)


def test_kpis_config_from_yaml():
    yaml = config_loader.CONFIG.yaml
    kpis = yaml.get("kpis")
    assert isinstance(kpis, list)
    for kpi in kpis:
        assert "name" in kpi and "label" in kpi and "color" in kpi and "icon" in kpi


def test_database_config_from_yaml():
    yaml = config_loader.CONFIG.yaml
    db_type = yaml.get("database.type")
    assert db_type in ("postgresql", "sqlite")
    postgres = yaml.get("database.postgres")
    assert isinstance(postgres, dict)
    sqlite_path = yaml.get("database.sqlite.path")
    assert isinstance(sqlite_path, str)


def test_model_config_from_yaml():
    yaml = config_loader.CONFIG.yaml
    assert isinstance(yaml.get("model.random_state"), int)
    assert isinstance(yaml.get("model.test_size"), float)
    assert isinstance(yaml.get("model.validation_split"), float)
    assert isinstance(yaml.get("model.cross_validation_folds"), int)
    assert isinstance(yaml.get("model.scaling_method"), str)
