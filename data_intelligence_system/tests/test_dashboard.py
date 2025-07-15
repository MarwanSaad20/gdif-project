import pytest
import pandas as pd
from dash import Dash, html
from dash.exceptions import PreventUpdate

from data_intelligence_system.dashboard.callbacks import register_callbacks
from data_intelligence_system.dashboard.callbacks.kpi_callbacks import (
    register_kpi_callbacks,
    parse_data,
    update_kpi_cards_func
)
from data_intelligence_system.dashboard.callbacks.layout_callbacks import register_layout_callbacks
from data_intelligence_system.dashboard.callbacks.filters_callbacks import register_filters_callbacks
from data_intelligence_system.dashboard.callbacks.charts_callbacks import register_charts_callbacks
from data_intelligence_system.dashboard.callbacks.export_callbacks import register_export_callbacks
from data_intelligence_system.dashboard.callbacks.upload_callbacks import register_upload_callbacks

from data_intelligence_system.dashboard.layouts.main_layout import get_layout, build_upload_section
from data_intelligence_system.dashboard.layouts.kpi_cards import generate_kpi_cards_layout
from data_intelligence_system.dashboard.layouts.charts_placeholders import forecast_chart
from data_intelligence_system.dashboard.layouts.stats_summary import stats_summary_card
from data_intelligence_system.dashboard.layouts.theme import Theme
from data_intelligence_system.dashboard.components.upload_component import upload_section
from data_intelligence_system.dashboard.components.filters import create_dropdown, create_slider, create_date_picker
from data_intelligence_system.dashboard.components.charts import create_line_chart, create_bar_chart, create_pie_chart
from data_intelligence_system.dashboard.components.tables import create_data_table
from data_intelligence_system.dashboard.components.indicators import create_kpi_card

from data_intelligence_system.dashboard.app import app


@pytest.fixture
def sample_df():
    data = {
        "numeric_col": [10, 20, 30, 40, 50],
        "category_col": ["A", "B", "A", "B", "C"],
        "date_col": pd.date_range("2023-01-01", periods=5),
        "null_col": [None, None, 1, 2, 3]
    }
    return pd.DataFrame(data)


@pytest.fixture
def sample_json(sample_df):
    return sample_df.to_json(orient="split")


def test_parse_data_valid(sample_json):
    df = parse_data(sample_json)
    assert not df.empty
    assert "numeric_col" in df.columns


def test_parse_data_empty():
    with pytest.raises(PreventUpdate):
        parse_data("")


def test_parse_data_invalid():
    with pytest.raises(PreventUpdate):
        parse_data("this is not json")


def test_update_kpi_cards_func(sample_df):
    result = update_kpi_cards_func(sample_df)
    assert isinstance(result, tuple)
    assert len(result) == 5


def test_register_all_callbacks_no_error():
    test_app = Dash(__name__)
    test_app.layout = get_layout()
    register_callbacks(test_app)
    assert True


def test_layout_structure():
    layout = get_layout()
    store_ids = {child.id for child in layout.children if hasattr(child, "id")}
    required_ids = {
        "store_raw_data", "store_filtered_data", "store_filtered_multi",
        "store_window_size", "store_raw_data_path", "store_analysis_done"
    }
    assert required_ids.issubset(store_ids)


def test_stats_summary_card_elements():
    card = stats_summary_card()
    found_pre = False

    def find_pre(children):
        nonlocal found_pre
        if isinstance(children, list):
            for c in children:
                find_pre(c)
        elif hasattr(children, "id") and children.id == "stats-summary-pre":
            found_pre = True
        elif hasattr(children, "children"):
            find_pre(children.children)

    find_pre(card.children)
    assert found_pre


def test_theme_colors():
    assert isinstance(Theme.PRIMARY_COLOR, str)
    assert Theme.BACKGROUND_COLOR.startswith("#")


def test_build_upload_section_contains_elements():
    section = build_upload_section()
    children_ids = []

    def gather_ids(children):
        if isinstance(children, list):
            for c in children:
                gather_ids(c)
        elif hasattr(children, "id"):
            children_ids.append(children.id)
        elif hasattr(children, "children"):
            gather_ids(children.children)

    gather_ids(section.children)
    assert "upload-status" in children_ids


def test_forecast_chart_type():
    chart = forecast_chart()
    found_graph = False

    def find_graph(children):
        nonlocal found_graph
        if isinstance(children, list):
            for c in children:
                find_graph(c)
        elif hasattr(children, "id") and children.id == "forecast-chart":
            found_graph = True
        elif hasattr(children, "children"):
            find_graph(children.children)

    find_graph(chart.children)
    assert found_graph


def test_components_functions_return_elements():
    dd = create_dropdown("test-dropdown", options=[{"label": "A", "value": "a"}], placeholder="اختر")
    slider = create_slider("test-slider", 0, 10, 1, 5)
    datepicker = create_date_picker("test-date-picker", start_date="2025-01-01", end_date="2025-01-31")
    upload_comp = upload_section()
    line_chart = create_line_chart("line-chart-test", y_data=[1, 2, 3])
    bar_chart = create_bar_chart("bar-chart-test", y_data=[1, 2, 3])
    pie_chart = create_pie_chart("pie-chart-test", values=[1, 2, 3], names=["A", "B", "C"])
    data_table = create_data_table("table-test")
    indicator = create_kpi_card("indicator-test", "Label", 123)

    assert dd.id == "test-dropdown"
    assert slider.id == "test-slider"
    assert datepicker.id == "test-date-picker"
    assert line_chart.id == "line-chart-test"
    assert bar_chart.id == "bar-chart-test"
    assert pie_chart.id == "pie-chart-test"
    assert data_table.id == "table-test"
    assert indicator.id == "indicator-test"


from pathlib import Path


def test_init_py_files_exist():
    base_path = Path(__file__).parent.parent / "data_intelligence_system" / "dashboard"
    dirs_to_check = [
        base_path / "callbacks",
        base_path / "components",
        base_path / "layouts",
    ]
    for d in dirs_to_check:
        init_file = d / "__init__.py"
        assert init_file.exists(), f"مفقود __init__.py في {d}"


def test_app_instance_exists():
    assert hasattr(app, "layout")
    assert hasattr(app, "run")   # بدل run_server
