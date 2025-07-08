import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.figure_factory as ff
from sklearn.metrics import (
    mean_absolute_error, mean_squared_error,
    accuracy_score, f1_score, precision_score,
    recall_score, confusion_matrix, classification_report
)

from data_intelligence_system.utils.logger import get_logger

logger = get_logger(name="Metrics")


def regression_metrics(y_true: np.ndarray | list, y_pred: np.ndarray | list) -> dict:
    """
    حساب مقاييس الانحدار: MAE, MSE, RMSE

    Args:
        y_true (array-like): القيم الحقيقية (رقمية).
        y_pred (array-like): القيم المتوقعة (رقمية).

    Returns:
        dict: يحتوي على MAE, MSE, RMSE مع تقريب 4 أرقام عشرية.

    Raises:
        ValueError: إذا كانت المدخلات None، فارغة، أو ذات أطوال مختلفة.
    """
    if y_true is None or y_pred is None:
        logger.error("y_true أو y_pred لا يمكن أن تكون None.")
        raise ValueError("y_true و y_pred يجب ألا يكونا None.")
    if len(y_true) == 0 or len(y_pred) == 0:
        logger.error("y_true أو y_pred لا يمكن أن تكون فارغة.")
        raise ValueError("y_true و y_pred لا يمكن أن تكون فارغة.")
    if len(y_true) != len(y_pred):
        logger.error("طول y_true لا يساوي طول y_pred.")
        raise ValueError("y_true و y_pred يجب أن يكونا بنفس الطول.")

    y_true_arr = np.array(y_true)
    y_pred_arr = np.array(y_pred)

    mae = mean_absolute_error(y_true_arr, y_pred_arr)
    mse = mean_squared_error(y_true_arr, y_pred_arr)
    rmse = np.sqrt(mse)

    return {
        "MAE": round(mae, 4),
        "MSE": round(mse, 4),
        "RMSE": round(rmse, 4)
    }


def classification_metrics(
    y_true: np.ndarray | list,
    y_pred: np.ndarray | list,
    average: str = 'weighted',
    zero_division: int = 0
) -> dict:
    """
    حساب مقاييس التصنيف الرئيسية.

    Args:
        y_true (array-like): القيم الحقيقية.
        y_pred (array-like): القيم المتوقعة.
        average (str): طريقة حساب المتوسط للـ Precision, Recall, F1.
        zero_division (int): القيمة التي تستخدم في حالة القسمة على صفر.

    Returns:
        dict: يحتوي على مقاييس الأداء مع تقريب 4 أرقام عشرية،
              بالإضافة إلى مصفوفة الالتباس وتقرير التصنيف (كقاموس).
    
    Raises:
        ValueError: إذا كانت المدخلات None، فارغة، أو ذات أطوال مختلفة.
    """
    if y_true is None or y_pred is None:
        logger.error("y_true أو y_pred لا يمكن أن تكون None.")
        raise ValueError("y_true و y_pred يجب ألا يكونا None.")
    if len(y_true) == 0 or len(y_pred) == 0:
        logger.error("y_true أو y_pred لا يمكن أن تكون فارغة.")
        raise ValueError("y_true و y_pred لا يمكن أن تكون فارغة.")
    if len(y_true) != len(y_pred):
        logger.error("طول y_true لا يساوي طول y_pred.")
        raise ValueError("y_true و y_pred يجب أن يكونا بنفس الطول.")

    y_true_arr = np.array(y_true)
    y_pred_arr = np.array(y_pred)

    acc = accuracy_score(y_true_arr, y_pred_arr)
    f1 = f1_score(y_true_arr, y_pred_arr, average=average, zero_division=zero_division)
    precision = precision_score(y_true_arr, y_pred_arr, average=average, zero_division=zero_division)
    recall = recall_score(y_true_arr, y_pred_arr, average=average, zero_division=zero_division)
    cm = confusion_matrix(y_true_arr, y_pred_arr)
    report = classification_report(y_true_arr, y_pred_arr, output_dict=True, zero_division=zero_division)

    return {
        "Accuracy": round(acc, 4),
        "F1 Score": round(f1, 4),
        "Precision": round(precision, 4),
        "Recall": round(recall, 4),
        "Confusion Matrix": cm,
        "Classification Report": report
    }


