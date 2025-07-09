# 🔍 07 – تحليل العلاقة مع المتغير الهدف
"""
الهدف: فهم قوة وتأثير كل متغير مستقل على المتغير الهدف باستخدام أساليب تحليلية وإحصائية متعددة.

المخرجات:
- مقاييس ارتباط (Pearson, Spearman, Cramér's V)
- تحليلات الانحدار البسيط
- رسومات توضيحية (Scatter, Boxplot, Heatmap)
- استنتاجات واضحة وقابلة للتطبيق
- ملف CSV ملخص للنتائج التحليلية
"""

import os
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import pearsonr, spearmanr, chi2_contingency
from sklearn.linear_model import LinearRegression
import warnings
from pathlib import Path

# ✅ استيراد التحليل الرسمي من النظام
from data_intelligence_system.analysis.target_relation_analysis import analyze_target_relation

warnings.filterwarnings('ignore')

# --- إعداد المسارات ---
try:
    SCRIPT_PATH = Path(__file__).resolve()
except NameError:
    SCRIPT_PATH = Path.cwd()

PROJECT_ROOT = SCRIPT_PATH.parent.parent
DATA_PATH = PROJECT_ROOT / 'data' / 'processed' / 'clean_data.csv'
OUTPUT_DIR = PROJECT_ROOT / 'reports' / 'output'
SUMMARY_OUTPUT_PATH = OUTPUT_DIR / 'target_relationship_summary.csv'
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

print(f"📁 DATA_PATH: {DATA_PATH}")
print(f"📁 OUTPUT_DIR: {OUTPUT_DIR}")

if not DATA_PATH.exists():
    sys.exit(f"⚠️ لم يتم العثور على ملف البيانات: {DATA_PATH}")

# --- تحميل البيانات ---
df = pd.read_csv(DATA_PATH)

# --- تحديد عمود الهدف تلقائيًا ---
target_col = None
possible_targets = ['target', 'label', 'y', 'species', 'is_fragrant']
for col in df.columns:
    if col.lower() in possible_targets:
        target_col = col
        break

if not target_col:
    print("الأعمدة الموجودة:", df.columns.tolist())
    sys.exit("⚠️ لا يوجد عمود هدف معروف")

print(f"🎯 عمود الهدف المحدد: {target_col}")

# --- استدعاء التحليل الرسمي من النظام ---
summary = analyze_target_relation(df, target=target_col)
print(summary)

# === باقي التحليلات والرسومات كما هي (إن وجدت) ===

if __name__ == "__main__":
    pass
