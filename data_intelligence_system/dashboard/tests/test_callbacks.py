"""
test_callbacks.py

اختبارات لوظائف callbacks في الواجهة باستخدام pytest و Dash testing.
يفترض أن يتم اختبار ردود الأفعال (callbacks) الأساسية.
"""

import pytest
from dash import Dash, html
from dashboard.callbacks import register_callbacks  # تأكد من صحة المسار والدالة

@pytest.fixture
def dash_app():
    app = Dash(__name__)
    app.layout = html.Div(id="test-div")
    register_callbacks(app)
    return app

def test_callbacks_registration(dash_app):
    """
    اختبار أن الـ callbacks مسجلة ولم تسبب أخطاء.
    """
    callbacks = dash_app.callback_map
    assert callbacks, "لم يتم تسجيل أي callback. تحقق من دالة register_callbacks."

    # مثال: التحقق من وجود callback معين (اختياري)
    # if "some-callback-output-id" in callbacks:
    #     assert True
    # else:
    #     pytest.fail("Callback 'some-callback-output-id' غير موجود.")
