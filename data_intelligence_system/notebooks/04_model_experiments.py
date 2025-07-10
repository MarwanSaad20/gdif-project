# ===============================
# 🤖 04 - Model Experiments
# ===============================

import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score, classification_report, confusion_matrix,
    mean_absolute_error, r2_score
)
from sklearn.preprocessing import LabelEncoder
import seaborn as sns
import matplotlib.pyplot as plt
import warnings

# استيراد نماذج الانحدار والتصنيف المحسّنة
from data_intelligence_system.ml_models.regression.lasso_regression import LassoRegressionModel
from data_intelligence_system.ml_models.regression.ridge_regression import RidgeRegressionModel
from data_intelligence_system.ml_models.classification.logistic_regression import LogisticRegressionModel
from data_intelligence_system.ml_models.classification.random_forest import RandomForestModel
from data_intelligence_system.ml_models.classification.xgboost_classifier import XGBoostClassifierModel
from data_intelligence_system.ml_models.forecasting.arima_model import ARIMAForecastingModel
from data_intelligence_system.forecasting.prophet_model import ProphetForecastingModel

warnings.filterwarnings("ignore")
sns.set_theme(style="whitegrid")

# =====================
# 📥 تحميل البيانات
# =====================

def load_clean_data():
    try:
        project_root = Path(__file__).resolve().parents[1]
    except NameError:
        project_root = Path.cwd().parents[0]

    data_path = project_root / "data" / "processed" / "clean_data.csv"
    if not data_path.exists():
        raise FileNotFoundError(f"❌ الملف غير موجود: {data_path}")
    df = pd.read_csv(data_path)
    print(f"✅ تم تحميل البيانات: {df.shape}")
    return df

# ==============================
# 🎯 تحديد عمود الهدف تلقائيًا أو يدويًا
# ==============================

def detect_target_column(df):
    for col in df.columns:
        if col.lower() in ['target', 'label', 'y']:
            print(f"🎯 تم اكتشاف العمود الهدف تلقائيًا: {col}")
            return col

    print("🚫 لم يتم العثور على عمود هدف باسم 'target' أو 'label' أو 'y'")
    print("🧠 الأعمدة المتاحة:", list(df.columns))

    for col in df.columns:
        if df[col].nunique() <= 10 and df[col].dtype in ['int64', 'object']:
            print(f"📌 سيتم استخدام العمود '{col}' كهدف محتمل (n_unique <= 10)")
            return col

    target_col = input("📝 أدخل اسم العمود الهدف يدويًا: ").strip()
    if target_col not in df.columns:
        raise ValueError(f"🚨 العمود '{target_col}' غير موجود في البيانات.")
    return target_col

# =============================
# ✂️ تقسيم البيانات للتدريب والاختبار
# =============================

def split_data(df, target_col):
    X = df.drop(columns=[target_col]).select_dtypes(include=["float64", "int64"]).fillna(0)
    y = df[target_col]

    if X.shape[1] == 0:
        raise ValueError("🚫 لا توجد سمات رقمية قابلة للنمذجة.")

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    return X_train, X_test, y_train, y_test, y

# =======================================
# 🧪 تدريب النموذج وتقييم الأداء تلقائيًا
# =======================================

def run_model_experiment(X_train, X_test, y_train, y_test, y_full):
    if y_full.nunique() <= 10:
        print("📌 نوع المسألة: تصنيف (Classification)")

        # تدريب وتقييم RandomForest كما هو
        rf_model = RandomForestModel()
        rf_model.fit(X_train, y_train)
        y_pred_rf = rf_model.predict(X_test)

        print(f"✅ RandomForest دقة (Accuracy): {accuracy_score(y_test, y_pred_rf):.4f}")
        print("🔎 تقرير التصنيف RandomForest:")
        print(classification_report(y_test, y_pred_rf))

        cm_rf = confusion_matrix(y_test, y_pred_rf)
        plt.figure(figsize=(6, 4))
        sns.heatmap(cm_rf, annot=True, fmt='d', cmap='Blues')
        plt.title('Confusion Matrix - RandomForest')
        plt.xlabel('Predicted')
        plt.ylabel('Actual')
        plt.tight_layout()
        plt.savefig("confusion_matrix_random_forest.png")
        plt.show()

        # ترميز الهدف لـ XGBoost
        le = LabelEncoder()
        y_train_enc = le.fit_transform(y_train)
        y_test_enc = le.transform(y_test)

        xgb_model = XGBoostClassifierModel()
        xgb_model.fit(X_train, y_train_enc)
        y_pred_xgb_enc = xgb_model.predict(X_test)
        y_pred_xgb = le.inverse_transform(y_pred_xgb_enc)

        print(f"✅ XGBoost دقة (Accuracy): {accuracy_score(y_test, y_pred_xgb):.4f}")
        print("🔎 تقرير التصنيف XGBoost:")
        print(classification_report(y_test, y_pred_xgb))

        cm_xgb = confusion_matrix(y_test, y_pred_xgb)
        plt.figure(figsize=(6, 4))
        sns.heatmap(cm_xgb, annot=True, fmt='d', cmap='Greens')
        plt.title('Confusion Matrix - XGBoost')
        plt.xlabel('Predicted')
        plt.ylabel('Actual')
        plt.tight_layout()
        plt.savefig("confusion_matrix_xgboost.png")
        plt.show()

    else:
        print("📌 نوع المسألة: انحدار (Regression)")

        # تجربة LassoRegressionModel
        lasso_model = LassoRegressionModel()
        lasso_model.fit(X_train, y_train)
        y_pred_lasso = lasso_model.predict(X_test)

        mae_lasso = mean_absolute_error(y_test, y_pred_lasso)
        r2_lasso = r2_score(y_test, y_pred_lasso)
        print(f"✅ Lasso MAE: {mae_lasso:.4f}")
        print(f"✅ Lasso R²: {r2_lasso:.4f}")

        plt.figure(figsize=(6, 4))
        sns.scatterplot(x=y_test, y=y_pred_lasso, color='darkorange')
        plt.xlabel('Actual')
        plt.ylabel('Predicted')
        plt.title('Actual vs Predicted (Lasso)')
        plt.tight_layout()
        plt.savefig("lasso_regression_results.png")
        plt.show()

        # تجربة RidgeRegressionModel
        ridge_model = RidgeRegressionModel()
        ridge_model.fit(X_train, y_train)
        y_pred_ridge = ridge_model.predict(X_test)

        mae_ridge = mean_absolute_error(y_test, y_pred_ridge)
        r2_ridge = r2_score(y_test, y_pred_ridge)
        print(f"✅ Ridge MAE: {mae_ridge:.4f}")
        print(f"✅ Ridge R²: {r2_ridge:.4f}")

        plt.figure(figsize=(6, 4))
        sns.scatterplot(x=y_test, y=y_pred_ridge, color='seagreen')
        plt.xlabel('Actual')
        plt.ylabel('Predicted')
        plt.title('Actual vs Predicted (Ridge)')
        plt.tight_layout()
        plt.savefig("ridge_regression_results.png")
        plt.show()

# ========================
# 🚀 نقطة تشغيل السكربت
# ========================

if __name__ == "__main__":
    df = load_clean_data()
    target_col = detect_target_column(df)
    X_train, X_test, y_train, y_test, y_full = split_data(df, target_col)
    run_model_experiment(X_train, X_test, y_train, y_test, y_full)