def plot_confusion_matrix(cm: np.ndarray, labels: list | None = None,
                          title: str = "Confusion Matrix",
                          save_path: str | None = None) -> None:
    """
    رسم مصفوفة الالتباس باستخدام Seaborn.

    Args:
        cm (np.ndarray): مصفوفة الالتباس.
        labels (list, optional): تسميات الفئات.
        title (str, optional): عنوان الرسم.
        save_path (str, optional): مسار لحفظ الصورة (png/pdf).

    Raises:
        ValueError: إذا كان cm ليست مصفوفة مربعة.
        Exception: أخطاء عامة في الرسم أو الحفظ.
    """
    if cm.shape[0] != cm.shape[1]:
        logger.error("مصفوفة الالتباس يجب أن تكون مربعة.")
        raise ValueError("مصفوفة الالتباس يجب أن تكون مربعة.")

    if labels is None:
        labels = [str(i) for i in range(cm.shape[0])]

    try:
        plt.figure(figsize=(6, 4))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                    xticklabels=labels, yticklabels=labels)
        plt.title(title)
        plt.xlabel('Predicted')
        plt.ylabel('True')
        plt.tight_layout()

        if save_path:
            plt.savefig(save_path)
            plt.close()
            logger.info(f"Confusion matrix saved to {save_path}")
        else:
            plt.show()
    except Exception as e:
        logger.error(f"Failed to plot confusion matrix: {e}")
        raise


def plot_interactive_confusion_matrix(cm: np.ndarray, labels: list | None = None,
                                      title: str = "Interactive Confusion Matrix",
                                      save_path: str | None = None) -> None:
    """
    رسم تفاعلي لمصفوفة الالتباس باستخدام Plotly.

    Args:
        cm (np.ndarray): مصفوفة الالتباس.
        labels (list, optional): تسميات الفئات.
        title (str, optional): عنوان الرسم.
        save_path (str, optional): مسار حفظ ملف HTML.

    Raises:
        ValueError: إذا كان cm ليست مصفوفة مربعة.
        ValueError: إذا لم يكن امتداد save_path .html.
        Exception: أخطاء عامة في الرسم أو الحفظ.
    """
    if cm.shape[0] != cm.shape[1]:
        logger.error("مصفوفة الالتباس يجب أن تكون مربعة.")
        raise ValueError("مصفوفة الالتباس يجب أن تكون مربعة.")

    x = labels if labels else [str(i) for i in range(cm.shape[0])]
    y = x

    try:
        fig = ff.create_annotated_heatmap(z=cm, x=x, y=y, colorscale='Blues')
        fig.update_layout(
            title_text=title,
            xaxis_title='Predicted',
            yaxis_title='Actual'
        )

        if save_path:
            if not save_path.endswith('.html'):
                logger.error("save_path يجب أن ينتهي بامتداد .html")
                raise ValueError("save_path يجب أن ينتهي بامتداد .html")
            fig.write_html(save_path)
            logger.info(f"Interactive confusion matrix saved to {save_path}")
            return

        fig.show()
    except Exception as e:
        logger.error(f"Failed to plot interactive confusion matrix: {e}")
        raise


if __name__ == "__main__":
    y_true = [0, 1, 2, 2, 0]
    y_pred = [0, 0, 2, 2, 0]

    print("📊 Regression Metrics:")
    print(regression_metrics(y_true, y_pred))

    print("\n🎯 Classification Metrics:")
    cls_metrics = classification_metrics(y_true, y_pred)
    for k in ["Accuracy", "Precision", "Recall", "F1 Score"]:
        print(f"{k}: {cls_metrics[k]}")

    print("\n📄 Classification Report:")
    report = cls_metrics["Classification Report"]
    for label, metrics in report.items():
        if isinstance(metrics, dict):
            print(f"{label}: ", {m: round(v, 2) for m, v in metrics.items()})
        else:
            print(f"{label}: {round(metrics, 2)}")

    print("\n📉 Confusion Matrix:")
    print(cls_metrics["Confusion Matrix"])

    plot_confusion_matrix(cls_metrics["Confusion Matrix"])
