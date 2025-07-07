# config/model_config.py

# 🔢 الإعدادات العامة للنماذج
RANDOM_STATE = 42
TEST_SIZE = 0.2
VALIDATION_SPLIT = 0.1
CROSS_VALIDATION_FOLDS = 5
SCALING_METHOD = "standard"  # خيارات: "minmax", "standard", "robust"

# ⚙️ إعدادات النماذج الانحدارية (Regression)
REGRESSION_MODELS = {
    "linear": {
        "fit_intercept": True,
        # ملاحظة: خيار normalize قديم في scikit-learn >= 1.0، يُفضل استخدام StandardScaler خارجياً
        "normalize": False
    },
    "lasso": {
        "alpha": 0.1,
        "max_iter": 1000
    },
    "ridge": {
        "alpha": 1.0,
        "solver": "auto"
    }
}

# ⚙️ إعدادات النماذج التصنيفية (Classification)
CLASSIFICATION_MODELS = {
    "logistic": {
        "penalty": "l2",
        "C": 1.0,
        "solver": "liblinear"  # قد تحتاج تعديل إلى 'saga' أو 'lbfgs' في التصنيفات المتعددة أو الكبيرة
    },
    "random_forest": {
        "n_estimators": 100,
        "max_depth": 10,
        "min_samples_split": 2,
        "random_state": RANDOM_STATE
    },
    "xgboost": {
        "learning_rate": 0.1,
        "max_depth": 6,
        "n_estimators": 100,
        "subsample": 0.8,
        "colsample_bytree": 0.8,
        "random_state": RANDOM_STATE  # توحيد اسم المتغير مع scikit-learn
    }
}

# ⚙️ إعدادات نماذج التجميع (Clustering)
CLUSTERING_MODELS = {
    "kmeans": {
        "n_clusters": 5,
        "init": "k-means++",
        "n_init": 10,
        "max_iter": 300,
        "random_state": RANDOM_STATE
    },
    "dbscan": {
        "eps": 0.5,
        "min_samples": 5,
        "metric": "euclidean"
    }
}

# ⚙️ إعدادات التنبؤ الزمني (Time Series)
TIME_SERIES_MODELS = {
    "arima": {
        "order": (1, 1, 1)
    },
    "prophet": {
        "seasonality_mode": "additive",
        "yearly_seasonality": "auto",
        "weekly_seasonality": True,
        "daily_seasonality": False
    }
}
