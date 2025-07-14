import pytest
import pandas as pd
from pathlib import Path
from unittest.mock import patch, MagicMock

# استيراد مطلق من جذر المشروع
from data_intelligence_system.etl import extract, transform, load, pipeline, etl_utils


# ---- بيانات مساعدة للاختبارات ----
@pytest.fixture
def sample_raw_csv(tmp_path):
    csv_path = tmp_path / "sample.csv"
    df = pd.DataFrame({
        "Name": ["Alice", "Bob", "Charlie"],
        "Age": [25, 30, 35],
        "City": ["NY", "LA", "SF"]
    })
    df.to_csv(csv_path, index=False)
    return csv_path, df


@pytest.fixture
def sample_dataframe():
    return pd.DataFrame({
        "name": ["alice", "bob", "alice", "dan"],
        "age": [25, 30, 25, None],
        "city": ["NY", "LA", "NY", "SF"]
    })


# ---- اختبارات extract.py ----

def test_is_valid_file(sample_raw_csv):
    path, _ = sample_raw_csv
    assert extract.is_valid_file(path) is True
    fake_path = Path("nonexistent.csv")
    assert extract.is_valid_file(fake_path) is False


@patch("data_intelligence_system.etl.extract.read_file")
def test_extract_file_success(mock_read_file, sample_raw_csv):
    path, df = sample_raw_csv
    mock_read_file.return_value = df
    result = extract.extract_file(path, validate=False)
    assert isinstance(result, dict)
    assert list(result.keys())[0] == extract.extract_file_name(str(path))


@patch("data_intelligence_system.etl.extract.read_file")
def test_extract_all_data(mock_read_file, tmp_path):
    raw_dir = tmp_path / "raw"
    raw_dir.mkdir()
    file_path = raw_dir / "data.csv"
    df = pd.DataFrame({"col1": [1, 2], "col2": [3, 4]})
    df.to_csv(file_path, index=False)

    mock_read_file.return_value = df

    with patch("data_intelligence_system.config.paths_config.RAW_DATA_PATHS", [raw_dir]):
        with patch("data_intelligence_system.config.paths_config.SUPPORTED_EXTENSIONS", [".csv"]):
            data = extract.extract_all_data(validate=False)
            assert isinstance(data, list)
            assert any(isinstance(t[1], pd.DataFrame) for t in data)


# ---- اختبارات transform.py ----

def test_unify_column_names(sample_dataframe):
    df = sample_dataframe.copy()
    df.columns = [" Name ", "AGE", "City!"]
    df2 = transform.unify_column_names(df)
    assert "name" in df2.columns
    assert "age" in df2.columns
    assert "city" in df2.columns


def test_encode_categorical_columns(sample_dataframe):
    df = sample_dataframe.copy()
    result = transform.encode_categorical_columns(df, encode_type="label")
    assert all(isinstance(val, (int, float)) for val in result["name"])


def test_remove_duplicates(sample_dataframe):
    df = sample_dataframe.copy()
    df2 = transform.remove_duplicates(df)
    assert len(df2) < len(df)


@patch("data_intelligence_system.etl.transform.fill_missing", lambda df: df.fillna(0))
@patch("data_intelligence_system.etl.transform.scale_numericals", lambda df: df)
def test_transform_datasets(sample_dataframe):
    datasets = [("test.csv", sample_dataframe)]
    transformed = transform.transform_datasets(datasets)
    assert isinstance(transformed, list)
    assert len(transformed) == 1
    assert isinstance(transformed[0][1], pd.DataFrame)


# ---- اختبارات load.py ----

@patch("data_intelligence_system.utils.file_manager.save_file")
@patch("data_intelligence_system.data.processed.validate_clean_data.validate", lambda df: True)
@patch("data_intelligence_system.data.raw.archive_raw_file.archive_file", new_callable=MagicMock, create=True)
def test_save_dataframe(mock_archive_file, mock_save_file, tmp_path, sample_dataframe):
    # موك لحفظ الملف فعلياً داخل المسار المؤقت مع إعادة المسار
    def fake_save_file(df, filepath):
        p = Path(filepath)
        p.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(p, index=False)
        return p

    mock_save_file.side_effect = fake_save_file

    output_dir = tmp_path / "processed"
    output_dir.mkdir()
    path = load.save_dataframe(sample_dataframe, output_dir, "testfile", "csv")
    assert path is not None
    assert path.exists()


def test_create_output_dir(tmp_path):
    new_dir = tmp_path / "new_output"
    result = load.create_output_dir(new_dir)
    assert result.exists()
    assert isinstance(result, Path)


# ---- اختبارات pipeline.py ----

@patch("data_intelligence_system.etl.extract.extract_file")
@patch("data_intelligence_system.etl.extract.is_valid_file", return_value=True)
@patch("data_intelligence_system.etl.transform.transform_datasets")
@patch("data_intelligence_system.utils.file_manager.save_file")
def test_run_full_pipeline(mock_save_file, mock_transform, mock_extract_file, mock_is_valid, sample_dataframe):
    mock_extract_file.return_value = {"file.csv": sample_dataframe}
    mock_transform.return_value = [("file.csv", sample_dataframe)]
    mock_save_file.return_value = True

    result = pipeline.run_full_pipeline(filepath="fake/path/file.csv", encode_type="label", scale_type="standard")
    assert result is True


# ---- اختبارات etl_utils.py ----

def test_get_all_files(tmp_path):
    file1 = tmp_path / "a.csv"
    file2 = tmp_path / "b.json"
    file1.write_text("dummy")
    file2.write_text("dummy")
    exts = [".csv"]
    files = etl_utils.get_all_files(tmp_path, extensions=exts)
    assert any(str(file1) == f for f in files)
    assert all(Path(f).suffix in exts for f in files)


def test_detect_file_type():
    assert etl_utils.detect_file_type("test.csv") == "csv"
    assert etl_utils.detect_file_type("test.xlsx") == "excel"
    assert etl_utils.detect_file_type("test.json") == "json"
    assert etl_utils.detect_file_type("test.unsupported") == "unsupported"


def test_is_supported_file():
    assert etl_utils.is_supported_file("file.csv") is True
    assert etl_utils.is_supported_file("file.unsupported") is False


def test_ensure_directory_exists(tmp_path):
    new_dir = tmp_path / "newfolder"
    result = etl_utils.ensure_directory_exists(new_dir)
    assert result.exists()


if __name__ == "__main__":
    pytest.main(["-v", __file__])
