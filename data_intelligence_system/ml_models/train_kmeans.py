import pandas as pd
from sklearn.cluster import KMeans
import joblib
from pathlib import Path

def main():
    # مسار ملف البيانات المعالجة (نظف بياناتك مسبقًا)
    data_path = Path("data_intelligence_system/data/processed/clean_data.csv")
    
    # تحميل البيانات
    df = pd.read_csv(data_path)

    # اختيار الأعمدة الرقمية فقط (يمكن تعديلها حسب بياناتك)
    num_cols = df.select_dtypes(include=["number"]).columns
    X = df[num_cols].fillna(0)  # تعويض القيم المفقودة إن وجدت

    # تهيئة نموذج KMeans بعدد المجموعات التي تريدها (مثلاً 3)
    n_clusters = 3
    model = KMeans(n_clusters=n_clusters, random_state=42)

    # تدريب النموذج
    model.fit(X)

    # تحديد مسار حفظ النموذج
    model_path = Path("data_intelligence_system/ml_models/trained_model.pkl")
    model_path.parent.mkdir(parents=True, exist_ok=True)  # إنشاء المجلدات إذا لم تكن موجودة

    # حفظ النموذج
    joblib.dump(model, model_path)

    print(f"✅ تم تدريب وحفظ نموذج KMeans في: {model_path}")

if __name__ == "__main__":
    main()
