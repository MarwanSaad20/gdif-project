from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
)
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os
from typing import List, Dict, Optional

# تعيين مسار الخط بطريقة ديناميكية بناء على موقع هذا الملف
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
FONT_PATH = os.path.join(CURRENT_DIR, "..", "..", "fonts", "DejaVuSans.ttf")

if not os.path.exists(FONT_PATH):
    print(f"⚠️ خط غير موجود: {FONT_PATH}. قد تواجه مشاكل في عرض الخطوط.")

# تسجيل خط DejaVu لتفادي مشكلة المربعات
pdfmetrics.registerFont(TTFont("DejaVu", FONT_PATH))


class PDFReportGenerator:
    def __init__(self, output_path: str, title: str = "Data Report"):
        self.output_path = output_path
        self.title = title
        self.styles = getSampleStyleSheet()
        self.custom_styles = {
            "title": ParagraphStyle(
                "Title",
                parent=self.styles["Heading1"],
                fontName="DejaVu",
                fontSize=24,
                alignment=1,  # Centered
                spaceAfter=20,
                textColor=colors.HexColor("#003366"),
            ),
            "heading": ParagraphStyle(
                "Heading2",
                parent=self.styles["Heading2"],
                fontName="DejaVu",
                fontSize=16,
                spaceBefore=12,
                spaceAfter=12,
                textColor=colors.HexColor("#003366"),
            ),
            "normal": ParagraphStyle(
                "Normal",
                fontName="DejaVu",
                fontSize=10,
                leading=14,
                spaceAfter=6,
            ),
            "footer": ParagraphStyle(
                "Footer",
                fontSize=8,
                alignment=1,
                textColor=colors.grey,
                fontName="DejaVu"
            )
        }

    def build_pdf(self, sections: List[Dict], cover_image_path: Optional[str] = None):
        os.makedirs(os.path.dirname(self.output_path), exist_ok=True)

        doc = SimpleDocTemplate(
            self.output_path,
            pagesize=A4,
            rightMargin=2 * cm,
            leftMargin=2 * cm,
            topMargin=2 * cm,
            bottomMargin=2 * cm
        )
        elements = []

        if cover_image_path and os.path.exists(cover_image_path):
            elements.append(Image(cover_image_path, width=16 * cm, height=9 * cm))
            elements.append(Spacer(1, 1 * cm))

        elements.append(Paragraph(self.title, self.custom_styles["title"]))
        elements.append(Spacer(1, 1 * cm))

        for section in sections:
            if "title" in section:
                elements.append(Paragraph(section["title"], self.custom_styles["heading"]))
            if "content" in section:
                if isinstance(section["content"], (Paragraph, Table)):
                    elements.append(section["content"])
                else:
                    elements.append(Paragraph(str(section["content"]), self.custom_styles["normal"]))
            if "images" in section:
                for img_path in section["images"]:
                    if os.path.exists(img_path):
                        elements.append(Spacer(1, 0.5 * cm))
                        elements.append(Image(img_path, width=14 * cm, height=7 * cm))
                    else:
                        print(f"⚠️ صورة غير موجودة: {img_path}")
            elements.append(Spacer(1, 1 * cm))

        elements.append(PageBreak())

        try:
            doc.build(elements, onFirstPage=self._add_page_number, onLaterPages=self._add_page_number)
            print(f"[INFO] PDF report created at: {self.output_path}")
        except Exception as e:
            print(f"❌ خطأ أثناء إنشاء ملف PDF: {e}")

    def _add_page_number(self, canvas_obj, doc):
        page_num_text = f"Page {doc.page}"
        canvas_obj.setFont("DejaVu", 8)
        width, height = A4
        canvas_obj.drawRightString(width - 2 * cm, 1 * cm, page_num_text)

    def create_table(self, data: List[List], col_widths: Optional[List[int]] = None) -> Table:
        table = Table(data, colWidths=col_widths)
        style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#003366")),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), 'DejaVu'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ])
        table.setStyle(style)
        return table

    def create_paragraph(self, text: str, style_name: str = "normal") -> Paragraph:
        style = self.custom_styles.get(style_name, self.styles["Normal"])
        return Paragraph(text, style)


# === Example Test ===
if __name__ == "__main__":
    pdf_path = "reports/output/report_sample_en.pdf"
    pdf_gen = PDFReportGenerator(pdf_path, "Exploratory Data Report")

    data = [
        ["Feature", "Value"],
        ["Row Count", "1500"],
        ["Column Count", "12"],
        ["Missing Value Rate", "3.4%"]
    ]

    sections = [
        {
            "title": "Data Summary",
            "content": pdf_gen.create_table(data)
        },
        {
            "title": "Notes",
            "content": pdf_gen.create_paragraph(
                "This report was generated using the ReportLab library. It includes tables, structured text, and optional images."
            )
        }
    ]

    pdf_gen.build_pdf(sections)
