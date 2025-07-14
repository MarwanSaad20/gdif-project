import pytest
from dash import html
from dash.exceptions import PreventUpdate
from dash import callback_context

from data_intelligence_system.dashboard import app as dashboard_app
from data_intelligence_system.dashboard.layouts import main_layout
from data_intelligence_system.dashboard.callbacks import (
    layout_callbacks,
    kpi_callbacks,
    charts_callbacks,
    export_callbacks,
    upload_callbacks,
    filters_callbacks,
)
from data_intelligence_system.dashboard.components import (
    upload_component,
    charts,
    tables,
    filters,
    indicators
)

def test_app_creation():
    app = dashboard_app.app
    assert app is not None
    assert hasattr(app, 'layout')
    assert app.title
    assert isinstance(app.layout, html.Div)

def test_layout_structure():
    layout = main_layout.get_layout()
    assert isinstance(layout, html.Div)
    expected_store_ids = [
        "store_raw_data", "store_filtered_data", "store_filtered_multi",
        "store_window_size", "store_raw_data_path", "store_analysis_done"
    ]
    found_ids = [comp.id for comp in layout.children if hasattr(comp, 'id')]
    for store_id in expected_store_ids:
        assert store_id in found_ids

@pytest.mark.parametrize("callback_module", [
    layout_callbacks, kpi_callbacks, charts_callbacks,
    export_callbacks, upload_callbacks, filters_callbacks
])
def test_register_callbacks_does_not_fail(callback_module):
    app = dashboard_app.app
    register_func_name = "register_" + callback_module.__name__.split(".")[-1].replace("_callbacks", "") + "_callbacks"
    register_func = getattr(callback_module, register_func_name, None)
    if register_func:
        try:
            register_func(app)
        except Exception as e:
            pytest.fail(f"{register_func.__name__} raised exception: {e}")

@pytest.mark.parametrize("component_func, args", [
    (upload_component.upload_section, []),

    (charts.create_line_chart, [
        [1, 2, 3],
        [10, 20, 15]
    ]),
    (charts.create_bar_chart, [
        ['A', 'B', 'C'],
        [5, 7, 3]
    ]),
    (charts.create_pie_chart, [
        ['Cat1', 'Cat2', 'Cat3'],
        [30, 50, 20]
    ]),

    (tables.create_data_table, [
        "test-table-id",
        [{"id": "col1", "name": "عمود 1"}],
        [],
        10,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        False,
        "native",
        "single",
    ]),

    (filters.create_dropdown, [
        "test-dropdown-id",
        [{"label": "خيار 1", "value": "val1"}],
        None,
        False,
        False,
        False,
        None,
    ]),

    (filters.create_slider, [
        "test-slider-id",
        0,
        10,
        1,
        5,
        None,
        True,
        True,
        False,
    ]),

    (filters.create_date_picker, [
        "test-date-picker-id",
        None,
        None,
        None,
        None,
        None,
        False,
        "YYYY-MM-DD",
    ]),

    (indicators.create_kpi_card, [
        "test-kpi-card-id",
        "عنوان KPI",
        "القيمة",
        None,
        None,
        None,
        None,
    ]),
])
def test_components_can_be_created(component_func, args):
    try:
        result = component_func(*args)
        assert result is not None
    except Exception as e:
        pytest.fail(f"{component_func.__name__} raised exception: {e}")

def test_toggle_sidebar_logic():
    style_block = {'display': 'block', 'width': '250px'}
    style_none = {'display': 'none', 'width': '250px'}
    res = layout_callbacks.toggle_sidebar(1, style_block)
    assert res['display'] == 'none'
    assert res['width'] == '0px'
    res = layout_callbacks.toggle_sidebar(1, style_none)
    assert res['display'] == 'block'
    assert res['width'] == '250px'

def test_enable_analysis_button_logic():
    assert layout_callbacks.enable_analysis_button_if_data_uploaded("/tmp/data.csv") is False
    assert layout_callbacks.enable_analysis_button_if_data_uploaded(None) is True

# =================
# اختبار callback موحد للرفع والتحليل (upload_callbacks.py)
# =================
from data_intelligence_system.dashboard.callbacks import upload_callbacks
from data_intelligence_system.core.data_bindings import df_to_dash_json
import pandas as pd

def test_unified_upload_and_analysis_callback(monkeypatch):
    sample_df = pd.DataFrame({
        "category": ["A", "B", "A"],
        "date": pd.to_datetime(["2025-01-01", "2025-01-02", "2025-01-03"]),
        "type": ["X", "Y", "X"],
        "value": [10, 20, 15]
    })

    monkeypatch.setattr(upload_callbacks, "save_uploaded_file", lambda contents, filename: "/tmp/fake_path.csv")
    monkeypatch.setattr(upload_callbacks, "load_data", lambda path: sample_df.copy())
    monkeypatch.setattr(upload_callbacks.etl_pipeline, "run_full_pipeline", lambda filepath=None: True)
    monkeypatch.setattr(upload_callbacks, "compute_statistics", lambda df: None)
    monkeypatch.setattr(upload_callbacks.report_dispatcher, "generate_reports", lambda df, args: None)

    # اختبار رفع ملف
    out = upload_callbacks.handle_upload_and_analysis(
        "data:text/csv;base64,FAKE_BASE64_ENCODED",
        None,
        "test.csv",
        None,
        "upload-data"
    )
    assert isinstance(out, tuple)
    assert "تم رفع الملف" in out[0].children or "⚠️" in out[0].children

    # اختبار تحليل بدون ملف (يجب تحذير)
    out2 = upload_callbacks.handle_upload_and_analysis(
        None,
        1,
        None,
        None,
        "run-full-analysis-btn"
    )
    assert isinstance(out2, tuple)
    assert "يرجى رفع ملف" in out2[1].children

    # اختبار تحليل مع ملف مرفوع
    out3 = upload_callbacks.handle_upload_and_analysis(
        None,
        1,
        None,
        "/tmp/fake_path.csv",
        "run-full-analysis-btn"
    )
    assert isinstance(out3, tuple)
    assert any(
        "تم تنفيذ التحليل الكامل" in (child.children if isinstance(child.children, str) else "")
        for child in out3[1].children
    )
