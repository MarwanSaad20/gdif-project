# tests/test_etl.py

import os
import shutil
import pytest
import pandas as pd
from pathlib import Path

from etl.extract import extract_from_path
from etl.transform import clean_data
from etl.load import save_transformed_data
from utils.data_loader import load_data

# === مسارات اختبارية ثابتة ===
TEST_SAMPLE_DIR = Path("tests/sample_data")
TEST_RAW_DATA = TEST_SAMPLE_DIR / "raw_sample.csv"
TEST_OUTPUT_DIR = Path("tests/temp_output")
TEST_PROCESSED_FILE = TEST_OUTPUT_DIR / "processed_sample.csv"

# === Fixture: إنشاء ملف بيانات خام لاختبار ETL ===
@pytest.fixture(scope="module")
def raw_test_df():
    """تهيئة بيانات خام لاختبار الاستخراج"""
    TEST_SAMPLE_DIR.mkdir(parents=True, exist_ok=True)
    df = pd.DataFrame({
        "name": ["Alice", "Bob", "Charlie", None],
        "age": [25, 30, None, 22],
        "city": ["NY", "LA", "SF", "NY"]
    })
    df.to_csv(TEST_RAW_DATA, index=False)
    return df


# === اختبار: استخراج البيانات ===
def test_extract_all_data(raw_test_df):
    """اختبار عملية الاستخراج باستخدام extract_from_path"""
    assert TEST_RAW_DATA.exists(), "❌ ملف البيانات الخام غير موجود للاختبار"
    df_extracted = extract_from_path(TEST_RAW_DATA)
    assert isinstance(df_extracted, pd.DataFrame)
    assert df_extracted.shape == raw_test_df.shape
    assert list(df_extracted.columns) == list(raw_test_df.columns)


# === اختبار: تنظيف البيانات ===
def test_clean_data(raw_test_df):
    """اختبار تنظيف البيانات"""
    df_cleaned = clean_data(df=raw_test_df)  # ✅ تمرير المعامل بالاسم
    assert isinstance(df_cleaned, pd.DataFrame)
    assert df_cleaned.isnull().sum().sum() == 0, "❌ لا تزال توجد قيم مفقودة بعد التنظيف"


# === اختبار: حفظ وتحميل البيانات ===
def test_load_data_process(raw_test_df):
    """اختبار تحميل البيانات بعد الحفظ"""
    df_cleaned = clean_data(df=raw_test_df)
    TEST_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    saved_path = save_transformed_data(
        df=df_cleaned,
        output_dir=TEST_OUTPUT_DIR,
        base_name="processed_sample",
        file_format="csv"
    )

    assert saved_path is not None and saved_path.exists(), "❌ فشل حفظ الملف المعالج"

    df_loaded = load_data(saved_path)
    assert df_loaded.equals(df_cleaned), "❌ البيانات المحمّلة لا تطابق البيانات المحفوظة"


# === Fixture: تنظيف الملفات بعد نهاية كل الاختبارات ===
@pytest.fixture(scope="module", autouse=True)
def cleanup():
    """تنظيف الملفات والمجلدات بعد تنفيذ جميع الاختبارات"""
    yield
    try:
        if TEST_RAW_DATA.exists():
            TEST_RAW_DATA.unlink()
        if TEST_PROCESSED_FILE.exists():
            TEST_PROCESSED_FILE.unlink()
        if TEST_OUTPUT_DIR.exists():
            shutil.rmtree(TEST_OUTPUT_DIR)
        if TEST_SAMPLE_DIR.exists():
            TEST_SAMPLE_DIR.rmdir()
    except Exception as e:
        print(f"⚠️ خطأ أثناء التنظيف: {e}")
