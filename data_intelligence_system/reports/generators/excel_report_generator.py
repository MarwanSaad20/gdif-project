import os
import uuid
import openpyxl
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.table import Table, TableStyleInfo
from datetime import datetime
from typing import List, Dict, Optional


class ExcelReportGenerator:
    def __init__(self, filename: str):
        """
        إنشاء تقرير Excel جديد.
        :param filename: مسار واسم ملف الإكسل الناتج (.xlsx)
        """
        self.filename = filename
        self.wb = openpyxl.Workbook()
        # نحذف الورقة الافتراضية لأننا سننشئ أوراق حسب الأقسام
        default_sheet = self.wb.active
        self.wb.remove(default_sheet)

    def _set_column_widths(self, ws, widths: Dict[int, int]):
        """
        تعيين عرض أعمدة مخصص.
        :param ws: ورقة العمل
        :param widths: dict {col_index: width}
        """
        for col_idx, width in widths.items():
            col_letter = get_column_letter(col_idx)
            ws.column_dimensions[col_letter].width = width

    def _apply_header_style(self, cell):
        """
        تنسيق خلايا العنوان.
        """
        cell.font = Font(bold=True, size=14, color="FFFFFF")
        cell.fill = PatternFill("solid", fgColor="0D6EFD")  # أزرق Bootstrap
        cell.alignment = Alignment(horizontal="center", vertical="center")

    def _apply_section_title_style(self, cell):
        """
        تنسيق عنوان القسم.
        """
        cell.font = Font(bold=True, size=12, color="0D6EFD")
        cell.alignment = Alignment(horizontal="left", vertical="center")

    def _apply_table_header_style(self, cell):
        """
        تنسيق رؤوس الجداول.
        """
        cell.font = Font(bold=True, color="FFFFFF")
        cell.fill = PatternFill("solid", fgColor="0D6EFD")
        cell.alignment = Alignment(horizontal="center", vertical="center")
        thin_border = Border(
            left=Side(style='thin'), right=Side(style='thin'),
            top=Side(style='thin'), bottom=Side(style='thin')
        )
        cell.border = thin_border

    def _apply_table_cell_style(self, cell):
        """
        تنسيق خلايا بيانات الجدول.
        """
        cell.alignment = Alignment(horizontal="left", vertical="center")
        thin_border = Border(
            left=Side(style='thin'), right=Side(style='thin'),
            top=Side(style='thin'), bottom=Side(style='thin')
        )
        cell.border = thin_border

    def _write_section(self, ws, start_row: int, section: Dict) -> int:
        """
        كتابة قسم مع عنوانه ومحتواه (جداول أو نصوص).
        :param ws: ورقة العمل
        :param start_row: بداية كتابة القسم في هذا الصف
        :param section: dict يحتوي على:
            - title: عنوان القسم
            - tables: قائمة جداول، كل جدول dict:
                - headers: list من العناوين
                - rows: list من القوائم (الصفوف)
            - paragraphs: قائمة نصوص (اختياري)
        :return: رقم الصف التالي بعد كتابة القسم
        """
        row = start_row

        # كتابة عنوان القسم
        title_cell = ws.cell(row=row, column=1, value=section.get("title", ""))
        self._apply_section_title_style(title_cell)
        ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=10)
        row += 2

        # كتابة الفقرات النصية مع دعم اتجاه النص العربي (يمين لليسار)
        paragraphs = section.get("paragraphs", [])
        for para in paragraphs:
            para_cell = ws.cell(row=row, column=1, value=para)
            para_cell.alignment = Alignment(wrap_text=True, vertical="top", horizontal="right")
            ws.row_dimensions[row].height = 30
            row += 1
        if paragraphs:
            row += 1

        # كتابة الجداول
        tables = section.get("tables", [])
        for table_idx, table in enumerate(tables):
            headers = table.get("headers", [])
            rows_data = table.get("rows", [])

            # كتابة رؤوس الجدول
            for col_idx, header in enumerate(headers, start=1):
                cell = ws.cell(row=row, column=col_idx, value=header)
                self._apply_table_header_style(cell)

            row += 1

            # كتابة بيانات الجدول
            for row_data in rows_data:
                for col_idx, value in enumerate(row_data, start=1):
                    cell = ws.cell(row=row, column=col_idx, value=value)
                    self._apply_table_cell_style(cell)
                row += 1

            # إضافة جدول رسمي Excel لسهولة الفلترة والترتيب
            if headers and rows_data:
                table_range = f"A{row - len(rows_data) -1}:{get_column_letter(len(headers))}{row - 1}"
                # اسم جدول فريد لتجنب التكرار
                table_id = uuid.uuid4().hex[:8]
                tab = Table(displayName=f"Table_{start_row}_{table_idx}_{table_id}", ref=table_range)
                style = TableStyleInfo(
                    name="TableStyleMedium9",
                    showFirstColumn=False,
                    showLastColumn=False,
                    showRowStripes=True,
                    showColumnStripes=False
                )
                tab.tableStyleInfo = style
                ws.add_table(tab)

            row += 2  # مسافة بعد كل جدول

        return row

    def generate(self, title: str, sections: List[Dict], author: Optional[str] = None):
        """
        توليد التقرير وحفظه.
        :param title: عنوان التقرير العام (يستخدم كاسم الورقة الأولى)
        :param sections: قائمة أقسام، كل قسم dict:
            - title: عنوان القسم
            - paragraphs: [نصوص]
            - tables: [جداول]
        :param author: اسم المؤلف (اختياري)
        """
        # ضمان وجود المجلد لحفظ التقرير
        os.makedirs(os.path.dirname(self.filename), exist_ok=True)

        # إعداد بيانات الوثيقة
        if author:
            self.wb.properties.creator = author
        self.wb.properties.title = title
        self.wb.properties.created = datetime.now()

        # إنشاء ورقة جديدة بعنوان التقرير
        ws = self.wb.create_sheet(title=title[:31])  # اسم الورقة max 31 حرف

        # إضافة رأس التقرير
        ws.merge_cells("A1:J1")
        header_cell = ws["A1"]
        header_cell.value = title
        self._apply_header_style(header_cell)
        ws.row_dimensions[1].height = 30

        current_row = 3

        # تعيين أعمدة عريضة بشكل مبدئي (يمكن تعديله حسب الحاجة)
        self._set_column_widths(ws, {
            1: 25,
            2: 20,
            3: 20,
            4: 20,
            5: 20,
            6: 20,
            7: 20,
            8: 20,
            9: 20,
            10: 20,
        })

        # كتابة الأقسام
        for section in sections:
            current_row = self._write_section(ws, current_row, section)

        # حفظ الملف مع معالجة الأخطاء
        try:
            self.wb.save(self.filename)
            print(f"تم إنشاء تقرير Excel وحفظه في: {self.filename}")
        except Exception as e:
            print(f"خطأ أثناء حفظ ملف الإكسل: {e}")
