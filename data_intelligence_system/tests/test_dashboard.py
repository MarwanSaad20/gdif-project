"""
✅ Tests for GDIF Dashboard (app, layout, and callbacks)
"""

import pytest
from dash import html
from data_intelligence_system.dashboard import app as dashboard_app
from data_intelligence_system.dashboard.layouts.main_layout import get_layout
from data_intelligence_system.dashboard.callbacks import layout_callbacks
from data_intelligence_system.dashboard.components import indicators


def test_app_creation():
    """
    Test that the Dash app is created and has correct properties.
    """
    app = dashboard_app.app
    assert app is not None
    assert hasattr(app, 'layout')
    assert app.title is not None
    assert isinstance(app.layout, html.Div)


def test_layout_structure():
    """
    Test that get_layout returns a Div with expected children.
    """
    layout = get_layout()
    assert isinstance(layout, html.Div)
    # يجب أن يحتوي على dcc.Store و dbc.Container على الأقل
    store_ids = [
        "store_raw_data", "store_filtered_data", "store_filtered_multi",
        "store_window_size", "store_raw_data_path", "store_analysis_done"
    ]
    found_ids = [comp.id for comp in layout.children if hasattr(comp, 'id')]
    for store_id in store_ids:
        assert store_id in found_ids


def test_register_layout_callbacks():
    """
    Test that registering layout callbacks does not raise exceptions
    and adds entries to app.callback_map.
    """
    app = dashboard_app.app
    num_callbacks_before = len(app.callback_map)

    # Call the registration function
    layout_callbacks.register_layout_callbacks(app)

    num_callbacks_after = len(app.callback_map)
    assert num_callbacks_after >= num_callbacks_before + 1  # تأكد تمت إضافة كولباكات


@pytest.mark.parametrize("current_display,new_display,expected_width", [
    ("block", "none", "0px"),
    ("none", "block", "250px"),
])
def test_toggle_sidebar_logic(current_display, new_display, expected_width):
    """
    Test the toggle_sidebar logic in isolation.
    """
    # استدعاء الدالة داخليًا بدون app.callback
    current_style = {'display': current_display, 'width': '250px'}
    result = layout_callbacks.toggle_sidebar(1, current_style)
    assert isinstance(result, dict)
    assert result['display'] == new_display
    assert result['width'] == expected_width


def test_enable_analysis_button_if_data_uploaded():
    """
    Test enabling the analysis button when a file is uploaded.
    """
    # مع وجود path -> يجب تفعيل الزر
    path = "/tmp/data.csv"
    enabled = layout_callbacks.enable_analysis_button_if_data_uploaded(path)
    assert enabled is False

    # بدون path -> يبقى معطل
    enabled = layout_callbacks.enable_analysis_button_if_data_uploaded(None)
    assert enabled is True


# اختبارات لمكونات indicators.py

def test_create_kpi_card_basic():
    """
    Test creating a single KPI card with minimal required arguments.
    """
    card = indicators.create_kpi_card(id="test-kpi", title="اختبار")
    assert isinstance(card, html.Div)
    assert card.id == "test-kpi"
    # تحقق أن العنوان موجود ضمن children
    assert any(isinstance(child, html.Div) and child.children == "اختبار" for child in card.children)


def test_create_kpi_container_with_cards():
    """
    Test creating a container with multiple KPI cards.
    """
    cards = [
        indicators.create_kpi_card(id=f"kpi-{i}", title=f"بطاقة {i}") for i in range(3)
    ]
    container = indicators.create_kpi_container(cards)
    assert isinstance(container, html.Div)
    assert len(container.children) == 3


def test_dashboard_kpis_default_returns_div():
    """
    Test that dashboard_kpis_default returns a Div containing default KPI cards.
    """
    container = indicators.dashboard_kpis_default()
    assert isinstance(container, html.Div)
    assert len(container.children) > 0
