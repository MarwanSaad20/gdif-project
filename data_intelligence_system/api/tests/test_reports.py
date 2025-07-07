# api/tests/test_reports.py

import os
import tempfile
import pandas as pd
import pytest

from data_intelligence_system.api.services.reports_service import ReportsService


@pytest.fixture
def sample_report_data():
    """
    إنشاء ملف CSV مؤقت يحتوي بيانات بسيطة
    """
    df = pd.DataFrame({
        "feature_1": [10, 20, 30, 40, 50],
        "feature_2": [5, 15, 25, 35, 45],
        "category": ["A", "B", "A", "B", "A"]
    })

    tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".csv", mode='w', encoding='utf-8', newline='')
    try:
        df.to_csv(tmp_file.name, index=False)
    finally:
        tmp_file.close()  # مهم: إغلاق الملف قبل الاستعمال في الاختبار
    yield tmp_file.name
    # إزالة الملف المؤقت بأمان مع التعامل مع أي استثناء
    try:
        os.remove(tmp_file.name)
    except FileNotFoundError:
        pass


@pytest.fixture
def temp_output_dir():
    """
    مجلد مؤقت لتخزين التقرير الناتج
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


def test_generate_report_outputs_file(sample_report_data, temp_output_dir):
    """
    اختبار توليد تقرير باستخدام ReportsService مع تحقق موسع
    """
    service = ReportsService()

    # تحقق من وجود ملف القالب الأساسي بصيغته الجديدة (HTML)
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    template_path = os.path.join(base_dir, "reports", "templates", "base_report.html")
    assert os.path.exists(template_path), f"❌ ملف القالب غير موجود: {template_path}"

    result = service.generate_summary_report(
        file_path=sample_report_data,
        output_dir=temp_output_dir,
        output_format="html",  # يمكن تغييره إلى "pdf" أو "excel" لاختبار أنواع أخرى
        title="Test Report"
    )

    # تأكد من نجاح العملية
    assert result is True

    # تحقق من وجود تقرير HTML في المجلد المؤقت
    output_files = os.listdir(temp_output_dir)
    html_files = [f for f in output_files if f.endswith(".html")]
    assert len(html_files) > 0, "❌ لم يتم توليد أي ملف HTML."

    # تحقق من محتوى التقرير (يقرأ الملف ويتأكد من وجود العنوان)
    output_path = os.path.join(temp_output_dir, html_files[0])
    with open(output_path, 'r', encoding='utf-8') as f:
        content = f.read()
    assert "Test Report" in content, "❌ العنوان المتوقع غير موجود في التقرير."


@pytest.mark.parametrize("output_format", ["html", "pdf", "excel"])
def test_generate_report_different_formats(sample_report_data, temp_output_dir, output_format):
    """
    اختبار توليد تقارير بصيغ مختلفة (HTML, PDF, Excel)
    """
    service = ReportsService()

    result = service.generate_summary_report(
        file_path=sample_report_data,
        output_dir=temp_output_dir,
        output_format=output_format,
        title=f"Test Report {output_format.upper()}"
    )

    assert result is True, f"❌ فشل توليد تقرير بصيغة {output_format}"

    # تحقق من وجود ملف الإخراج المناسب للصيغة
    output_files = os.listdir(temp_output_dir)
    ext_map = {"html": ".html", "pdf": ".pdf", "excel": ".xlsx"}
    expected_ext = ext_map.get(output_format, ".html")
    matched_files = [f for f in output_files if f.endswith(expected_ext)]
    assert len(matched_files) > 0, f"❌ لم يتم توليد ملف بصيغة {expected_ext}"


def test_generate_report_with_invalid_path(temp_output_dir):
    """
    اختبار التعامل مع مسار خاطئ للملف
    """
    service = ReportsService()

    result = service.generate_summary_report(
        file_path="invalid/path/to/data.csv",
        output_dir=temp_output_dir,
        output_format="html"
    )

    # يجب أن يفشل بلطف ولا يسبب كسرًا في التنفيذ
    assert result is False or result is None
