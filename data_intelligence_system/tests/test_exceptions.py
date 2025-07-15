# tests/test_exceptions.py

import pytest
from fastapi import Request
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.datastructures import URL
from unittest.mock import AsyncMock, MagicMock

from data_intelligence_system.api.utils.exceptions import (
    CustomAppException,
    FileNotFoundAppException,
    AnalysisFailedException,
    AuthFailedException,
    json_error_response,
    custom_exception_handler,
    validation_exception_handler,
    http_exception_handler,
    general_exception_handler
)


@pytest.mark.asyncio
async def test_custom_app_exception_properties():
    exc = CustomAppException("خطأ مخصص", status_code=418)
    assert exc.message == "خطأ مخصص"
    assert exc.status_code == 418
    assert str(exc) == "خطأ مخصص"

def test_file_not_found_app_exception_message_and_code():
    filename = "data.csv"
    exc = FileNotFoundAppException(filename)
    assert "الملف غير موجود" in exc.message
    assert filename in exc.message
    assert exc.status_code == 404

def test_analysis_failed_exception_default_message_and_code():
    exc = AnalysisFailedException()
    assert "فشل التحليل" in exc.message
    assert exc.status_code == 500

def test_auth_failed_exception_message_and_code():
    exc = AuthFailedException()
    assert "المصادقة فشلت" in exc.message
    assert exc.status_code == 401

def test_json_error_response_basic():
    mock_request = MagicMock()
    mock_request.url = URL("http://testserver/api/resource")
    response = json_error_response(
        request=mock_request,
        status_code=400,
        detail="رسالة خطأ",
        errors=None
    )
    assert response.status_code == 400
    content = response.body.decode()
    assert "رسالة خطأ" in content
    assert "error" in content
    assert str(mock_request.url) in content

@pytest.mark.asyncio
async def test_custom_exception_handler_returns_expected_json():
    mock_request = MagicMock()
    mock_request.url = URL("http://testserver/api/custom_error")
    exc = CustomAppException("مشكلة مخصصة", status_code=409)

    response = await custom_exception_handler(mock_request, exc)
    assert response.status_code == 409
    content = response.body.decode()
    assert "مشكلة مخصصة" in content
    assert "error" in content
    assert str(mock_request.url) in content

@pytest.mark.asyncio
async def test_validation_exception_handler_returns_422_with_errors():
    mock_request = MagicMock()
    mock_request.url = URL("http://testserver/api/validate")
    validation_error = RequestValidationError(errors=[{"loc": ("body", "field"), "msg": "خطأ في الحقل", "type": "value_error"}])

    response = await validation_exception_handler(mock_request, validation_error)
    assert response.status_code == 422
    content = response.body.decode()
    assert "بيانات غير صالحة" in content
    assert "errors" in content
    assert str(mock_request.url) in content

@pytest.mark.asyncio
async def test_http_exception_handler_returns_status_and_detail():
    mock_request = MagicMock()
    mock_request.url = URL("http://testserver/api/http_error")
    http_exc = StarletteHTTPException(status_code=403, detail="غير مصرح")

    response = await http_exception_handler(mock_request, http_exc)
    assert response.status_code == 403
    content = response.body.decode()
    assert "غير مصرح" in content
    assert str(mock_request.url) in content

@pytest.mark.asyncio
async def test_general_exception_handler_returns_500_and_generic_message():
    mock_request = MagicMock()
    mock_request.url = URL("http://testserver/api/unhandled_error")
    exc = Exception("خطأ غير متوقع")

    response = await general_exception_handler(mock_request, exc)
    assert response.status_code == 500
    content = response.body.decode()
    assert "حدث خطأ غير متوقع" in content
    assert str(mock_request.url) in content
