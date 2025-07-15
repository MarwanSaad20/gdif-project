import pytest
from unittest.mock import patch, MagicMock
from fastapi import HTTPException
from pathlib import Path
import pandas as pd

from data_intelligence_system.api.utils import dependencies
from data_intelligence_system.api.services.analysis_service import AnalysisService
from data_intelligence_system.api.services import dashboard_service
from data_intelligence_system.api.services.etl_service import ETLService


# ================== اختبارات api/utils/dependencies.py ==================

def test_get_db_yields_and_closes():
    class DummySession:
        closed = False
        def close(self): self.closed = True

    with patch("data_intelligence_system.api.utils.dependencies.get_db_session", return_value=DummySession()):
        gen = dependencies.get_db()
        session = next(gen)
        assert isinstance(session, DummySession)
        gen.close()
        assert session.closed is True


def test_get_current_user_missing_authorization_header():
    with pytest.raises(HTTPException) as exc_info:
        dependencies.get_current_user(None)
    assert exc_info.value.status_code == 401


def test_get_current_user_invalid_authorization_format():
    with pytest.raises(HTTPException) as exc_info:
        dependencies.get_current_user("Token abc123")
    assert exc_info.value.status_code == 401


@patch("data_intelligence_system.api.utils.dependencies.verify_jwt_token")
def test_get_current_user_valid_token(mock_verify):
    mock_verify.return_value = {"user_id": 42}
    result = dependencies.get_current_user("Bearer validtoken123")
    mock_verify.assert_called_once_with("validtoken123")
    assert result == {"user_id": 42}


def test_rate_limiter_blocks_after_limit():
    class DummyRequest:
        def __init__(self, host): self.client = MagicMock(host=host)

    dependencies.rate_limit_store.clear()
    client_ip = "127.0.0.1"
    req = DummyRequest(client_ip)

    for _ in range(100):
        dependencies.rate_limiter(req, max_requests=100, window_seconds=60)

    with pytest.raises(HTTPException) as exc_info:
        dependencies.rate_limiter(req, max_requests=100, window_seconds=60)
    assert exc_info.value.status_code == 429


@patch("data_intelligence_system.api.utils.dependencies.verify_api_key")
def test_api_key_header_valid(mock_verify):
    mock_verify.return_value = None
    api_key = "valid_key"
    result = dependencies.api_key_header(api_key)
    mock_verify.assert_called_once_with(api_key)
    assert result == api_key


def test_api_key_header_missing_raises():
    with pytest.raises(HTTPException):
        dependencies.api_key_header(None)


# ================== اختبارات AnalysisService ==================

@pytest.fixture
def dummy_df():
    return pd.DataFrame({"A": [1, 2, 3], "B": [4, 5, 6], "target": [0, 1, 0]})


@pytest.fixture
def analysis_service(tmp_path, dummy_df):
    file_path = tmp_path / "clean_data.csv"
    dummy_df.to_csv(file_path, index=False)
    return AnalysisService(data_path=file_path)


def test_load_data_success(analysis_service, dummy_df):
    df = analysis_service.load_data()
    pd.testing.assert_frame_equal(df, dummy_df)


@patch("data_intelligence_system.api.services.analysis_service.AnalysisService.load_data")
def test_load_data_file_not_found(mock_load_data, tmp_path):
    # نجعل load_data يرفع FileNotFoundError
    mock_load_data.side_effect = FileNotFoundError("File not found")
    file_path = tmp_path / "nonexistent.csv"
    service = AnalysisService(data_path=file_path)
    with pytest.raises(FileNotFoundError):
        service.load_data(force_reload=True)


@patch("data_intelligence_system.api.services.analysis_service.generate_descriptive_stats")
def test_descriptive_statistics(mock_generate, analysis_service, dummy_df):
    analysis_service.data = dummy_df
    mock_generate.return_value = {"mean": {"A": 2}}
    result = analysis_service.descriptive_statistics()
    mock_generate.assert_called_once_with(dummy_df)
    assert "mean" in result


