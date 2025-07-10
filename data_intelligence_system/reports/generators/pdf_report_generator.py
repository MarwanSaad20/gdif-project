import os
import logging
from typing import List, Dict, Optional
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

# إعداد تسجيل الأخطاء
logging.basicConfig(level=logging.INFO)

# إعداد الخط
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
FONT_PATH = os.path.join(CURRENT_DIR, "..", "..", "fonts", "DejaVuSans.ttf")

if not os.path.exists(FONT_PATH):
    logging.warning(f"خط غير موجود: {FONT_PATH}. قد تواجه مشاكل في عرض الخطوط.")

pdfmetrics.registerFont(TTFont("DejaVu", FONT_PATH))


class PDFReportGenerator:
    """
    Generates PDF reports with titles, sections, tables, paragraphs, and optional images.
    """

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
                alignment=1,
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

    def build_pdf(self, sections: Optional[List[Dict]], cover_image_path: Optional[str] = None):
        """
        Build and save the PDF report.
        """
        if sections is None:
            logging.error("Sections list is None.")
            return

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
            title = section.get("title")
            content = section.get("content")
            images = section.get("images", [])

            if title:
                elements.append(Paragraph(title, self.custom_styles["heading"]))

            if content:
                if isinstance(content, (Paragraph, Table)):
                    elements.append(content)
                else:
                    elements.append(Paragraph(str(content), self.custom_styles["normal"]))

            for img_path in images:
                if os.path.exists(img_path):
                    elements.append(Spacer(1, 0.5 * cm))
                    elements.append(Image(img_path, width=14 * cm, height=7 * cm))
                else:
                    logging.warning(f"صورة غير موجودة: {img_path}")

            elements.append(Spacer(1, 1 * cm))

        elements.append(PageBreak())

        try:
            doc.build(elements, onFirstPage=self._add_page_number, onLaterPages=self._add_page_number)
            logging.info(f"PDF report created at: {self.output_path}")
        except Exception as e:
            logging.error(f"خطأ أثناء إنشاء ملف PDF: {e}")

    def _add_page_number(self, canvas_obj: canvas.Canvas, doc):
        """
        Add page number on each page.
        """
        page_num_text = f"Page {doc.page}"
        canvas_obj.setFont("DejaVu", 8)
        width, _ = A4
        canvas_obj.drawRightString(width - 2 * cm, 1 * cm, page_num_text)

    def create_table(self, data: List[List], col_widths: Optional[List[int]] = None) -> Table:
        """
        Create styled table from data.
        """
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
        """
        Create a paragraph with custom or default style.
        """
        style = self.custom_styles.get(style_name, self.styles["Normal"])
        return Paragraph(text, style)
