import os
import logging
from typing import Dict, Any, Union
import pandas as pd

from data_intelligence_system.reports.generators.pdf_report_generator import PDFReportGenerator
from data_intelligence_system.reports.generators.excel_report_generator import ExcelReportGenerator
from data_intelligence_system.reports.export_utils import (
    save_dataframe_to_csv,
    df_to_html_table
)
from data_intelligence_system.config.report_config import OUTPUT_PATH  # ✅ تعديل الاستيراد ليتوافق مع التحديث الجديد

logging.basicConfig(level=logging.INFO)


def ensure_dir(path: str):
    if not os.path.exists(path):
        os.makedirs(path)


class ReportDispatcher:
    def __init__(self, output_dir: str = str(OUTPUT_PATH)):
        self.output_dir = output_dir
        ensure_dir(self.output_dir)

    def dispatch(self, report_type: str, data: Union[pd.DataFrame, list], config: Dict[str, Any] = None) -> str:
        config = self._build_config(config)
        filename = config["filename"]
        full_path = os.path.join(self.output_dir, filename)

        if report_type == "pdf":
            return self._generate_pdf(data, full_path, config)
        elif report_type == "excel":
            return self._generate_excel(data, full_path, config)
        elif report_type == "csv":
            return self._generate_csv(data, filename)
        elif report_type == "html":
            return self._generate_html(data, full_path)
        else:
            raise ValueError(f"[ERROR] Unsupported report type: '{report_type}'")

    def _build_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        config = config or {}
        return {
            "filename": config.get("filename", "report"),
            "title": config.get("title", "Data Report"),
            "cover_image": config.get("cover_image")
        }

    def _generate_pdf(self, data: Union[pd.DataFrame, list], full_path: str, config: Dict[str, Any]) -> str:
        pdf_path = f"{full_path}.pdf"
        pdf_gen = PDFReportGenerator(pdf_path, title=config["title"])
        cover_image = config.get("cover_image")

        if isinstance(data, list):
            pdf_gen.build_pdf(data, cover_image_path=cover_image)
            return pdf_path
        if not isinstance(data, pd.DataFrame):
            raise TypeError("[ERROR] PDF report requires a DataFrame or pre-built sections list.")

        sections = self._build_pdf_sections(data, pdf_gen)
        pdf_gen.build_pdf(sections, cover_image_path=cover_image)
        logging.info(f"PDF report created at: {pdf_path}")
        return pdf_path

    def _build_pdf_sections(self, df: pd.DataFrame, pdf_gen: PDFReportGenerator) -> list:
        sections = []
        preview_data = [list(df.columns)] + df.head(10).values.tolist()
        preview_table = pdf_gen.create_table(preview_data)
        sections.append({"title": "📋 معاينة أولية للبيانات", "content": preview_table})

        for col in df.columns:
            series = df[col]
            title = f"🔎 تحليل العمود: {col}"

            if pd.api.types.is_numeric_dtype(series):
                desc = series.describe().round(2).to_string()
                content = pdf_gen.create_paragraph(f"📊 إحصائيات رقمية:\n{desc}")
            elif pd.api.types.is_datetime64_any_dtype(series):
                freq = series.dropna().dt.to_period("M").value_counts().sort_index()
                content = pdf_gen.create_paragraph(f"⏱️ التوزيع الشهري:\n{freq.to_string()}")
            elif pd.api.types.is_object_dtype(series) or pd.api.types.is_categorical_dtype(series):
                vc = series.value_counts(dropna=False).head(10)
                content = pdf_gen.create_paragraph(f"🔤 القيم الأكثر تكرارًا:\n{vc.to_string()}")
            else:
                content = pdf_gen.create_paragraph("⚠️ نوع العمود غير مدعوم بتحليل مباشر.")

            sections.append({"title": title, "content": content})

        note = pdf_gen.create_paragraph("📌 تم توليد هذا التقرير بشكل ذكي بناءً على نوع كل عمود.")
        sections.append({"title": "📎 ملاحظات ختامية", "content": note})
        return sections

    def _generate_excel(self, data: pd.DataFrame, full_path: str, config: Dict[str, Any]) -> str:
        if not isinstance(data, pd.DataFrame):
            raise TypeError("[ERROR] Excel report requires a pandas DataFrame.")
        excel_path = f"{full_path}.xlsx"
        excel_gen = ExcelReportGenerator(excel_path)
        sections = [{
            "title": "📊 البيانات",
            "paragraphs": ["تقرير Excel تم توليده تلقائيًا."],
            "tables": [{
                "headers": list(data.columns),
                "rows": data.values.tolist()
            }]
        }]
        excel_gen.generate(title=config["title"], sections=sections)
        return excel_path

    def _generate_csv(self, data: pd.DataFrame, filename: str) -> str:
        if not isinstance(data, pd.DataFrame):
            raise TypeError("[ERROR] CSV report requires a pandas DataFrame.")
        save_dataframe_to_csv(data, filename, self.output_dir)
        return os.path.join(self.output_dir, f"{filename}.csv")

    def _generate_html(self, data: pd.DataFrame, full_path: str) -> str:
        if not isinstance(data, pd.DataFrame):
            raise TypeError("[ERROR] HTML report requires a pandas DataFrame.")
        html_table = df_to_html_table(data, classes="table table-striped", index=False)
        html_path = f"{full_path}.html"
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html_table)
        return html_path


def generate_report(data: Union[pd.DataFrame, list], report_type: str = "pdf", config: Dict[str, Any] = None) -> str:
    dispatcher = ReportDispatcher()
    return dispatcher.dispatch(report_type, data, config or {})


def generate_reports(data: Union[pd.DataFrame, list], config: Dict[str, Any] = None):
    config = config or {}
    dispatcher = ReportDispatcher()
    dispatcher.dispatch("pdf", data, {
        "filename": config.get("pdf_filename", "report_pdf"),
        "title": config.get("pdf_title", "Data Report"),
        "cover_image": config.get("cover_image")
    })
    dispatcher.dispatch("excel", data, {
        "filename": config.get("excel_filename", "report_excel"),
        "title": config.get("excel_title", "Data Report")
    })
    dispatcher.dispatch("html", data, {
        "filename": config.get("html_filename", "report_html")
    })
    if config.get("include_csv", True):
        dispatcher.dispatch("csv", data, {
            "filename": config.get("csv_filename", "report_csv")
        })
