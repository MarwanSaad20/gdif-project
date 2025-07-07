import numpy as np
import inspect
import pandas as pd
from sklearn.metrics import (
    mean_squared_error,
    mean_absolute_error,
    r2_score,
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix as sk_confusion_matrix,
    silhouette_score,
    adjusted_rand_score,
)

from data_intelligence_system.ml_models.utils.preprocessing import DataPreprocessor
from data_intelligence_system.utils.preprocessing import fill_missing_values  # ✅ محدث


class RegressionMetrics:
    @staticmethod
    def mse(y_true: np.ndarray, y_pred: np.ndarray) -> float:
        return mean_squared_error(y_true, y_pred)

    @staticmethod
    def rmse(y_true: np.ndarray, y_pred: np.ndarray) -> float:
        if 'squared' in inspect.signature(mean_squared_error).parameters:
            return mean_squared_error(y_true, y_pred, squared=False)
        else:
            return np.sqrt(mean_squared_error(y_true, y_pred))

    @staticmethod
    def mae(y_true: np.ndarray, y_pred: np.ndarray) -> float:
        return mean_absolute_error(y_true, y_pred)

    @staticmethod
    def r2(y_true: np.ndarray, y_pred: np.ndarray) -> float:
        return r2_score(y_true, y_pred)

    @staticmethod
    def all_metrics(y_true: np.ndarray, y_pred: np.ndarray, inverse_transform=False,
                    preprocessor: DataPreprocessor = None) -> dict:
        if isinstance(y_true, np.ndarray):
            y_true = pd.DataFrame(y_true)
            y_true = fill_missing_values(y_true).values.flatten()
        else:
            y_true = fill_missing_values(y_true)

        if isinstance(y_pred, np.ndarray):
            y_pred = pd.DataFrame(y_pred)
            y_pred = fill_missing_values(y_pred).values.flatten()
        else:
            y_pred = fill_missing_values(y_pred)

        if inverse_transform and preprocessor:
            y_true = preprocessor.inverse_transform_scaler(y_true.reshape(-1, 1)).flatten()
            y_pred = preprocessor.inverse_transform_scaler(y_pred.reshape(-1, 1)).flatten()

        return {
            "MSE": RegressionMetrics.mse(y_true, y_pred),
            "RMSE": RegressionMetrics.rmse(y_true, y_pred),
            "MAE": RegressionMetrics.mae(y_true, y_pred),
            "R2": RegressionMetrics.r2(y_true, y_pred),
        }


class ClassificationMetrics:
    @staticmethod
    def accuracy(y_true: np.ndarray, y_pred: np.ndarray) -> float:
        return accuracy_score(y_true, y_pred)

    @staticmethod
    def precision(y_true: np.ndarray, y_pred: np.ndarray, average="binary") -> float:
        return precision_score(y_true, y_pred, average=average, zero_division=0)

    @staticmethod
    def recall(y_true: np.ndarray, y_pred: np.ndarray, average="binary") -> float:
        return recall_score(y_true, y_pred, average=average, zero_division=0)

    @staticmethod
    def f1(y_true: np.ndarray, y_pred: np.ndarray, average="binary") -> float:
        return f1_score(y_true, y_pred, average=average, zero_division=0)

    @staticmethod
    def confusion(y_true: np.ndarray, y_pred: np.ndarray) -> np.ndarray:
        return sk_confusion_matrix(y_true, y_pred)

    @staticmethod
    def all_metrics(y_true: np.ndarray, y_pred: np.ndarray, average="binary") -> dict:
        if isinstance(y_true, np.ndarray):
            y_true = pd.DataFrame(y_true)
            y_true = fill_missing_values(y_true).values.flatten()
        else:
            y_true = fill_missing_values(y_true)

        if isinstance(y_pred, np.ndarray):
            y_pred = pd.DataFrame(y_pred)
            y_pred = fill_missing_values(y_pred).values.flatten()
        else:
            y_pred = fill_missing_values(y_pred)

        return {
            "Accuracy": ClassificationMetrics.accuracy(y_true, y_pred),
            "Precision": ClassificationMetrics.precision(y_true, y_pred, average),
            "Recall": ClassificationMetrics.recall(y_true, y_pred, average),
            "F1 Score": ClassificationMetrics.f1(y_true, y_pred, average),
            "Confusion Matrix": ClassificationMetrics.confusion(y_true, y_pred),
        }


class ClusteringMetrics:
    @staticmethod
    def silhouette(X: np.ndarray, labels: np.ndarray) -> float:
        try:
            if isinstance(X, np.ndarray):
                X = pd.DataFrame(X)
                X = fill_missing_values(X).values
            else:
                X = fill_missing_values(X)

            if isinstance(labels, np.ndarray):
                labels = pd.DataFrame(labels)
                labels = fill_missing_values(labels).values.flatten()
            else:
                labels = fill_missing_values(labels)

            score = silhouette_score(X, labels)
        except ValueError:
            score = float('nan')
        return score

    @staticmethod
    def adjusted_rand(y_true: np.ndarray, y_pred: np.ndarray) -> float:
        if isinstance(y_true, np.ndarray):
            y_true = pd.DataFrame(y_true)
            y_true = fill_missing_values(y_true).values.flatten()
        else:
            y_true = fill_missing_values(y_true)

        if isinstance(y_pred, np.ndarray):
            y_pred = pd.DataFrame(y_pred)
            y_pred = fill_missing_values(y_pred).values.flatten()
        else:
            y_pred = fill_missing_values(y_pred)

        return adjusted_rand_score(y_true, y_pred)

    @staticmethod
    def all_metrics(X: np.ndarray, y_true: np.ndarray, y_pred: np.ndarray) -> dict:
        return {
            "Silhouette Score": ClusteringMetrics.silhouette(X, y_pred),
            "Adjusted Rand Index": ClusteringMetrics.adjusted_rand(y_true, y_pred),
        }


if __name__ == "__main__":
    y_true_reg = np.array([3.0, -0.5, 2.0, 7.0])
    y_pred_reg = np.array([2.5, 0.0, 2.1, 7.8])
    print("Regression Metrics:", RegressionMetrics.all_metrics(y_true_reg, y_pred_reg))

    y_true_cls = np.array([0, 1, 1, 0])
    y_pred_cls = np.array([0, 1, 0, 0])
    print("Classification Metrics:", ClassificationMetrics.all_metrics(y_true_cls, y_pred_cls))