def test_descriptive_statistics_empty(analysis_service):
    analysis_service.data = pd.DataFrame()
    result = analysis_service.descriptive_statistics()
    assert result == {}


# ================== اختبارات dashboard_service ==================

@patch("pathlib.Path.exists", return_value=True)
@patch("pandas.read_csv")
@patch("data_intelligence_system.config.paths_config.PROCESSED_DATA_DIR", new=Path("/tmp"))
def test_load_processed_data_success(mock_read_csv, mock_exists):
    mock_df = pd.DataFrame({"col1": [1, 2], "col2": [3, 4]})
    mock_read_csv.return_value = mock_df
    df = dashboard_service.load_processed_data("test.csv")
    assert isinstance(df, pd.DataFrame)
    assert not df.empty


@patch("data_intelligence_system.config.paths_config.PROCESSED_DATA_DIR", new=Path("/tmp"))
def test_load_processed_data_file_not_found():
    with pytest.raises(FileNotFoundError):
        dashboard_service.load_processed_data("nonexistent.csv")


# ================== اختبارات ETLService ==================

@pytest.fixture
def etl_service():
    return ETLService()


@patch("data_intelligence_system.api.services.etl_service.load_data")
@patch("data_intelligence_system.api.services.etl_service.extract_file")
def test_etl_extract_use_load_data(mock_extract_file, mock_load_data, etl_service):
    extract_params = MagicMock(filters={"use_load_data": True})
    mock_load_data.return_value = pd.DataFrame({"a": [1, 2]})
    df = etl_service._extract("dummy_source.csv", extract_params)
    assert isinstance(df, pd.DataFrame)
    mock_load_data.assert_called_once_with("dummy_source.csv")
    mock_extract_file.assert_not_called()


@patch("data_intelligence_system.api.services.etl_service.extract_file")
def test_etl_extract_no_params(mock_extract, etl_service):
    mock_extract.return_value = pd.DataFrame({"a": [1, 2]})
    df = etl_service._extract("dummy_source.csv", None)
    assert isinstance(df, pd.DataFrame)
    mock_extract.assert_called_once()


@patch("data_intelligence_system.api.services.etl_service.transform_datasets")
def test_etl_transform_success(mock_transform, etl_service):
    mock_transform.return_value = [("name", pd.DataFrame({"a": [1]}))]
    result = etl_service._transform([("name", pd.DataFrame({"a": [1]}))], None)
    assert isinstance(result, list)
    mock_transform.assert_called_once()


@patch("data_intelligence_system.api.services.etl_service.save_multiple_datasets")
def test_etl_load_success(mock_save, etl_service):
    mock_save.return_value = True
    load_params = MagicMock(target_table="test_table", batch_size=100)
    result = etl_service._load([("name", pd.DataFrame({"a": [1]}))], load_params)
    assert result is True
    mock_save.assert_called_once()


def test_etl_run_etl_success(etl_service):
    with patch.object(etl_service, "_extract", return_value=pd.DataFrame({"a": [1]})) as mock_extract, \
         patch.object(etl_service, "_transform", return_value=[("name", pd.DataFrame({"a": [1]}))]) as mock_transform, \
         patch.object(etl_service, "_load", return_value=True) as mock_load, \
         patch("data_intelligence_system.data.raw.register_sources.main") as mock_register:

        load_params = MagicMock(target_table="test_table", batch_size=100)
        result = etl_service.run_etl("dummy_source.csv", None, None, load_params)
        assert result is True
        mock_extract.assert_called_once()
        mock_transform.assert_called_once()
        mock_load.assert_called_once()
        mock_register.assert_called_once()


def test_etl_run_etl_failure(etl_service):
    with patch.object(etl_service, "_extract", return_value=None), \
         patch("data_intelligence_system.data.raw.register_sources.main") as mock_register:

        load_params = MagicMock(target_table="test_table", batch_size=100)
        result = etl_service.run_etl("dummy_source.csv", None, None, load_params)
        assert result is False
        mock_register.assert_not_called()
