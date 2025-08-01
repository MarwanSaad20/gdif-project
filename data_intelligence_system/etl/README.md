# ETL Module - Data Intelligence System

## نظرة عامة

هذا المجلد يحتوي على وحدات ETL (Extract - Transform - Load) التي تشكل جوهر معالجة البيانات في نظام تحليل البيانات الذكي.  
المهام الأساسية هي:

- **استخراج** البيانات من مصادر متعددة (ملفات CSV, Excel, JSON، قواعد بيانات، APIs،...).
- **تنظيف وتحويل** البيانات (معالجة القيم المفقودة، توحيد الأعمدة، ترميز، توازن).
- **تحميل** البيانات المنظفة بصيغ مختلفة مع خيارات للأرشفة.

النظام مصمم ليكون مرن، متين، وقابل للتوسع بسهولة.

---

## هيكل المجلد والملفات

| الملف            | الوصف                                              |
|------------------|---------------------------------------------------|
| `extract.py`     | قراءة البيانات من كل المصادر المدعومة.            |
| `transform.py`   | تنظيف، معالجة، وتوحيد مجموعات البيانات.           |
| `load.py`        | حفظ البيانات المعالجة بصيغ متعددة (csv, parquet, excel). |
| `pipeline.py`    | تسلسل متكامل لتنفيذ جميع مراحل ETL دفعة واحدة.    |
| `etl_utils.py`   | دوال مساعدة مشتركة مثل التحقق من جودة البيانات، التعرف على نوع الملف، وآليات اللوق. |
| `README.md`      | هذا الملف: شرح شامل للآلية وطريقة الاستخدام.       |

---

## طريقة الاستخدام

### 1. تشغيل التسلسل الكامل ETL

```bash
python -m data_intelligence_system.etl.pipeline
