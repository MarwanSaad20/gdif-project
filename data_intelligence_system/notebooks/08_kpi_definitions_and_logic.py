# 🎯 08 – تعريف مؤشرات الأداء الرئيسية (KPIs) ومنطق حسابها

"""
الهدف:
- تحديد مؤشرات الأداء المهمة وتحويلها إلى حسابات منطقية قابلة للتنفيذ باستخدام البيانات.
- تصدير مؤشرات الأداء بصيغ متعددة لتحليل أو تقارير.

المخرجات:
- تعريف واضح لكل KPI
- حساب كل KPI من البيانات
- مثال على تصدير KPIs
"""

import sys
import json
import pprint
import pandas as pd
import numpy as np
from pathlib import Path

# --- إعداد المسارات بشكل متوافق مع Jupyter وملفات .py ---
try:
    SCRIPT_PATH = Path(__file__).resolve()
except NameError:
    SCRIPT_PATH = Path.cwd()

BASE_DIR = SCRIPT_PATH.parent.parent
DATA_PATH = BASE_DIR / 'data' / 'processed' / 'clean_data.csv'
REPORTS_DIR = BASE_DIR / 'reports'
REPORTS_DIR.mkdir(exist_ok=True)

EXPORT_PATH_CSV = REPORTS_DIR / 'kpis.csv'
EXPORT_PATH_JSON = REPORTS_DIR / 'kpis.json'

print(f"SCRIPT_PATH = {SCRIPT_PATH}")
print(f"BASE_DIR = {BASE_DIR}")
print(f"DATA_PATH = {DATA_PATH}")
print(f"DATA_PATH exists = {DATA_PATH.exists()}")

if not DATA_PATH.exists():
    sys.exit(f"⚠️ لم يتم العثور على ملف البيانات: {DATA_PATH}")

# --- تحميل البيانات ---
df = pd.read_csv(DATA_PATH)

# --- تعديل دالة تحديد عمود الهدف لتشمل الأعمدة الممكنة في بياناتك ---
def find_target_column(df):
    for col in df.columns:
        if col.lower() in ['target', 'label', 'y', 'species', 'is_fragrant']:
            return col
    return None

target_col = find_target_column(df)
if not target_col:
    print(f"الأعمدة المتاحة: {df.columns.tolist()}")
    sys.exit("⚠️ لم يتم تحديد عمود الهدف")

# --- معالجة القيم الناقصة في عمود الهدف ---
df = df.dropna(subset=[target_col])

# --- تعريف KPIs مع التعامل مع أنواع الهدف عددي أو نصي ---
def calculate_kpis(df, target_col):
    kpis = {}
    target_data = df[target_col]

    if pd.api.types.is_numeric_dtype(target_data):
        # الهدف عددّي
        kpis['average_target'] = target_data.mean()
        threshold = target_data.quantile(0.75)
        kpis['above_75th_percentile'] = (target_data > threshold).mean()
    else:
        # الهدف نصّي (تصنيفي)
        kpis['target_value_counts'] = target_data.value_counts().to_dict()
        kpis['target_unique_values'] = target_data.nunique()

    # عدد الفئات الفريدة في الأعمدة النوعية
    kpis['unique_categories'] = df.select_dtypes(include=['object']).nunique().to_dict()

    # نسبة القيم الناقصة في كل عمود
    kpis['missing_values_ratio'] = df.isna().mean().to_dict()

    # إذا كان هناك عمود 'category' وعددي، حساب متوسط الهدف حسب فئة
    if 'category' in df.columns and pd.api.types.is_numeric_dtype(target_data):
        kpis['target_mean_by_category'] = df.groupby('category')[target_col].mean().to_dict()

    return kpis

kpis = calculate_kpis(df, target_col)

# --- دالة لتفكيك القواميس داخل KPIs لتسهيل التصدير ---
def flatten_kpis(kpis):
    flat_kpis = {}
    for key, val in kpis.items():
        if isinstance(val, dict):
            for subkey, subv in val.items():
                flat_kpis[f"{key}_{subkey}"] = subv
        else:
            flat_kpis[key] = val
    return flat_kpis

flat_kpis = flatten_kpis(kpis)

# --- عرض النتائج بشكل جميل ---
pp = pprint.PrettyPrinter(indent=2)
print("### مؤشرات الأداء الرئيسية (KPIs) المحسوبة:")
pp.pprint(kpis)

# --- تصدير KPIs ---
def export_kpis(flat_kpis, kpis, csv_path, json_path):
    # تصدير إلى CSV
    kpis_df = pd.DataFrame.from_dict(flat_kpis, orient='index', columns=['Value'])
    kpis_df.to_csv(csv_path)
    print(f"✅ تم تصدير KPIs إلى ملف CSV: {csv_path}")

    # تصدير إلى JSON (الهيكل الأصلي مع القواميس)
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(kpis, f, ensure_ascii=False, indent=2)
    print(f"✅ تم تصدير KPIs إلى ملف JSON: {json_path}")

export_kpis(flat_kpis, kpis, EXPORT_PATH_CSV, EXPORT_PATH_JSON)

if __name__ == "__main__":
    pass
