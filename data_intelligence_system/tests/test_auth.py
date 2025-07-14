import pytest
import pandas as pd
import numpy as np
import os
import matplotlib
matplotlib.use('Agg')  # حل مشكلة TclError في بيئة الاختبارات
import matplotlib.pyplot as plt

from data_intelligence_system.utils import (
    data_loader,
    preprocessing,
    feature_utils,
    config_handler
)
from data_intelligence_system.utils.visualization import (
    visuals_static,
    visuals_helpers,
    visuals_interactive
)

# -------- بيانات عامة للاختبارات --------

df_basic = pd.DataFrame({
    "income": [1000, 1500, 2000, None],
    "expenses": [800, 1200, 1800, 1000],
    "clicks": [100, 200, 150, 300],
    "impressions": [1000, 1500, 1800, 0],
    "city": ["Baghdad", "Erbil", "Basra", "Mosul"],
    "country": ["Iraq", "Iraq", "Iraq", "Iraq"],
    "target": [0, 1, 0, 1],
    "category": ["A", "B", "A", "B"],
    "numeric1": [1.5, 2.5, 3.5, 4.5],
    "numeric2": [10, 15, 20, 25]
})

# -------- اختبارات data_loader --------

def test_load_data_csv(tmp_path):
    path = tmp_path / "test.csv"
    df_basic.to_csv(path, index=False)
    df_loaded = data_loader.load_data(str(path))
    pd.testing.assert_frame_equal(df_loaded, df_basic)

def test_load_data_file_not_found():
    with pytest.raises(FileNotFoundError):
        data_loader.load_data("non_existent_file.csv")

def test_load_data_unsupported_ext(tmp_path):
    path = tmp_path / "file.unsupported"
    path.write_text("dummy")
    with pytest.raises(ValueError):
        data_loader.load_data(str(path))

# -------- اختبارات preprocessing --------

def test_normalize_column_names():
    df = pd.DataFrame({" Col 1 ": [1], "COL#2": [2]})
    df_norm = preprocessing.normalize_column_names(df)
    assert "col_1" in df_norm.columns
    assert "col_2" in df_norm.columns

def test_fill_missing_values_mean():
    series = pd.Series([1, np.nan, 3])
    filled = preprocessing.fill_missing_values(series, strategy="mean")
    assert not filled.isnull().any()

def test_fill_missing_values_invalid_strategy():
    with pytest.raises(ValueError):
        preprocessing.fill_missing_values(df_basic, strategy="invalid")

def test_encode_categoricals_label():
    df = pd.DataFrame({"cat": ["a", "b", "a"]})
    encoded = preprocessing.encode_categoricals(df, method="label")
    assert encoded["cat"].dtype == int or np.issubdtype(encoded["cat"].dtype, np.integer)

def test_scale_numericals_standard():
    df = pd.DataFrame({"num": [1, 2, 3, 4, 5]})
    scaled = preprocessing.scale_numericals(df)
    assert abs(scaled["num"].mean()) < 1e-6

# -------- اختبارات feature_utils --------

def test_select_k_best_features_classification():
    X = df_basic[["numeric1", "numeric2"]]
    y = df_basic["target"]
    selected, scores = feature_utils.select_k_best_features(X, y, task="classification", k=1)
    assert isinstance(selected, list)
    assert len(selected) == 1

def test_generate_derived_features():
    df_new = feature_utils.generate_derived_features(df_basic)
    assert "net_savings" in df_new.columns
    assert "ctr" in df_new.columns
    assert "location" in df_new.columns

# -------- اختبارات config_handler --------

def test_config_handler_json(tmp_path):
    import json
    config_data = {"section": {"key": "value", "num": 10}}
    path = tmp_path / "config.json"
    path.write_text(json.dumps(config_data))
    ch = config_handler.ConfigHandler(str(path))
    assert ch.get("section.key") == "value"
    assert ch.get("section.num") == 10
    assert ch.get("section.missing", default=123) == 123

def test_config_handler_ini(tmp_path):
    ini_text = "[section]\nkey = value\nnum = 10\nflag = true"
    path = tmp_path / "config.ini"
    path.write_text(ini_text)
    ch = config_handler.ConfigHandler(str(path))
    assert ch.get("section.key") == "value"
    assert ch.get("section.num") == 10
    assert ch.get("section.flag") is True

# -------- اختبارات visuals_helpers --------

def test_validate_columns_success_and_dropna():
    df = pd.DataFrame({"x": [1, 2, None], "y": [4, 5, 6]})
    filtered = visuals_helpers._validate_columns(df, ["x", "y"])
    assert filtered.shape[0] == 2  # dropna True by default

def test_handle_save_or_show_creates_file(tmp_path):
    fig, ax = plt.subplots()
    ax.plot([1, 2, 3])
    save_path = tmp_path / "fig.png"
    visuals_helpers._handle_save_or_show(fig, str(save_path))
    assert save_path.exists()

# -------- اختبارات visuals_static --------

def test_plot_box_returns_figure_axes():
    fig, ax = visuals_static.plot_box(df_basic, column="income")
    assert fig and ax

def test_plot_correlation_heatmap_raises_on_no_numeric():
    df = pd.DataFrame({"non_num": ["a", "b"]})
    with pytest.raises(ValueError):
        visuals_static.plot_correlation_heatmap(df)

# -------- اختبارات visuals_interactive --------

def test_interactive_scatter_matrix_show(monkeypatch):
    called = {}
    def fake_show(*args, **kwargs):  # تعديل هنا لقبول أي باراميترات
        called["shown"] = True
    monkeypatch.setattr("plotly.graph_objs._figure.Figure.show", fake_show)
    fig = visuals_interactive.interactive_scatter_matrix(df_basic, dimensions=["income", "expenses"])
    assert fig is not None
    assert called.get("shown")

def test_interactive_scatter_matrix_save(tmp_path):
    path = tmp_path / "scatter.html"
    res = visuals_interactive.interactive_scatter_matrix(df_basic, dimensions=["income", "expenses"], save_path=str(path))
    assert res is None
    assert path.exists()
