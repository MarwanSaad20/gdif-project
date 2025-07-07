# ⚙️ Config Module — General Data Intelligence Framework (GDIF)

هذا المجلد يحتوي على جميع ملفات الإعدادات المركزية التي تتحكم بسلوك النظام، من مسارات البيانات، إعدادات النماذج، تفاصيل التقارير، إعدادات الواجهة التفاعلية، إلى مفاتيح التشغيل البيئي.

الهدف هو فصل التهيئة (Configuration) عن التنفيذ (Execution)، وضمان مرونة وسهولة التخصيص دون تعديل الأكواد الرئيسية.

---

## 📂 محتويات المجلد

| الملف | الوصف |
|-------|--------|
| `paths_config.py` | مسارات الملفات والمجلدات الأساسية (بيانات، تقارير، مخرجات، إلخ) |
| `model_config.py` | إعدادات نماذج تعلم الآلة: المعاملات الافتراضية، أسماء، أنواع، إلخ |
| `report_config.py` | إعدادات التقارير: العنوان، الألوان، الشعار، القوالب، نوع الإخراج |
| `dashboard_config.py` | إعدادات واجهة Dash: الأقسام، الثيم، KPIs، عدد السجلات، خطوط |
| `env_config.py` | تحميل الإعدادات البيئية (من .env أو متغيرات النظام): السرية، اللغة، المسارات، البريد |
| `config_loader.py` | واجهة موحدة لتحميل جميع الإعدادات في كائن `CONFIG` جاهز للاستخدام |

---

## 🧠 استخدام موحد لجميع الإعدادات

بدلًا من استيراد كل إعداد بشكل منفصل، يمكنك فقط استيراد الكائن المركزي:

```python
from config.config_loader import CONFIG

# أمثلة:
print(CONFIG.paths.PROCESSED_DATA_PATH)
print(CONFIG.models.CLASSIFICATION_MODELS["random_forest"])
print(CONFIG.reports.REPORT_TITLE)
print(CONFIG.dashboard.KPI_SETTINGS["revenue"]["color"])
print(CONFIG.env.DEBUG_MODE)
