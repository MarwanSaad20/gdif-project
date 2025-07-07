import os
import logging
import pandas as pd
from typing import List
from datetime import datetime
from jinja2 import Environment, FileSystemLoader, TemplateNotFound
from weasyprint import HTML
from data_intelligence_system.utils.data_loader import load_data
from data_intelligence_system.analysis.descriptive_stats import generate_descriptive_stats
from data_intelligence_system.utils.logger import get_logger

# استخدام اللوقر الموحد
logger = get_logger("report.service")

# مسارات ثابتة
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TEMPLATE_DIR = os.path.join(BASE_DIR, "reports", "templates")
REPORTS_OUTPUT_DIR = os.path.join(BASE_DIR, "reports", "generated")

def ensure_dir(path: str):
    """إنشاء مجلد إذا لم يكن موجودًا."""
    if not os.path.exists(path):
        os.makedirs(path)
        logger.info(f"📂 تم إنشاء المجلد: {path}")

class ReportsService:

    def generate_summary_report(
        self,
        file_path: str,
        output_dir: str = REPORTS_OUTPUT_DIR,
        output_format: str = "html",
        title: str = "Data Summary Report"
    ) -> bool:
        """
        توليد تقرير ملخص للبيانات بصيغ HTML أو PDF أو Excel.
        """
        try:
            df = load_data(file_path)
            if df.empty:
                logger.warning(f"⚠️ الملف فارغ: {file_path}")
                return False

            stats = generate_descriptive_stats(df, save_outputs=False)
            if not stats:
                logger.warning("⚠️ لم يتم حساب الإحصائيات بنجاح.")
                return False

            # توليد تقرير HTML أولاً
            html_path = self._generate_html(file_path, stats, title, output_dir)

            if output_format == "html":
                return True

            elif output_format == "pdf":
                self._convert_html_to_pdf(html_path, output_dir)
                return True

            elif output_format == "excel":
                dfs = [
                    pd.DataFrame([stats.get("general_info", {})]),
                    pd.DataFrame(stats.get("numeric_summary", {})).T
                ]
                base_name = os.path.splitext(os.path.basename(file_path))[0]
                excel_filename = f"{base_name}_summary.xlsx"
                self._export_to_excel(dfs, ["General Info", "Numeric Summary"], excel_filename, output_dir)
                return True

            else:
                logger.warning(f"⚠️ نوع الإخراج غير مدعوم: {output_format}")
                return False

        except Exception as e:
            logger.error(f"❌ فشل في توليد التقرير: {e}", exc_info=True)
            return False

    def _generate_html(self, data_path: str, stats: dict, title: str, output_dir: str) -> str:
        ensure_dir(output_dir)
        try:
            env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
            template = env.get_template("base_report.html")
        except TemplateNotFound:
            logger.error(f"❌ قالب التقرير غير موجود في المسار: {TEMPLATE_DIR}")
            raise
        except Exception as e:
            logger.error(f"❌ خطأ أثناء تحميل القالب: {e}", exc_info=True)
            raise

        html_content = template.render(
            title=title,
            general_info=stats.get("general_info", {}),
            numeric_summary=stats.get("numeric_summary", {}),
            generated_on=datetime.now().strftime("%Y-%m-%d %H:%M"),
            additional_images=[]
        )

        filename = os.path.splitext(os.path.basename(data_path))[0] + "_report.html"
        output_path = os.path.join(output_dir, filename)

        try:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(html_content)
            logger.info(f"✅ تم إنشاء تقرير HTML: {output_path}")
        except Exception as e:
            logger.error(f"❌ فشل في حفظ تقرير HTML: {e}", exc_info=True)
            raise

        return output_path

    def _convert_html_to_pdf(self, html_path: str, output_dir: str) -> str:
        ensure_dir(output_dir)
        basename = os.path.splitext(os.path.basename(html_path))[0] + ".pdf"
        output_path = os.path.join(output_dir, basename)

        try:
            HTML(html_path).write_pdf(output_path)
            logger.info(f"📄 تم تحويل HTML إلى PDF: {output_path}")
        except Exception as e:
            logger.error(f"❌ فشل تحويل HTML إلى PDF: {e}", exc_info=True)
            raise

        return output_path

    def _export_to_excel(
        self,
        dfs: List[pd.DataFrame],
        sheet_names: List[str],
        output_filename: str,
        output_dir: str
    ) -> str:
        ensure_dir(output_dir)
        output_path = os.path.join(output_dir, output_filename)

        try:
            with pd.ExcelWriter(output_path) as writer:
                for df, name in zip(dfs, sheet_names):
                    df.to_excel(writer, sheet_name=name, index=False)
            logger.info(f"📊 تم حفظ تقرير Excel: {output_path}")
        except Exception as e:
            logger.error(f"❌ فشل في حفظ تقرير Excel: {e}", exc_info=True)
            raise

        return output_path

# ===========================
# دوال خارج الكلاس للاستخدام الخارجي
# ===========================

_service_instance = ReportsService()

def generate_summary_report(*args, **kwargs):
    return _service_instance.generate_summary_report(*args, **kwargs)

def convert_html_to_pdf(html_path: str, output_dir: str = REPORTS_OUTPUT_DIR):
    return _service_instance._convert_html_to_pdf(html_path, output_dir)

def export_to_excel(
    dfs: List[pd.DataFrame],
    sheet_names: List[str],
    output_filename: str,
    output_dir: str = REPORTS_OUTPUT_DIR
):
    return _service_instance._export_to_excel(dfs, sheet_names, output_filename, output_dir)
