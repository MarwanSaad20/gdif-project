import os
import tempfile
import pandas as pd
import pytest

from data_intelligence_system.analysis.descriptive_stats import generate_descriptive_stats


@pytest.fixture
def sample_dataframe_file():
    """
    Fixture لإنشاء ملف CSV مؤقت يحتوي بيانات اختبار.
    يستخدم NamedTemporaryFile مع delete=False للتحكم بالحذف يدويًا بعد الانتهاء.
    """
    df = pd.DataFrame({
        "age": [25, 30, 35, 40, 45],
        "salary": [3000, 4000, 5000, 6000, 7000],
        "gender": ["M", "F", "M", "F", "M"]
    })

    with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as tmp_file:
        df.to_csv(tmp_file.name, index=False)
        tmp_filename = tmp_file.name

    yield tmp_filename

    # تأكد من حذف الملف بعد انتهاء الاختبار (مع معالجة مشاكل Windows)
    try:
        os.remove(tmp_filename)
    except PermissionError:
        import time
        time.sleep(0.1)
        os.remove(tmp_filename)


@pytest.fixture
def temp_output_dir():
    """
    Fixture لإنشاء مجلد مؤقت لتخزين مخرجات التحليل.
    يغلق ويحذف المجلد تلقائياً بعد الانتهاء.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


def test_generate_descriptive_stats_creates_output(sample_dataframe_file, temp_output_dir):
    """
    اختبار أن دالة التحليل تولد ملفات النتائج المتوقعة:
    ملفات CSV للإحصائيات وملفات PNG للرسوم البيانية.
    """
    generate_descriptive_stats(sample_dataframe_file, output_dir=temp_output_dir)

    base_filename = os.path.basename(sample_dataframe_file).replace(".csv", "")

    # تحقق من وجود ملف إحصائيات الأعمدة الرقمية
    numeric_stats_file = os.path.join(temp_output_dir, f"{base_filename}_numeric_stats.csv")
    assert os.path.exists(numeric_stats_file), "ملف إحصائيات الأعمدة الرقمية غير موجود"

    # تحقق من وجود ملف تكرار القيم للعمود الفئوي 'gender'
    expected_value_count_file = os.path.join(temp_output_dir, f"{base_filename}_value_counts_gender.csv")
    assert os.path.exists(expected_value_count_file), "ملف تكرار القيم للعمود 'gender' غير موجود"

    # تحقق من وجود ملفات PNG تحتوي على كلمة "distribution" في اسمها
    plots = [f for f in os.listdir(temp_output_dir) if f.endswith(".png")]
    assert any("distribution" in f for f in plots), "لا توجد صور رسوم بيانية محفوظة تتضمن كلمة 'distribution'"


# --- تحسينات مقترحة (اختياري):

@pytest.mark.parametrize("invalid_file", ["", "non_existent.csv"])
def test_generate_descriptive_stats_with_invalid_file(invalid_file, temp_output_dir):
    """
    اختبار أن دالة التحليل ترفع استثناء عند ملف غير صالح أو غير موجود.
    """
    with pytest.raises(Exception):
        generate_descriptive_stats(invalid_file, output_dir=temp_output_dir)


def test_generated_files_content(sample_dataframe_file, temp_output_dir):
    """
    اختبار بسيط لقراءة ملف الإحصائيات الرقمية والتأكد من احتوائه على أعمدة متوقعة.
    """
    generate_descriptive_stats(sample_dataframe_file, output_dir=temp_output_dir)
    base_filename = os.path.basename(sample_dataframe_file).replace(".csv", "")
    numeric_stats_file = os.path.join(temp_output_dir, f"{base_filename}_numeric_stats.csv")

    df_stats = pd.read_csv(numeric_stats_file)
    # تأكد من وجود أعمدة إحصائية مهمة مثل 'mean' أو 'std'
    assert "mean" in df_stats.columns, "ملف إحصائيات الأعمدة الرقمية يفتقد عمود 'mean'"
    assert "std" in df_stats.columns, "ملف إحصائيات الأعمدة الرقمية يفتقد عمود 'std'"

