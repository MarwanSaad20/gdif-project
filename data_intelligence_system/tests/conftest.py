# tests/conftest.py

import sys
import os
import pytest
import pandas as pd
from fastapi.testclient import TestClient

# إضافة مجلد tests إلى sys.path لتسهيل الاستيراد المطلق داخل هذا المجلد
current_dir = os.path.dirname(__file__)
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# استيراد دوال من مجلد helpers الموجود داخل tests
from helpers.sample_data import get_sample_dataframe


# ====================================
# 🌐 Fixture: Test Client (API Client)
# ====================================
@pytest.fixture(scope="session")
def client():
    """
    عميل اختبار لاختبار endpoints في FastAPI.
    """
    from data_intelligence_system.api.app import app  # استيراد هنا لتجنب مشاكل الاستيراد المبكر
    return TestClient(app)


# ============================================
# 📄 Fixture: بيانات CSV وهمية (DataFrame صغير)
# ============================================
@pytest.fixture(scope="session")
def sample_df():
    """
    يعيد DataFrame بسيط لاستخدامه في اختبارات التحليل أو التحميل.
    """
    return get_sample_dataframe()


# ======================================
# 📂 Fixture: مسار ملف CSV وهمي مؤقت
# ======================================
@pytest.fixture(scope="session")
def sample_csv_path(tmp_path_factory, sample_df):
    """
    ينشئ ملف CSV وهمي مؤقتًا للاختبارات التي تحتاج ملف فعلي.
    """
    path = tmp_path_factory.mktemp("data") / "mock_data.csv"
    sample_df.to_csv(path, index=False)
    return str(path)


# ======================================
# 🧪 Fixture: جلسة قاعدة بيانات وهمية (اختياري)
# ======================================
@pytest.fixture(scope="session")
def fake_db_session():
    """
    جلسة قاعدة بيانات وهمية أو Mock - يمكن ربطها بمحرك SQLAlchemy لاحقًا.
    """

    class FakeDBSession:
        def query(self, *args, **kwargs):
            return []

        def close(self):
            pass

    return FakeDBSession()
