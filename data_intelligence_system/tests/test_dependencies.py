import pytest
from fastapi import Depends, HTTPException, status
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from api.main import app  # استورد التطبيق الرئيسي
from api.utils.dependencies import get_db, get_current_user, verify_api_key

# client للاختبار
client = TestClient(app)


# ========== 🔧 اختبار تبعية قاعدة البيانات ==========
def test_get_db_session_returns_session():
    """تأكد من أن get_db تعيد جلسة قاعدة بيانات صالحة"""
    db = None
    try:
        generator = get_db()
        db = next(generator)
        assert isinstance(db, Session)
    finally:
        if db:
            db.close()


# ========== 🔐 اختبار استخراج المستخدم الحالي ==========
def test_get_current_user_unauthorized():
    """يجب أن يرفض الطلبات بدون Authorization"""
    response = client.get("/secure-endpoint")  # مسار وهمي محمي بـ Depends(get_current_user)
    assert response.status_code == 401


# ========== 🧾 اختبار مفتاح API ==========
def test_verify_api_key_valid(monkeypatch):
    """تمرير مفتاح صالح واختبار القبول"""
    from api.utils.dependencies import verify_api_key

    # مؤقتًا نمرر مفتاح صالح
    class DummyRequest:
        headers = {"X-API-Key": "supersecretkey"}

    result = verify_api_key(DummyRequest())
    assert result == "supersecretkey"


def test_verify_api_key_invalid():
    """عدم تمرير المفتاح أو تمرير مفتاح خاطئ"""
    from api.utils.dependencies import verify_api_key

    class DummyRequest:
        headers = {"X-API-Key": "invalid"}

    with pytest.raises(HTTPException) as exc_info:
        verify_api_key(DummyRequest())

    assert exc_info.value.status_code in [401, 403]
    assert "Invalid API Key" in str(exc_info.value.detail)
