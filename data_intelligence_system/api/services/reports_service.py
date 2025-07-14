import os
from pathlib import Path
import pandas as pd
from typing import List
from datetime import datetime
from jinja2 import Environment, FileSystemLoader, TemplateNotFound
from weasyprint import HTML

from data_intelligence_system.utils.data_loader import load_data
from data_intelligence_system.analysis.descriptive_stats import generate_descriptive_stats
from data_intelligence_system.utils.logger import get_logger
from data_intelligence_system.reports.report_dispatcher import generate_report
from data_intelligence_system.config.report_config import REPORT_CONFIG

logger = get_logger("report.service")

BASE_DIR = Path(__file__).resolve().parents[2]
TEMPLATE_DIR = BASE_DIR / "reports" / "generators" / "templates"
REPORTS_OUTPUT_DIR = Path(REPORT_CONFIG["output_dir"])


def ensure_dir(path: Path):
    """Ensure directory exists."""
    path.mkdir(parents=True, exist_ok=True)
    logger.info(f"📂 تم التأكد من وجود المجلد: {path}")


class ReportsService:
    """
    خدمة توليد التقارير بمختلف الصيغ: HTML, PDF, Excel.
    """

    def generate_summary_report(
        self,
        file_path: str,
        output_dir: Path = REPORTS_OUTPUT_DIR,
        output_format: str = "html",
        title: str = "Data Summary Report"
    ) -> bool:
        """
        يولّد تقريرًا موجزًا من ملف بيانات.
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

            html_path = self.generate_html(file_path, stats, title, output_dir)

            if output_format == "html":
                return True

            elif output_format == "pdf":
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                config = {"filename": f"summary_report_{timestamp}", "title": title}
                generate_report(data=df, report_type="pdf", config=config)
                return True

            elif output_format == "excel":
                dfs = [
                    pd.DataFrame([stats.get("general_info", {})]),
                    pd.DataFrame(stats.get("numeric_summary", {})).T
                ]
                if len(dfs) != 2:
                    logger.warning("⚠️ عدد أوراق العمل لا يتطابق مع البيانات.")
                excel_filename = f"{Path(file_path).stem}_summary.xlsx"
                self.export_to_excel(dfs, ["General Info", "Numeric Summary"], excel_filename, output_dir)
                return True

            else:
                logger.warning(f"⚠️ نوع الإخراج غير مدعوم: {output_format}")
                return False

        except Exception as e:
            logger.error(f"❌ فشل في توليد التقرير: {e}", exc_info=True)
            return False

    def generate_html(self, data_path: str, stats: dict, title: str, output_dir: Path) -> Path:
        """ينشئ تقرير HTML باستخدام القالب."""
        ensure_dir(output_dir)
        try:
            env = Environment(loader=FileSystemLoader(str(TEMPLATE_DIR)))
            template = env.get_template("base_report.html")
        except TemplateNotFound:
            logger.error(f"❌ قالب التقرير غير موجود: {TEMPLATE_DIR}")
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

        output_path = output_dir / f"{Path(data_path).stem}_report.html"
        try:
            output_path.write_text(html_content, encoding="utf-8")
            logger.info(f"✅ تم إنشاء تقرير HTML: {output_path}")
        except Exception as e:
            logger.error(f"❌ فشل في حفظ تقرير HTML: {e}", exc_info=True)
            raise

        return output_path

    def convert_html_to_pdf(self, html_path: Path, output_dir: Path = REPORTS_OUTPUT_DIR) -> Path:
        """يحوّل تقرير HTML إلى PDF."""
        ensure_dir(output_dir)
        output_path = output_dir / (html_path.stem + ".pdf")
        try:
            HTML(str(html_path)).write_pdf(str(output_path))
            logger.info(f"📄 تم تحويل HTML إلى PDF: {output_path}")
        except Exception as e:
            logger.error(f"❌ فشل تحويل HTML إلى PDF: {e}", exc_info=True)
            raise
        return output_path

    def export_to_excel(
        self,
        dfs: List[pd.DataFrame],
        sheet_names: List[str],
        output_filename: str,
        output_dir: Path = REPORTS_OUTPUT_DIR
    ) -> Path:
        """يصدّر البيانات إلى ملف Excel."""
        ensure_dir(output_dir)
        output_path = output_dir / output_filename
        try:
            with pd.ExcelWriter(output_path) as writer:
                for df, name in zip(dfs, sheet_names):
                    df.to_excel(writer, sheet_name=name, index=False)
            logger.info(f"📊 تم حفظ تقرير Excel: {output_path}")
        except Exception as e:
            logger.error(f"❌ فشل في حفظ تقرير Excel: {e}", exc_info=True)
            raise
        return output_path


_service_instance = ReportsService()

def generate_summary_report(*args, **kwargs):
    return _service_instance.generate_summary_report(*args, **kwargs)

def convert_html_to_pdf(html_path: str, output_dir: str = REPORTS_OUTPUT_DIR):
    return _service_instance.convert_html_to_pdf(Path(html_path), Path(output_dir))

def export_to_excel(
    dfs: List[pd.DataFrame],
    sheet_names: List[str],
    output_filename: str,
    output_dir: str = REPORTS_OUTPUT_DIR
):
    return _service_instance.export_to_excel(dfs, sheet_names, output_filename, Path(output_dir))
