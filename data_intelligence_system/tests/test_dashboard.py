"""
✅ Comprehensive tests for GDIF Dashboard:
- app creation
- layout structure
- callbacks registration
- components creation
"""

import pytest
from dash import html
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
    """Test that Dash app is created and has layout/title."""
    app = dashboard_app.app
    assert app is not None
    assert hasattr(app, 'layout')
    assert app.title
    assert isinstance(app.layout, html.Div)


def test_layout_structure():
    """Test that get_layout returns Div with expected children IDs."""
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
    """
    Ensure that register_*_callbacks functions do not raise exceptions.
    """
    app = dashboard_app.app
    register_func = getattr(callback_module, "register_" + callback_module.__name__.split(".")[-1].replace("_callbacks", "") + "_callbacks", None)
    if register_func:
        try:
            register_func(app)
        except Exception as e:
            pytest.fail(f"{register_func.__name__} raised exception: {e}")


@pytest.mark.parametrize("component_func", [
    upload_component.upload_section,
    charts.create_line_chart,
    charts.create_bar_chart,
    charts.create_pie_chart,
    tables.create_data_table,
    filters.create_dropdown,
    filters.create_slider,
    filters.create_date_picker,
    indicators.create_indicator_card
])
def test_components_can_be_created(component_func):
    """
    Test that component factory functions return non-null Dash components.
    """
    try:
        result = component_func(*([None] * component_func.__code__.co_argcount))
        assert result is not None
    except Exception as e:
        pytest.fail(f"{component_func.__name__} raised exception: {e}")


def test_toggle_sidebar_logic():
    """Test toggle_sidebar logic directly."""
    style_block = {'display': 'block', 'width': '250px'}
    style_none = {'display': 'none', 'width': '250px'}
    # Toggle from block -> none
    res = layout_callbacks.toggle_sidebar(1, style_block)
    assert res['display'] == 'none'
    assert res['width'] == '0px'
    # Toggle from none -> block
    res = layout_callbacks.toggle_sidebar(1, style_none)
    assert res['display'] == 'block'
    assert res['width'] == '250px'


def test_enable_analysis_button_logic():
    """Test enable_analysis_button_if_data_uploaded logic directly."""
    assert layout_callbacks.enable_analysis_button_if_data_uploaded("/tmp/data.csv") is False
    assert layout_callbacks.enable_analysis_button_if_data_uploaded(None) is True
