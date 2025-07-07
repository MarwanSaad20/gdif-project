import os
import pytest
import pandas as pd
from unittest.mock import patch

from api.services import reports_service


@pytest.fixture
def sample_csv(tmp_path):
    # ملف CSV بسيط للاختبار
    df = pd.DataFrame({
        "A": [1, 2, 3],
        "B": [4, 5, 6]
    })
    csv_path = tmp_path / "sample.csv"
    df.to_csv(csv_path, index=False)
    return str(csv_path)


@pytest.fixture
def sample_dfs():
    df1 = pd.DataFrame({"X": [1, 2], "Y": [3, 4]})
    df2 = pd.DataFrame({"M": [5, 6], "N": [7, 8]})
    return [df1, df2], ["Sheet1", "Sheet2"]


@patch("api.services.reports_service.load_data")
@patch("api.services.reports_service.generate_descriptive_stats")
def test_generate_html_report(mock_generate_stats, mock_load_data, sample_csv, tmp_path):
    # تهيئة البيانات المزيفة
    mock_load_data.return_value = pd.DataFrame({"A": [1, 2], "B": [3, 4]})
    mock_generate_stats.return_value = {
        "general_info": {"Number of Rows": 2, "Number of Columns": 2},
        "numeric_summary": {}
    }

    # تعديل مسارات القوالب لاستخدام مجلد مؤقت
    reports_service.TEMPLATE_DIR = str(tmp_path)
    reports_service.REPORTS_OUTPUT_DIR = str(tmp_path)

    # إنشاء قالب HTML بسيط للاختبار
    template_content = """
    <html><head><title>{{ title }}</title></head>
    <body><h1>{{ title }}</h1></body></html>
    """
    (tmp_path / "base_report.html").write_text(template_content, encoding="utf-8")

    result = reports_service.generate_summary_report(
        sample_csv,
        title="Test Report",
        output_format="html",
        output_dir=str(tmp_path)  # تمرير مجلد الإخراج بشكل صريح
    )

    expected_html_path = os.path.join(str(tmp_path), os.path.splitext(os.path.basename(sample_csv))[0] + "_report.html")

    assert result is True
    assert os.path.exists(expected_html_path)
    assert expected_html_path.endswith(".html")


def test_convert_html_to_pdf(tmp_path):
    # إنشاء ملف HTML بسيط
    html_file = tmp_path / "test_report.html"
    html_file.write_text("<html><body><h1>Test PDF</h1></body></html>", encoding="utf-8")

    reports_service.REPORTS_OUTPUT_DIR = str(tmp_path)

    # استدعاء مع تمرير output_dir بشكل صريح
    pdf_path = reports_service.convert_html_to_pdf(str(html_file), output_dir=str(tmp_path))

    assert os.path.exists(pdf_path)
    assert pdf_path.endswith(".pdf")


def test_export_to_excel(sample_dfs, tmp_path):
    dfs, sheet_names = sample_dfs
    output_filename = "test_report.xlsx"

    reports_service.REPORTS_OUTPUT_DIR = str(tmp_path)

    # استدعاء مع تمرير output_dir بشكل صريح
    output_path = reports_service.export_to_excel(dfs, sheet_names, output_filename, output_dir=str(tmp_path))

    assert os.path.exists(output_path)
    assert output_path.endswith(".xlsx")

    # تحقق من وجود أسماء الأوراق داخل ملف Excel
    xls = pd.ExcelFile(output_path)
    assert sorted(xls.sheet_names) == sorted(sheet_names)
