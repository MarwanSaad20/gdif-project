# =============================
# 05 - Outlier Handling Script
# =============================

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import sys

# ------------------------
# ضبط مسار جذر المشروع بطريقة ديناميكية
try:
    PROJECT_ROOT = Path(__file__).resolve().parents[1]  # مجلد data_intelligence_system
except NameError:
    PROJECT_ROOT = Path.cwd().parents[0]  # إذا كان التنفيذ في بيئة لا تحتوي على __file__ (مثل Jupyter)

# ------------------------
# تحميل البيانات من المسار الصحيح داخل هيكل المشروع
DATA_PATH = PROJECT_ROOT / "data" / "processed" / "clean_data.csv"
if not DATA_PATH.exists():
    raise FileNotFoundError(f"❌ الملف غير موجود في: {DATA_PATH}")

df = pd.read_csv(DATA_PATH)
print(f"✅ تم تحميل البيانات من: {DATA_PATH}")
print(f"شكل البيانات: {df.shape}")

# ------------------------
# مثال على التعامل مع القيم الشاذة - رسم boxplot لأحد الأعمدة الرقمية
num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
if not num_cols:
    raise ValueError("🚫 لا توجد أعمدة رقمية في البيانات")

col_to_check = num_cols[0]
plt.figure(figsize=(8, 5))
sns.boxplot(x=df[col_to_check])
plt.title(f"Boxplot لعمود {col_to_check}")
plt.show()

# ------------------------
# كشف القيم الشاذة باستخدام طريقة IQR
Q1 = df[col_to_check].quantile(0.25)
Q3 = df[col_to_check].quantile(0.75)
IQR = Q3 - Q1
lower_bound = Q1 - 1.5 * IQR
upper_bound = Q3 + 1.5 * IQR

outliers = df[(df[col_to_check] < lower_bound) | (df[col_to_check] > upper_bound)]
print(f"عدد القيم الشاذة في '{col_to_check}': {len(outliers)}")

# ------------------------
# إزالة القيم الشاذة
df_no_outliers = df[(df[col_to_check] >= lower_bound) & (df[col_to_check] <= upper_bound)]
print(f"شكل البيانات بعد إزالة القيم الشاذة: {df_no_outliers.shape}")

# ------------------------
# حفظ نسخة جديدة من البيانات بعد التنظيف (اختياري)
OUTPUT_PATH = PROJECT_ROOT / "data" / "processed" / "clean_data_no_outliers.csv"
df_no_outliers.to_csv(OUTPUT_PATH, index=False)
print(f"[✓] تم حفظ البيانات بعد إزالة القيم الشاذة في: {OUTPUT_PATH}")
