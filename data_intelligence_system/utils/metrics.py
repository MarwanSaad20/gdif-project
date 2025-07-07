# utils/metrics.py

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.figure_factory as ff
from sklearn.metrics import (
    mean_absolute_error, mean_squared_error,
    accuracy_score, f1_score, precision_score,
    recall_score, confusion_matrix, classification_report
)

# ✅ التكامل مع لوجر المشروع
from data_intelligence_system.utils.logger import get_logger

logger = get_logger(name="Metrics")


# ========================
# 📏 Regression Metrics
# ========================
def regression_metrics(y_true, y_pred):
    """
    حساب مقاييس الانحدار: MAE, MSE, RMSE
    """
    if y_true is None or y_pred is None:
        raise ValueError("y_true و y_pred يجب ألا يكونا None.")
    if len(y_true) == 0 or len(y_pred) == 0:
        raise ValueError("y_true و y_pred لا يمكن أن تكون فارغة.")
    if len(y_true) != len(y_pred):
        raise ValueError("y_true و y_pred يجب أن يكونا بنفس الطول.")

    y_true, y_pred = np.array(y_true), np.array(y_pred)

    mae = mean_absolute_error(y_true, y_pred)
    mse = mean_squared_error(y_true, y_pred)
    rmse = np.sqrt(mse)

    return {
        "MAE": round(mae, 4),
        "MSE": round(mse, 4),
        "RMSE": round(rmse, 4)
    }


# ========================
# 🧠 Classification Metrics
# ========================
def classification_metrics(y_true, y_pred, average='weighted', zero_division=0):
    """
    حساب دقة التصنيف، F1، Precision، Recall، مصفوفة الالتباس وتقرير التصنيف.
    """
    if y_true is None or y_pred is None:
        raise ValueError("y_true و y_pred يجب ألا يكونا None.")
    if len(y_true) == 0 or len(y_pred) == 0:
        raise ValueError("y_true و y_pred لا يمكن أن تكون فارغة.")
    if len(y_true) != len(y_pred):
        raise ValueError("y_true و y_pred يجب أن يكونا بنفس الطول.")

    y_true, y_pred = np.array(y_true), np.array(y_pred)

    acc = accuracy_score(y_true, y_pred)
    f1 = f1_score(y_true, y_pred, average=average, zero_division=zero_division)
    precision = precision_score(y_true, y_pred, average=average, zero_division=zero_division)
    recall = recall_score(y_true, y_pred, average=average, zero_division=zero_division)
    cm = confusion_matrix(y_true, y_pred)
    report = classification_report(y_true, y_pred, output_dict=True, zero_division=zero_division)

    return {
        "Accuracy": round(acc, 4),
        "F1 Score": round(f1, 4),
        "Precision": round(precision, 4),
        "Recall": round(recall, 4),
        "Confusion Matrix": cm,
        "Classification Report": report
    }


# ========================
# 📊 Static Confusion Matrix
# ========================
def plot_confusion_matrix(cm, labels=None, title="Confusion Matrix", save_path: str = None):
    """
    رسم مصفوفة الالتباس باستخدام Seaborn.
    """
    if labels is None:
        labels = [str(i) for i in range(cm.shape[0])]

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
    else:
        plt.show()


# ========================
# 🌐 Interactive Confusion Matrix
# ========================
def plot_interactive_confusion_matrix(cm, labels=None, title="Interactive Confusion Matrix", save_path: str = None):
    """
    رسم تفاعلي لمصفوفة الالتباس باستخدام Plotly.
    """
    if cm.shape[0] != cm.shape[1]:
        raise ValueError("مصفوفة الالتباس يجب أن تكون مربعة الشكل.")

    x = labels if labels else [str(i) for i in range(cm.shape[0])]
    y = x
    fig = ff.create_annotated_heatmap(z=cm, x=x, y=y, colorscale='Blues')
    fig.update_layout(
        title_text=title,
        xaxis_title='Predicted',
        yaxis_title='Actual'
    )

    if save_path:
        if not save_path.endswith('.html'):
            raise ValueError("save_path يجب أن ينتهي بامتداد .html")
        fig.write_html(save_path)
        return

    fig.show()


# ========================
# 🧪 Example on Direct Execution
# ========================
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
