import os
import sys
import tempfile
import pandas as pd
import pytest

# ✨ تأكد من أن المسار الجذري للمشروع مضاف حتى يتم استيراد الحزم بشكل صحيح
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from data_intelligence_system.api.services.etl_service import ETLService


@pytest.fixture
def sample_csv_file():
    """
    Fixture ينشئ ملف CSV مؤقت يحتوي بيانات بسيطة مع بعض القيم المفقودة والتكرار.
    """
    df = pd.DataFrame({
        "Name": ["Ali", "Zahra", "Hussein", "Ali"],  # "Ali" مكرر لاختبار إزالة التكرار
        "Age": [25, None, 32, 25],                    # None لاختبار ملء القيم الناقصة
        "Salary": [3000, 4000, 5000, 3000]
    })

    tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".csv", mode="w", newline='', encoding="utf-8")
    try:
        df.to_csv(tmp_file.name, index=False)
    finally:
        tmp_file.close()

    yield tmp_file.name

    # إزالة الملف المؤقت بعد الانتهاء من الاختبار (مع معالجة الاستثناءات)
    try:
        os.remove(tmp_file.name)
    except FileNotFoundError:
        pass


@pytest.fixture
def temp_output_dir():
    """
    Fixture ينشئ مجلد مؤقت للإخراج ويضمن تنظيفه بعد الانتهاء.
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


def test_etl_pipeline(sample_csv_file, temp_output_dir):
    """
    اختبار تشغيل خدمة ETL على ملف CSV بسيط والتحقق من نتائج التحويل والإخراج.
    """
    etl = ETLService(config={
        "output_dir": temp_output_dir
    })

    success = etl.run_etl(
        source=sample_csv_file,
        transform_params={
            "fill_strategy": "mean",
            "encode_type": "label",
            "scale_type": "standard"
        },
        load_params={
            "output_dir": temp_output_dir,
            "file_format": "csv",
            "archive": False
        }
    )

    # تحقق من نجاح العملية
    assert success is True, "فشل تشغيل ETL بنجاح."

    # تحقق من وجود ملف الإخراج بصيغة CSV
    output_files = os.listdir(temp_output_dir)
    csv_files = [f for f in output_files if f.endswith(".csv")]
    assert len(csv_files) > 0, "لا يوجد ملفات CSV في مجلد الإخراج."

    # قراءة الملف الناتج والتحقق من محتواه
    output_path = os.path.join(temp_output_dir, csv_files[0])
    df = pd.read_csv(output_path)

    # تحقق من أن التكرارات أُزيلت وأن عدد الصفوف صحيح
    assert df.shape[0] == 3, "عدد الصفوف غير المتوقع بعد إزالة التكرارات."

    # تحقق من عدد الأعمدة (ثلاثة أعمدة متوقعة)
    assert df.shape[1] == 3, "عدد الأعمدة غير المتوقع في البيانات الناتجة."

    # تحقق من وجود الأعمدة بأسماء موحدة (صغيرة)
    expected_columns = ['name', 'age', 'salary']
    assert all(col in df.columns for col in expected_columns), f"الأعمدة المتوقعة غير موجودة: {expected_columns}"


def test_etl_invalid_source(temp_output_dir):
    """
    اختبار حالة تمرير مصدر بيانات غير موجود، يجب أن تفشل العملية بأمان.
    """
    etl = ETLService(config={
        "output_dir": temp_output_dir
    })

    # التحقق من أن run_etl إما ترفع استثناء أو ترجع False عند ملف غير موجود
    try:
        success = etl.run_etl(
            source="non_existent_file.csv",
            transform_params={},
            load_params={}
        )
    except Exception:
        pass  # الاستثناء متوقع ومقبول
    else:
        # إذا لم ترفع استثناء، يجب أن ترجع False
        assert success is False, "run_etl يجب أن تفشل أو ترجع False عند مصدر بيانات غير موجود."


# للسماح بتشغيل هذا الملف مباشرة من PyCharm أو الطرفية
if __name__ == "__main__":
    import sys
    sys.exit(pytest.main(["-v", __file__]))
