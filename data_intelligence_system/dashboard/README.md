# 📊 Dashboard Module — Data Intelligence System

هذا المجلد مسؤول عن **واجهة المستخدم التفاعلية** للنظام، باستخدام مكتبة Dash المبنية على Flask. يوفر واجهة رسومية متقدمة تُمكّن المستخدم من استعراض البيانات، تنفيذ التحليلات، عرض النتائج، والتفاعل مع النماذج بشكل سلس وعملي.

---

## 🧠 محتوى المجلد:

| الملف / المجلد          | الوصف                                                                                      |
|------------------------|--------------------------------------------------------------------------------------------|
| `app.py`               | نقطة الدخول الرئيسية لتشغيل تطبيق الويب (Dash + Flask).                                   |
| `layouts.py`           | تعريف التخطيطات (Layouts) الخاصة بالصفحات والمكونات الرئيسية للواجهة.                      |
| `callbacks.py`         | تسجيل ردود الأفعال (Callbacks) التي تربط عناصر الواجهة بوظائف معالجة البيانات والتحديث.    |
| `components/`          | مكونات واجهة قابلة لإعادة الاستخدام: جداول، رسوم بيانية، فلاتر، مؤشرات أداء، وغيرها.     |
| `data_bindings.py`     | وظائف لجلب البيانات وربطها بالنماذج، التحليلات، والواجهة.                                |
| `assets/`              | ملفات static مثل CSS, JavaScript, الصور، والخطوط التي يستخدمها Dash تلقائيًا.             |
| `config.py`            | إعدادات خاصة بالواجهة مثل خيارات الثيم، API endpoints، إعدادات عامة للـ dashboard.         |
| `utils.py`             | أدوات مساعدة للواجهة: تحويل تواريخ، تنسيقات نصوص، دوال مساعدة صغيرة.                      |
| `tests/`               | اختبارات وحدات (Unit Tests) للتأكد من سلامة ردود الأفعال والمكونات باستخدام pytest.       |
| `README.md`            | توثيق يشرح هيكل المجلد، استخدامه، وكيفية التوسع فيه.                                    |

---

## 🚀 كيفية الاستخدام

1. تأكد من تنصيب جميع المكتبات المطلوبة (مثل `dash`, `pandas`, `plotly`، وغيرها) من ملف `requirements.txt`.

2. لتشغيل التطبيق محليًا:

```bash
cd dashboard
python app.py
