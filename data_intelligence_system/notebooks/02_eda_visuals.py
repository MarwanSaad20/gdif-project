# ============================
# 📊 02 - EDA Visuals Script
# ============================

import sys
import os
import pandas as pd
import warnings
import plotly.io as pio

# ⚙️ إعداد بيئة العرض لرسوم Plotly
try:
    pio.renderers.default = "notebook"
except Exception:
    pio.renderers.default = "browser"

warnings.filterwarnings("ignore")

# 🛠️ إضافة جذر المشروع إلى sys.path
project_root = os.path.abspath(os.path.join(os.getcwd(), ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from utils.visualization import (
    plot_box,
    plot_distribution,
    interactive_scatter_matrix,
    plot_correlation_heatmap
)

# =====================
# 📂 تحميل البيانات
# =====================

def load_clean_data():
    data_path = os.path.join(project_root, "data", "processed", "clean_data.csv")
    df = pd.read_csv(data_path)
    print(f"✅ تم تحميل البيانات: {df.shape}")
    return df


# ==========================
# 🎯 Boxplot لأعمدة رقمية
# ==========================

def generate_boxplot(df):
    numeric_cols = df.select_dtypes(include=["int64", "float64"]).columns.tolist()
    if numeric_cols:
        fig, ax = plot_box(df, column=numeric_cols[0], title="Boxplot لأول عمود رقمي")
    else:
        print("🚫 لا توجد أعمدة رقمية متاحة للرسم.")
    return numeric_cols


# ========================================
# 🎯 Histogram + KDE لأول 5 أعمدة رقمية
# ========================================

def generate_distributions(df, numeric_cols):
    for col in numeric_cols[:min(5, len(numeric_cols))]:
        fig, ax = plot_distribution(df, column=col, kde=True, bins=30, title=f"Distribution – {col}")


# ============================
# 🎯 Scatter Matrix (Plotly)
# ============================

def generate_scatter_matrix(df, numeric_cols):
    categorical_cols = df.select_dtypes(include="object").columns.tolist()
    color_col = categorical_cols[0] if categorical_cols else None

    dims = numeric_cols[:min(4, len(numeric_cols))]
    if len(dims) >= 2:
        try:
            fig = interactive_scatter_matrix(
                df,
                dimensions=dims,
                color=color_col,
                title="Scatter Matrix – متغيرات رقمية مختارة"
            )
        except ValueError as e:
            print(f"⚠️ خطأ في رسم Scatter Matrix: {e}")
    else:
        print("🚫 عدد الأعمدة الرقمية غير كافٍ لرسم Scatter Matrix.")


# ===============================
# 🎯 Heatmap للارتباط بين الأرقام
# ===============================

def generate_correlation_heatmap(df, numeric_cols):
    if len(numeric_cols) >= 2:
        fig, ax = plot_correlation_heatmap(df[numeric_cols], title="Heatmap – الارتباط بين المتغيرات الرقمية")
    else:
        print("🚫 لا يوجد عدد كافٍ من المتغيرات الرقمية لإنشاء Heatmap.")


# ======================
# 🚀 نقطة تشغيل السكربت
# ======================

if __name__ == "__main__":
    df = load_clean_data()
    numeric_cols = generate_boxplot(df)
    generate_distributions(df, numeric_cols)
    generate_scatter_matrix(df, numeric_cols)
    generate_correlation_heatmap(df, numeric_cols)
