# 📊 Analysis Module — Data Intelligence System

هذا المجلد يحتوي على جميع التحليلات الإحصائية والاستكشافية التي تُجرى بعد تنظيف البيانات وقبل بناء النماذج. الهدف هو استخراج **رؤى ذكية**، كشف الأنماط، فهم العلاقات، والتأكد من جودة البيانات.

---

## 🧠 محتوى المجلد:

| الملف | الوصف |
|-------|--------|
| `descriptive_stats.py` | إحصاءات وصفية: المتوسط، الوسيط، الانحراف المعياري، النسب، التوزيعات |
| `correlation_analysis.py` | تحليل الترابط بين المتغيرات باستخدام Pearson/Spearman + مصفوفة Heatmap |
| `outlier_detection.py` | كشف القيم الشاذة باستخدام IQR، Z-score، وIsolationForest |
| `clustering_analysis.py` | تحليل التجمعات باستخدام KMeans وDBSCAN مع تقارير وVisuals |
| `target_relation_analysis.py` | تحليل العلاقة بين المتغيرات والمتغير الهدف باستخدام ANOVA وChi-Square |
| `analysis_utils.py` | دوال مساعدة مشتركة لكل التحليلات (حفظ الرسوم، فلترة الأعمدة، تسجيل المعلومات) |
| `analysis_output/` | مجلد يحتوي على المخرجات النهائية لكل التحليلات (صور، جداول، تقارير HTML) |

---

## 🧪 كيفية الاستخدام

1. تأكد من أن البيانات المنظفة موجودة في `data/processed/`.
2. شغّل أي سكربت بشكل منفصل مثل:

```bash
python analysis/descriptive_stats.py
python analysis/correlation_analysis.py
