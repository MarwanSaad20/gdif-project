import pytest
import pandas as pd
from unittest.mock import patch
from pathlib import Path

from data_intelligence_system.api.services import reports_service


@pytest.fixture
def sample_csv(tmp_path: Path) -> Path:
    """إنشاء ملف CSV مؤقت للاختبار."""
    df = pd.DataFrame({
        "A": [1, 2, 3],
        "B": [4, 5, 6]
    })
    csv_path = tmp_path / "sample.csv"
    df.to_csv(csv_path, index=False)
    return csv_path


@pytest.fixture
def sample_dfs():
    """إنشاء قائمة DataFrames وأسماء أوراق لاختبار تصدير Excel."""
    df1 = pd.DataFrame({"X": [1, 2], "Y": [3, 4]})
    df2 = pd.DataFrame({"M": [5, 6], "N": [7, 8]})
    return [df1, df2], ["Sheet1", "Sheet2"]


@patch("data_intelligence_system.api.services.reports_service.load_data")
@patch("data_intelligence_system.api.services.reports_service.generate_descriptive_stats")
def test_generate_html_report(mock_generate_stats, mock_load_data, sample_csv: Path, tmp_path: Path):
    """
    اختبار توليد تقرير HTML.
    يتحقق من أن التقرير يتم إنشاؤه وحفظه في المسار المتوقع.
    """
    mock_load_data.return_value = pd.DataFrame({"A": [1, 2], "B": [3, 4]})
    mock_generate_stats.return_value = {
        "general_info": {"Number of Rows": 2, "Number of Columns": 2},
        "numeric_summary": {}
    }

    # إعداد مجلدات القوالب والإخراج المؤقتة
    reports_service.TEMPLATE_DIR = tmp_path
    reports_service.REPORTS_OUTPUT_DIR = tmp_path

    # إنشاء قالب HTML بسيط مؤقت للاختبار
    template_content = """
    <html><head><title>{{ title }}</title></head>
    <body><h1>{{ title }}</h1></body></html>
    """
    (tmp_path / "base_report.html").write_text(template_content, encoding="utf-8")

    result = reports_service.generate_summary_report(
        str(sample_csv),
        title="Test Report",
        output_format="html",
        output_dir=tmp_path  # تمرير Path وليس str
    )

    expected_html_path = tmp_path / f"{sample_csv.stem}_report.html"

    assert result is True
    assert expected_html_path.exists()
    assert expected_html_path.suffix == ".html"


def test_convert_html_to_pdf(tmp_path: Path):
    """
    اختبار تحويل ملف HTML إلى PDF.
    يتحقق من وجود ملف PDF الناتج في المسار المتوقع.
    """
    html_file = tmp_path / "test_report.html"
    html_file.write_text("<html><body><h1>Test PDF</h1></body></html>", encoding="utf-8")

    reports_service.REPORTS_OUTPUT_DIR = tmp_path

    pdf_path = reports_service.convert_html_to_pdf(str(html_file), output_dir=tmp_path)

    assert pdf_path and Path(pdf_path).exists()
    assert Path(pdf_path).suffix == ".pdf"


@pytest.mark.parametrize("invalid_html", ["", "non_existent_file.html"])
def test_convert_html_to_pdf_invalid(invalid_html):
    """
    اختبار تحويل HTML إلى PDF مع ملف HTML غير موجود أو غير صالح.
    يجب أن ترجع الدالة None أو False عند المدخلات غير الصالحة.
    """
    result = reports_service.convert_html_to_pdf(invalid_html)
    assert result in (None, False)


def test_export_to_excel(sample_dfs, tmp_path: Path):
    """
    اختبار تصدير بيانات متعددة إلى ملف Excel مع أوراق متعددة.
    يتحقق من أن الملف تم إنشاؤه ويحتوي على الأوراق المطلوبة.
    """
    dfs, sheet_names = sample_dfs
    output_filename = "test_report.xlsx"

    reports_service.REPORTS_OUTPUT_DIR = tmp_path

    output_path = reports_service.export_to_excel(dfs, sheet_names, output_filename, output_dir=tmp_path)

    assert output_path and Path(output_path).exists()
    assert Path(output_path).suffix == ".xlsx"

    xls = pd.ExcelFile(output_path)
    assert sorted(xls.sheet_names) == sorted(sheet_names)


@pytest.mark.parametrize("empty_dfs", [([], []), (None, None)])
def test_export_to_excel_empty(empty_dfs):
    """
    اختبار تصدير Excel مع بيانات فارغة.
    يجب أن تتعامل الدالة مع القوائم الفارغة أو None بشكل آمن.
    """
    dfs, sheets = empty_dfs
    try:
        result = reports_service.export_to_excel(dfs, sheets, "empty.xlsx")
    except Exception:
        result = False
    # قد ترجع مسار، أو False، أو ترفع استثناء => نتحقق أنها لا ترجع مسار لملف فعلي
    assert result is False or result is None or not (isinstance(result, (str, Path)) and Path(result).exists())
