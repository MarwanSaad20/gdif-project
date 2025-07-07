import importlib
from typing import Any

# خريطة النماذج المتوفرة حسب النوع
MODEL_REGISTRY = {
    "regression": {
        "linear": "ml_models.regression.linear_regression.LinearRegressionModel",
        "lasso": "ml_models.regression.lasso_regression.LassoRegressionModel",
        "ridge": "ml_models.regression.ridge_regression.RidgeRegressionModel"
    },
    "classification": {
        "logistic": "ml_models.classification.logistic_regression.LogisticRegressionModel",
        "random_forest": "ml_models.classification.random_forest.RandomForestClassifierModel",
        "xgboost": "ml_models.classification.xgboost_classifier.XGBoostClassifierModel"
    },
    "clustering": {
        "kmeans": "ml_models.clustering.kmeans.KMeansClusteringModel",
        "dbscan": "ml_models.clustering.dbscan.DBSCANClusteringModel"
    },
    "forecasting": {
        "arima": "ml_models.forecasting.arima_model.ARIMAForecastingModel",
        "prophet": "ml_models.forecasting.prophet_model.ProphetForecastingModel"
    }
}

def list_models() -> dict:
    """إرجاع خريطة النماذج المتاحة."""
    return MODEL_REGISTRY

def get_model(model_type: str, model_name: str, **kwargs) -> Any:
    """
    تحميل النموذج المطلوب ديناميكيًا من المسار المناسب.

    Args:
        model_type (str): نوع النموذج ('regression', 'classification', 'clustering', 'forecasting')
        model_name (str): اسم النموذج داخل النوع ('linear', 'arima', إلخ)
        kwargs: معلمات تُمرر إلى المُنشئ (constructor)

    Returns:
        Instance of model class.

    Raises:
        ValueError: إذا كان model_type أو model_name غير موجود.
        RuntimeError: إذا حدث خطأ أثناء استيراد أو إنشاء النموذج.
    """
    if not isinstance(model_type, str) or not isinstance(model_name, str):
        raise TypeError("model_type و model_name يجب أن يكونا نصوصًا (str).")

    try:
        type_dict = MODEL_REGISTRY[model_type]
    except KeyError:
        available_types = list(MODEL_REGISTRY.keys())
        raise ValueError(f"نوع النموذج '{model_type}' غير معروف. الأنواع المتاحة: {available_types}")

    try:
        module_path = type_dict[model_name]
    except KeyError:
        available_models = list(type_dict.keys())
        raise ValueError(f"اسم النموذج '{model_name}' غير معروف لنوع '{model_type}'. النماذج المتاحة: {available_models}")

    try:
        module_name, class_name = module_path.rsplit('.', 1)
        module = importlib.import_module(module_name)
        model_class = getattr(module, class_name)
        return model_class(**kwargs)
    except Exception as e:
        raise RuntimeError(f"فشل تحميل النموذج '{model_name}' من النوع '{model_type}': {e}")
