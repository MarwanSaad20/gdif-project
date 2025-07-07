import pytest
from fastapi.testclient import TestClient
from api.main import app  # تأكد من أن app موجود هنا أو استورد من ملف FastAPI الرئيسي

client = TestClient(app)


def test_unauthorized_access():
    """اختبار الوصول إلى Endpoint محمي بدون JWT"""
    response = client.get("/secure-endpoint")  # يجب أن يكون محمي بـ Depends(get_current_user)
    assert response.status_code == 401
    assert "Unauthorized" in response.text or "Missing" in response.text


def test_forbidden_access():
    """اختبار الوصول بمفتاح API غير مصرح"""
    headers = {"X-API-Key": "invalid-key"}
    response = client.get("/secure-endpoint", headers=headers)
    assert response.status_code == 401 or response.status_code == 403
    assert "Unauthorized" in response.text or "Forbidden" in response.text


def test_not_found_route():
    """اختبار الوصول إلى مسار غير موجود"""
    response = client.get("/non-existent-route")
    assert response.status_code == 404
    assert "Not Found" in response.text or "message" in response.json()


def test_internal_server_error_handling(monkeypatch):
    """اختبار توليد خطأ داخلي 500 داخل أحد المسارات"""

    # استخدم monkeypatch لتعطيل دالة وإجبار استثناء
    def raise_exception(*args, **kwargs):
        raise Exception("💥 خلل داخلي تجريبي")

    # لنفترض وجود دالة في خدمة اسمها compute_statistics نكسرها
    from analysis import descriptive_stats
    monkeypatch.setattr(descriptive_stats, "compute_statistics", raise_exception)

    path = "data/processed/clean_data.csv"  # تأكد من وجود هذا الملف
    response = client.get(f"/generate-report?file_path={path}")

    assert response.status_code == 500
    assert "Internal Server Error" in response.text or "message" in response.json()
