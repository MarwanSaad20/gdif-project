import shutil
import pytest
import pandas as pd
from pathlib import Path

from data_intelligence_system.etl.extract import extract_file
from data_intelligence_system.etl.transform import clean_data
from data_intelligence_system.etl.load import save_transformed_data
from data_intelligence_system.utils.data_loader import load_data


@pytest.fixture(scope="function")
def raw_test_df(tmp_path):
    """تهيئة بيانات خام لاختبار ETL في مجلد مؤقت"""
    csv_path = tmp_path / "raw_sample.csv"
    df = pd.DataFrame({
        "name": ["Alice", "Bob", "Charlie", None],
        "age": [25, 30, None, 22],
        "city": ["NY", "LA", "SF", "NY"]
    })
    df.to_csv(csv_path, index=False)
    return df, csv_path


def test_extract_all_data(raw_test_df):
    """اختبار عملية الاستخراج باستخدام extract_file"""
    df_expected, csv_path = raw_test_df
    assert csv_path.exists(), "❌ ملف البيانات الخام غير موجود للاختبار"
    extracted_dict = extract_file(csv_path)
    assert isinstance(extracted_dict, dict)
    key = csv_path.stem
    assert key in extracted_dict
    df_extracted = extracted_dict[key]
    assert isinstance(df_extracted, pd.DataFrame)
    assert df_extracted.shape == df_expected.shape
    assert list(df_extracted.columns) == list(df_expected.columns)


def test_clean_data(raw_test_df):
    """اختبار تنظيف البيانات"""
    df_raw, _ = raw_test_df
    df_cleaned = clean_data(df=df_raw)  # ✅ تمرير المعامل بالاسم
    assert isinstance(df_cleaned, pd.DataFrame)
    assert df_cleaned.isnull().sum().sum() == 0, "❌ لا تزال توجد قيم مفقودة بعد التنظيف"


def test_save_and_load_data(tmp_path, raw_test_df):
    """اختبار حفظ البيانات المعالجة ثم تحميلها والتأكد من التطابق"""
    df_raw, _ = raw_test_df
    df_cleaned = clean_data(df=df_raw)

    output_dir = tmp_path / "output"
    output_dir.mkdir(parents=True, exist_ok=True)

    saved_path = save_transformed_data(
        df=df_cleaned,
        output_dir=output_dir,
        base_name="processed_sample",
        file_format="csv"
    )

    assert saved_path is not None and saved_path.exists(), "❌ فشل حفظ الملف المعالج"

    df_loaded = load_data(saved_path)
    pd.testing.assert_frame_equal(df_loaded, df_cleaned, check_dtype=False)


@pytest.mark.parametrize("invalid_path", [
    "non_existent_file.csv",
    "/path/to/nowhere/data.csv"
])
def test_extract_raises_file_not_found(invalid_path):
    """اختبار رفع استثناء عند محاولة استخراج بيانات من مسار غير موجود"""
    with pytest.raises(FileNotFoundError):
        extract_file(invalid_path)


def test_clean_data_handles_empty_df():
    """اختبار تنظيف بيانات فارغة"""
    empty_df = pd.DataFrame(columns=["name", "age", "city"])
    df_cleaned = clean_data(df=empty_df)
    assert df_cleaned.empty, "❌ التنظيف لم يرجع DataFrame فارغ كما هو متوقع"


@pytest.fixture(scope="function", autouse=True)
def cleanup_tmp_dir(tmp_path):
    """تنظيف الملفات بعد كل اختبار - يتم تلقائيًا باستخدام tmp_path فلا حاجة لعمل إضافي"""
    yield
    # لا حاجة لتنظيف هنا لأن tmp_path يدير ذلك تلقائيًا
