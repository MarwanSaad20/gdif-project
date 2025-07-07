# 🧠 نظام تحليل البيانات العام — General Data Intelligence Framework (GDIF)

نظام مرن ومتكامل لتحليل البيانات الخام من أي مصدر وتحويلها إلى رؤى قابلة للتنفيذ باستخدام Python، ETL، الإحصاء، تعلم الآلة، التقارير، ولوحة تحكم تفاعلية  Dash

---

## 🌟 الهدف

تم تصميم GDIF ليكون إطارًا عامًا لتحليل أي مجموعة بيانات خام، بغض النظر عن نوعها أو مصدرها، من خلال مراحل:

1. استخراج وتحويل وتحميل البيانات (ETL)
2. تحليل وصفي، ارتباطي، وتجمعي
3. نمذجة تنبؤية (ML)
4. توليد تقارير (HTML/PDF/Excel)
5. عرض النتائج عبر واجهة Dash تفاعلية
6. إمكانية التكامل مع API لاستخدام خارجي

---

## 🏠 الهيكل العام للمجلدات

```
data_intelligence_system/
├── data/                  # بيانات خام ومعالجة
│   ├── raw/               # ملفات أولية
│   └── processed/         # بيانات جاهزة للتحليل
│
├── data_profiles/         # ملفات وصف البيانات
│
├── etl/                   # استخراج وتحويل وتحميل
│   ├── extract.py
│   ├── transform.py
│   ├── load.py
│
├── analysis/              # تحليلات متقدمة
│   ├── descriptive_stats.py
│   ├── correlation_analysis.py
│   ├── clustering_analysis.py
│   ├── target_relation_analysis.py
│   ├── outlier_detection.py
│   └── analysis_utils.py
│
├── ml_models/             # نماذج تعلم الآلة (تخصيص لاحقًا)
│
├── dashboard/             # الواجهة التفاعلية  Dash
│   ├── app.py
│   ├── layout.py
│   └── callbacks.py
│
├── reports/               # تقارير بصيغ مختلفة
│   ├── templates/         # قوالب HTML
│   ├── generated/         # تقارير ناتجة
│   └── generators/        # خدمات التوليد البرمجية
│
├── config/                # إعدادات النظام
│   ├── paths_config.py
│   ├── model_config.py
│   ├── report_config.py
│   ├── dashboard_config.py
│   ├── env_config.py
│   └── config_loader.py
│
├── utils/                 # أدوات مساعدة
│   ├── data_loader.py
│   ├── visualization.py
│   ├── logger.py
│
├── api/                   # طبقة الخدمات والتوثيق
│   ├── services/
│   │   ├── etl_service.py
│   │   ├── analysis_service.py
│   │   └── reports_service.py
│   ├── utils/
│   │   ├── auth.py
│   │   ├── exceptions.py
│   │   ├── dependencies.py
│   │   └── logger.py
│   └── tests/             # اختبارات باستخدام pytest
│       ├── test_etl.py
│       ├── test_analysis.py
│       ├── test_reports.py
│       ├── test_dashboard.py
│       ├── test_auth.py
│       ├── test_config.py
│       ├── test_exceptions.py
│       ├── test_dependencies.py
│       └── conftest.py
│
├── main.py                # نقطة تشغيل شاملة
├── requirements.txt       # جميع التبعيات المطلوبة
└── README.md              # هذا الملف
```

---

## 🚀 تشغيل النظام

```bash
# لتشغيل كل الوحدات (ETL + تحليل + تقارير)
python main.py --etl --analyze --report

# لتشغيل الواجهة التفاعلية Dash
python main.py --dashboard
```

---

## 🤮 الاختبارات

يتم استخدام `pytest` + `httpx` لاختبار الخدمات:

```bash
pytest api/tests/
```

---

## 🔒 الأمن والتوثيق

* نظام JWT للتوثيق عبر `utils/auth.py`
* دعم لمفاتيح API و OAuth2 (قابل للتوسعة)
* سجل نشاط شامل عبر `utils/logger.py`

---

## 🧰 التوسع المستقبلي

* دعم قواعد بيانات (PostgreSQL / SQLite)
* دعم GraphQL / FastAPI
* دعم إرسال تقارير بالبريد
* إدارة المستخدمين والصلاحيات
* تشغيل آلي مجدول (Scheduler)

---

## 📬 تواصل

هذا النظام مخصص للاستخدام الداخلي والتحليلي، لكن يمكن تطويره كنواة لنظام SaaS تحليلي حقيقي في السوق.

---

## ✅ كود موحد لتحميل ك
