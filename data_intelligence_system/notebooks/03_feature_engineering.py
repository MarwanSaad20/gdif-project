# =============================
# ⚙️ 03 – Feature Engineering
# =============================

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import PolynomialFeatures
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from pathlib import Path
import sys
import warnings

warnings.filterwarnings("ignore")
sns.set_theme(style="whitegrid")

# ============================
# 📂 تحميل البيانات
# ============================

def load_data():
    try:
        # نصعد مرتين للوصول لجذر المشروع PythonProject10
        project_root = Path(__file__).resolve().parents[2]
    except NameError:
        project_root = Path.cwd().parents[1]

    # ✅ إضافة جذر المشروع إلى sys.path للتكامل مع config/paths_config.py
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

    data_path = project_root / "data_intelligence_system" / "data" / "processed" / "clean_data.csv"
    if not data_path.exists():
        raise FileNotFoundError(f"الملف غير موجود: {data_path}")
    df = pd.read_csv(data_path)
    print(f"✅ البيانات المحملة: {df.shape}")
    return df

# =============================================
# 🧪 توليد سمات جديدة مشتقة (فرق، نسب، مجموع)
# =============================================

def generate_derived_features(df):
    numeric_cols = df.select_dtypes(include=["int64", "float64"]).columns.tolist()
    if len(numeric_cols) >= 2:
        df['diff_feature'] = df[numeric_cols[0]] - df[numeric_cols[1]]
        df['ratio_feature'] = df[numeric_cols[0]] / (df[numeric_cols[1]] + 1e-5)
        df['sum_feature'] = df[numeric_cols[0]] + df[numeric_cols[1]]
        print("✅ تم توليد السمات المشتقة (فرق، نسبة، مجموع)")
    return df, numeric_cols

# ===========================================
# 🧮 Polynomial Features (تفاعلات مرتبة)
# ===========================================

def generate_polynomial_features(df, numeric_cols):
    if len(numeric_cols) >= 2:
        poly = PolynomialFeatures(degree=2, interaction_only=True, include_bias=False)
        poly_features = poly.fit_transform(df[[numeric_cols[0], numeric_cols[1]]])
        poly_df = pd.DataFrame(poly_features, columns=poly.get_feature_names_out([numeric_cols[0], numeric_cols[1]]))
        df = pd.concat([df, poly_df.iloc[:, 2:]], axis=1)  # استثناء الأعمدة الأصلية
        print("✅ تم توليد السمات متعددة الحدود (تفاعلية)")
    return df

# =================================
# ⏳ استخراج السمات من التواريخ
# =================================

def generate_datetime_features(df):
    object_cols = df.select_dtypes(include=["object"]).columns.tolist()
    for col in object_cols:
        try:
            sample = df[col].dropna().iloc[0]
            pd.to_datetime(sample)  # محاولة أولية للتحقق
            df[col] = pd.to_datetime(df[col], errors='coerce')
            df[f"{col}_year"] = df[col].dt.year
            df[f"{col}_month"] = df[col].dt.month
            df[f"{col}_day"] = df[col].dt.day
            df[f"{col}_weekday"] = df[col].dt.weekday
            print(f"✅ تم استخراج سمات زمنية من العمود: {col}")
        except Exception:
            continue
    return df

# ============================================
# ⭐ تحليل أهمية السمات باستخدام Random Forest
# ============================================

def feature_importance_analysis(df):
    possible_targets = [col for col in df.columns if col.lower() in ["target", "label", "y"]]
    
    if not possible_targets:
        print("🚫 لم يتم العثور على عمود هدف. يمكنك التعديل يدويًا داخل السكربت لتحديده.")
        print(f"🧠 الأعمدة المتاحة: {list(df.columns)}")
        return
    
    target = possible_targets[0]
    print(f"🎯 سيتم استخدام العمود '{target}' كهدف.")

    X = df.drop(columns=[target]).select_dtypes(include=["float64", "int64"]).fillna(0)
    y = df[target]

    if y.nunique() <= 10:
        model = RandomForestClassifier(random_state=42)
    else:
        model = RandomForestRegressor(random_state=42)

    model.fit(X, y)
    importances = pd.Series(model.feature_importances_, index=X.columns).sort_values(ascending=False)

    plt.figure(figsize=(10, 6))
    sns.barplot(x=importances.values[:10], y=importances.index[:10], palette='viridis')
    plt.title("Top 10 Feature Importances")
    plt.tight_layout()
    plt.show()
    print("✅ تم تحليل أهمية السمات.")

# ======================
# 🚀 نقطة تشغيل السكربت
# ======================

if __name__ == "__main__":
    df = load_data()
    df, numeric_cols = generate_derived_features(df)
    df = generate_polynomial_features(df, numeric_cols)
    df = generate_datetime_features(df)
    feature_importance_analysis(df)
