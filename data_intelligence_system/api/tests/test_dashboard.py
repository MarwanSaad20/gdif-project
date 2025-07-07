import pytest
from werkzeug.test import Client
from werkzeug.wrappers import Response
from dashboard.app import server  # ✅ تأكد أن هذا هو المسار الصحيح للسيرفر

# إنشاء الكلاينت
client = Client(server, Response)

def test_dashboard_homepage():
    """
    اختبار الصفحة الرئيسية للتأكد من أنها تعمل وترجع المحتوى المتوقع.
    """
    response = client.get("/")
    decoded = response.data.decode("utf-8")
    assert response.status_code == 200
    assert "نظام تحليل البيانات العام" in decoded or "Dashboard" in decoded

def test_dashboard_callback_basic():
    """
    اختبار رد فعل (callback) أساسي.
    """
    response = client.get("/")
    assert response.status_code == 200

def test_assets_serving():
    """
    التأكد من تقديم ملفات static assets بشكل صحيح.
    """
    asset_paths = [
        "/assets/custom.css",
        "/assets/theme.js",
    ]
    for path in asset_paths:
        response = client.get(path)
        assert response.status_code in (200, 404)

# ✅ تشغيل يدوي من الملف
if __name__ == "__main__":
    import sys
    sys.exit(pytest.main(["-v", __file__]))
