from pathlib import Path
from ydata_profiling import ProfileReport
from ydata_profiling.config import Settings  # استيراد إعدادات التهيئة
from eda_utils import load_clean_data, logger

# تحديد جذر المشروع بالنسبة لهذا الملف (عدّل حسب موقع ملفك)
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DEFAULT_DATA_PATH = BASE_DIR / "data_intelligence_system" / "data" / "processed" / "clean_data.csv"

OUTPUT_DIR = BASE_DIR / "data_profiles" / "eda_output"
HTML_REPORT = OUTPUT_DIR / "eda_ydata_report.html"
JSON_REPORT = OUTPUT_DIR / "eda_ydata_report.json"


def generate_ydata_report(
    data_path: Path | str = None,
    html_output: Path | str = HTML_REPORT,
    json_output: Path | str = JSON_REPORT
):
    """
    توليد تقرير ydata-profiling التحليلي للبيانات.

    Args:
        data_path (Path | str): مسار البيانات النظيفة (اختياري).
        html_output (Path | str): مسار حفظ تقرير HTML.
        json_output (Path | str): مسار حفظ تقرير JSON.
    """
    logger.info("🚀 بدء توليد تقرير ydata-profiling ...")

    data_path = Path(data_path) if data_path else DEFAULT_DATA_PATH
    html_output = Path(html_output)
    json_output = Path(json_output)

    logger.info(f"📥 جاري تحميل البيانات من: {data_path}")

    try:
        df = load_clean_data(path=str(data_path))

        # إعداد التهيئة الصحيحة لـ correlations
        settings = Settings(
            correlations={
                "pearson": {"calculate": True},
                "spearman": {"calculate": True},
                "kendall": {"calculate": False}
            }
        )

        profile = ProfileReport(
            df,
            title="YData Profiling Report",
            explorative=True,
            config=settings
        )
        logger.info("✅ تم إنشاء تقرير التحليل التفصيلي")

        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

        # حفظ التقرير كـ HTML
        profile.to_file(html_output)
        logger.info(f"📄 تم حفظ تقرير HTML في: {html_output}")

        # حفظ التقرير كـ JSON (باستخدام to_json() وليس to_file() لأن to_file لا تدعم JSON)
        json_str = profile.to_json()
        with open(json_output, 'w', encoding='utf-8') as f:
            f.write(json_str)
        logger.info(f"📊 تم حفظ تقرير JSON في: {json_output}")

    except FileNotFoundError:
        logger.error(f"❌ الملف غير موجود: {data_path}")
    except Exception:
        logger.exception("❌ فشل توليد تقرير ydata-profiling")


# إمكانية التشغيل كملف مستقل
if __name__ == "__main__":
    generate_ydata_report()
