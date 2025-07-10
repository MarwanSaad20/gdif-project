import os
import logging
from typing import Dict, Any, Union
import pandas as pd
import numpy as np

# استيراد من جذر المشروع مع المسار الكامل
from data_intelligence_system.reports.generators.pdf_report_generator import PDFReportGenerator
from data_intelligence_system.reports.export_utils import (
    save_dataframe_to_excel,
    save_dataframe_to_csv,
    df_to_html_table
)
from data_intelligence_system.reports.report_config import OUTPUT_PATH

logging.basicConfig(level=logging.INFO)


def ensure_dir(path: str):
    if not os.path.exists(path):
        os.makedirs(path)


class ReportDispatcher:
    def __init__(self, output_dir: str = OUTPUT_PATH):
        self.output_dir = output_dir
        ensure_dir(self.output_dir)

    def dispatch(self, report_type: str, data: Union[pd.DataFrame, list], config: Dict[str, Any] = None) -> str:
        config = config or {}
        filename = config.get("filename", "report")
        full_path = os.path.join(self.output_dir, filename)

        if report_type == "pdf":
            return self._generate_pdf(data, full_path, config)

        elif report_type == "excel":
            if not isinstance(data, pd.DataFrame):
                raise TypeError("[ERROR] Excel report requires a pandas DataFrame.")
            save_dataframe_to_excel(data, filename, self.output_dir)
            return f"{full_path}.xlsx"

        elif report_type == "csv":
            if not isinstance(data, pd.DataFrame):
                raise TypeError("[ERROR] CSV report requires a pandas DataFrame.")
            save_dataframe_to_csv(data, filename, self.output_dir)
            return f"{full_path}.csv"

        elif report_type == "html":
            if not isinstance(data, pd.DataFrame):
                raise TypeError("[ERROR] HTML report requires a pandas DataFrame.")
            html_table = df_to_html_table(data, classes="table table-striped", index=False)
            html_path = f"{full_path}.html"
            with open(html_path, "w", encoding="utf-8") as f:
                f.write(html_table)
            return html_path

        else:
            raise ValueError(f"[ERROR] Unsupported report type: '{report_type}'")

    def _generate_pdf(self, data: Union[pd.DataFrame, list], full_path: str, config: Dict[str, Any]) -> str:
        pdf_path = f"{full_path}.pdf"
        title = config.get("title", "Data Report")
        cover_image = config.get("cover_image")
        pdf_gen = PDFReportGenerator(pdf_path, title=title)

        if isinstance(data, list):
            pdf_gen.build_pdf(data, cover_image_path=cover_image)
            return pdf_path

        if not isinstance(data, pd.DataFrame):
            raise TypeError("[ERROR] PDF report requires a DataFrame or pre-built sections list.")

        sections = []
        df = data.copy()

        preview_data = [list(df.columns)] + df.head(10).values.tolist()
        preview_table = pdf_gen.create_table(preview_data)
        sections.append({"title": "📋 معاينة أولية للبيانات", "content": preview_table})

        for col in df.columns:
            series = df[col]
            section_title = f"🔎 تحليل العمود: {col}"

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

            sections.append({"title": section_title, "content": content})

        note = pdf_gen.create_paragraph("📌 تم توليد هذا التقرير بشكل ذكي بناءً على نوع كل عمود.")
        sections.append({"title": "📎 ملاحظات ختامية", "content": note})

        pdf_gen.build_pdf(sections, cover_image_path=cover_image)
        logging.info(f"PDF report created at: {pdf_path}")
        return pdf_path


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
        "filename": config.get("excel_filename", "report_excel")
    })

    dispatcher.dispatch("html", data, {
        "filename": config.get("html_filename", "report_html")
    })

    if config.get("include_csv", True):
        dispatcher.dispatch("csv", data, {
            "filename": config.get("csv_filename", "report_csv")
        })
