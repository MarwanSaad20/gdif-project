from pathlib import Path
from data_intelligence_system.utils.config_handler import ConfigHandler
from data_intelligence_system.utils.logger import get_logger

logger = get_logger("model_config")

CONFIG_PATH = Path(__file__).resolve().parent / "config.yaml"
config = ConfigHandler(str(CONFIG_PATH)) if CONFIG_PATH.exists() else None


def get_config_value(key: str, default):
    """Helper to get config value or default."""
    return config.get(key, default) if config else default


# 🔢 الإعدادات العامة للنماذج
RANDOM_STATE = get_config_value("model.random_state", 42)
TEST_SIZE = get_config_value("model.test_size", 0.2)
VALIDATION_SPLIT = get_config_value("model.validation_split", 0.1)
CROSS_VALIDATION_FOLDS = get_config_value("model.cross_validation_folds", 5)
SCALING_METHOD = get_config_value("model.scaling_method", "standard")

# ⚙️ إعدادات النماذج الانحدارية (Regression)
REGRESSION_MODELS = {
    "linear": {
        "fit_intercept": True,
        "normalize": False,
    },
    "lasso": {
        "alpha": 0.1,
        "max_iter": 1000,
    },
    "ridge": {
        "alpha": 1.0,
        "solver": "auto",
    },
}

# ⚙️ إعدادات النماذج التصنيفية (Classification)
CLASSIFICATION_MODELS = {
    "logistic": {
        "penalty": "l2",
        "C": 1.0,
        "solver": "liblinear",
    },
    "random_forest": {
        "n_estimators": 100,
        "max_depth": 10,
        "min_samples_split": 2,
        "random_state": RANDOM_STATE,
    },
    "xgboost": {
        "learning_rate": 0.1,
        "max_depth": 6,
        "n_estimators": 100,
        "subsample": 0.8,
        "colsample_bytree": 0.8,
        "random_state": RANDOM_STATE,
    },
}

# ⚙️ إعدادات نماذج التجميع (Clustering)
CLUSTERING_MODELS = {
    "kmeans": {
        "n_clusters": 5,
        "init": "k-means++",
        "n_init": 10,
        "max_iter": 300,
        "random_state": RANDOM_STATE,
    },
    "dbscan": {
        "eps": 0.5,
        "min_samples": 5,
        "metric": "euclidean",
    },
}

# ⚙️ إعدادات التنبؤ الزمني (Time Series)
TIME_SERIES_MODELS = {
    "arima": {
        "order": (1, 1, 1),
    },
    "prophet": {
        "seasonality_mode": "additive",
        "yearly_seasonality": "auto",
        "weekly_seasonality": True,
        "daily_seasonality": False,
    },
}

if __name__ == "__main__":
    print(f"RANDOM_STATE: {RANDOM_STATE}")
    print(f"SCALING_METHOD: {SCALING_METHOD}")
    print(f"TEST_SIZE: {TEST_SIZE}")
    print(f"VALIDATION_SPLIT: {VALIDATION_SPLIT}")
    print(f"CROSS_VALIDATION_FOLDS: {CROSS_VALIDATION_FOLDS}")
