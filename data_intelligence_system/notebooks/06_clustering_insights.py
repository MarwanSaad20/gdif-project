import os
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    accuracy_score,
    mean_squared_error,
    r2_score,
)
import joblib
from pathlib import Path

# ======= ضبط المسارات النسبية بناءً على مكان السكربت =======
try:
    project_root = Path(__file__).resolve().parents[1]  # مجلد data_intelligence_system
except NameError:
    project_root = Path.cwd().parents[1]  # عند تشغيل السكربت في بيئة لا تحتوي على __file__

DATA_PATH = project_root / "data" / "processed" / "clean_data.csv"
MODEL_PATH = project_root / "ml_models" / "trained_model.pkl"
EXPORT_DIR = project_root / "reports" / "output"
EXPORT_PATH = EXPORT_DIR / "predictions_output.csv"

print(f"🔍 تحميل البيانات من: {DATA_PATH}")
df = pd.read_csv(DATA_PATH)

# ======= تحديد عمود الهدف =======
target_candidates = ['target', 'label', 'y', 'species', 'is_fragrant']

target = None
for col in df.columns:
    if col.lower() in target_candidates:
        target = col
        print(f"🎯 تم التعرف على عمود الهدف: {target}")
        break

if target is None:
    print("⚠️ لم يتم العثور على عمود هدف واضح في البيانات. الأعمدة المتاحة:")
    print(", ".join(df.columns))
    sys.exit("🚨 الرجاء تحديد عمود الهدف في البيانات.")

# ======= فصل السمات الرقمية والهدف =======
X = df.drop(columns=[target]).select_dtypes(include=[np.number]).fillna(0)
y = df[target]

if X.shape[1] == 0:
    sys.exit("🚫 لا توجد سمات رقمية مناسبة للنمذجة بعد إزالة عمود الهدف.")

# ======= التحقق من وجود النموذج =======
if not MODEL_PATH.exists():
    sys.exit(f"🚫 النموذج المدرب غير موجود في المسار: {MODEL_PATH}")

# ======= تحميل النموذج =======
model = joblib.load(MODEL_PATH)
print(f"✅ تم تحميل النموذج المدرب بنجاح من: {MODEL_PATH}")

# ======= التنبؤ =======
y_pred = model.predict(X)

# ======= تحليل النتائج =======
is_classification = y.nunique() <= 10

if is_classification:
    acc = accuracy_score(y, y_pred)
    print(f"🎯 الدقة الإجمالية: {acc:.4f}\n")
    print("📌 تقرير التصنيف:")
    print(classification_report(y, y_pred))

    cm = confusion_matrix(y, y_pred)
    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues')
    plt.title("مصفوفة الالتباس النهائية")
    plt.xlabel('Predicted')
    plt.ylabel('Actual')
    plt.tight_layout()
    plt.show()

else:
    rmse = mean_squared_error(y, y_pred, squared=False)
    r2 = r2_score(y, y_pred)
    print(f"📉 RMSE: {rmse:.4f}\n📈 R²: {r2:.4f}")

    plt.figure(figsize=(8, 6))
    sns.scatterplot(x=y, y=y_pred, alpha=0.6, color='green')
    plt.title("Actual vs Predicted")
    plt.xlabel("Actual")
    plt.ylabel("Predicted")
    plt.tight_layout()
    plt.show()

# ======= حفظ التنبؤات =======
EXPORT_DIR.mkdir(parents=True, exist_ok=True)

results_df = pd.DataFrame({
    'Actual': y,
    'Predicted': y_pred
})

results_df.to_csv(EXPORT_PATH, index=False)
print(f"✅ تم حفظ النتائج النهائية في: {EXPORT_PATH}")
