# =============================
# 05 - Outlier Handling Script
# =============================

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

# ✅ استيراد دوال الكشف من جذر المشروع
from data_intelligence_system.analysis.outlier_detection import detect_outliers_iqr

# ------------------------
# ضبط مسار جذر المشروع بطريقة ديناميكية
try:
    PROJECT_ROOT = Path(__file__).resolve().parents[1]
except NameError:
    PROJECT_ROOT = Path.cwd().parents[0]

# ------------------------
# تحميل البيانات
DATA_PATH = PROJECT_ROOT / "data" / "processed" / "clean_data.csv"
if not DATA_PATH.exists():
    raise FileNotFoundError(f"❌ الملف غير موجود في: {DATA_PATH}")

df = pd.read_csv(DATA_PATH)
print(f"✅ تم تحميل البيانات من: {DATA_PATH}")
print(f"شكل البيانات: {df.shape}")

# ------------------------
# مثال boxplot لأحد الأعمدة الرقمية
num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
if not num_cols:
    raise ValueError("🚫 لا توجد أعمدة رقمية في البيانات")

col_to_check = num_cols[0]
plt.figure(figsize=(8, 5))
sns.boxplot(x=df[col_to_check])
plt.title(f"Boxplot لعمود {col_to_check}")
plt.show()

# ------------------------
# كشف القيم الشاذة باستخدام الدالة من outlier_detection
outliers_mask = detect_outliers_iqr(df)
outliers = df[outliers_mask]
print(f"عدد الصفوف التي تحتوي على قيم شاذة: {len(outliers)}")

# ------------------------
# إزالة الصفوف الشاذة
df_no_outliers = df[~outliers_mask]
print(f"شكل البيانات بعد إزالة القيم الشاذة: {df_no_outliers.shape}")

# ------------------------
# حفظ نسخة جديدة بعد التنظيف (اختياري)
OUTPUT_PATH = PROJECT_ROOT / "data" / "processed" / "clean_data_no_outliers.csv"
df_no_outliers.to_csv(OUTPUT_PATH, index=False)
print(f"[✓] تم حفظ البيانات بعد إزالة القيم الشاذة في: {OUTPUT_PATH}")
