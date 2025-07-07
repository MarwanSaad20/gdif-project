# ML Models Module - Data Intelligence System

## 🧠 نظرة عامة

هذا المجلد يحتوي على جميع نماذج تعلم الآلة في نظام تحليل البيانات الذكي (GDIF).  
وُضع ليكون مرنًا، قابلاً للتوسعة، ومتناسقًا مع بقية النظام عبر واجهة `BaseModel` الموحّدة، التي تضمن توحيد التعامل مع جميع النماذج من تدريب، توقع، حفظ وتحميل.

يدعم النظام أربعة أنواع رئيسية من النماذج:

- **الانحدار (Regression)**: للتنبؤ بالقيم المستمرة.
- **التصنيف (Classification)**: لتصنيف الفئات.
- **التجميع (Clustering)**: لتقسيم البيانات غير المسمّاة إلى مجموعات.
- **التنبؤ الزمني (Forecasting)**: لتحليل وتوقع بيانات السلاسل الزمنية.

---

## 📁 هيكل المجلد والملفات

| الملف / المجلد                       | الوصف                                                                 |
|-------------------------------------|------------------------------------------------------------------------|
| `base_model.py`                     | كلاس أساسي موحد لجميع النماذج يحتوي على (fit, predict, save, load).    |
| `regression/`                       | نماذج الانحدار (Linear, Lasso, Ridge).                                 |
| `classification/`                  | نماذج التصنيف (Logistic, Random Forest, XGBoost).                      |
| `clustering/`                       | نماذج التجميع (KMeans, DBSCAN).                                       |
| `forecasting/`                      | نماذج التنبؤ الزمني (ARIMA, Prophet).                                  |
| `utils/`                            | أدوات مساعدة للتقييم (MSE, Accuracy...) والمعالجة المسبقة (تحجيم، تقسيم...). |
| `model_factory.py`                  | محرك ديناميكي لإنشاء النموذج الصحيح بناءً على النوع والاسم.             |
| `README.md`                         | هذا الملف: توثيق آلية العمل.                                           |

---

## 🛠️ الاستخدام الأساسي

### 1. استدعاء نموذج ديناميكي باستخدام `model_factory`

```python
from ml_models.model_factory import get_model

model = get_model(model_type="regression", model_name="lasso", alpha=0.1)
model.fit(X_train, y_train)
predictions = model.predict(X_test)
