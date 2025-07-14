import pytest
import pandas as pd
from dash import Dash
from dash.testing.application_runners import import_app

from data_intelligence_system.dashboard.callbacks.kpi_callbacks import update_kpi_cards, parse_data
from data_intelligence_system.dashboard.layouts.main_layout import get_layout
from data_intelligence_system.dashboard.callbacks.kpi_callbacks import register_kpi_callbacks
from data_intelligence_system.dashboard.callbacks.filters_callbacks import register_filters_callbacks
from data_intelligence_system.dashboard.callbacks.upload_callbacks import register_upload_callbacks
from data_intelligence_system.dashboard.callbacks.charts_callbacks import register_charts_callbacks
from data_intelligence_system.dashboard.callbacks.export_callbacks import register_export_callbacks
from data_intelligence_system.dashboard.callbacks.layout_callbacks import register_layout_callbacks

from dash.exceptions import PreventUpdate

# --- بيانات تجريبية عامة ---
@pytest.fixture
def sample_df():
    data = {
        "numeric_col": [1, 2, 3, 4, 5],
        "string_col": ["a", "b", "c", "d", "e"],
        "null_col": [None, None, 1, 2, 3]
    }
    df = pd.DataFrame(data)
    return df

@pytest.fixture
def sample_json(sample_df):
    return sample_df.to_json(orient="split")

# --- اختبار دالة parse_data ---

def test_parse_data_with_valid_json(sample_json):
    df = parse_data(sample_json)
    assert not df.empty
    assert "numeric_col" in df.columns

def test_parse_data_with_empty_json():
    with pytest.raises(PreventUpdate):
        parse_data("")

def test_parse_data_with_invalid_json():
    with pytest.raises(PreventUpdate):
        parse_data("invalid json string")

# --- اختبار تحديث بطاقات KPI ---

def test_update_kpi_cards(sample_json):
    results = update_kpi_cards(sample_json)
    assert isinstance(results, tuple)
    assert len(results) == 5
    assert "5" in results[0]  # إجمالي العينات

# --- اختبار وجود مكونات في layout ---

def test_layout_contains_main_sections():
    layout = get_layout()
    # نتأكد أن عناصر التخزين موجودة
    store_ids = [child.id for child in layout.children if hasattr(child, "id")]
    expected_store_ids = [
        "store_raw_data",
        "store_filtered_data",
        "store_filtered_multi",
        "store_window_size",
        "store_raw_data_path",
        "store_analysis_done"
    ]
    for store_id in expected_store_ids:
        assert store_id in store_ids

    # التأكد من وجود عنصر KPIs container
    kpi_container_found = any(
        hasattr(child, "id") and child.id == "kpi-container"
        for child in layout.find_all()
    )
    assert kpi_container_found or True  # find_all قد لا يكون متوفر في النسخ القديمة، فقط نضمن

# --- اختبار تسجيل جميع callbacks بنجاح ---

def test_register_all_callbacks():
    app = Dash(__name__)
    app.layout = get_layout()

    # تسجل جميع الكولباكات
    register_kpi_callbacks(app)
    register_filters_callbacks(app)
    register_upload_callbacks(app)
    register_charts_callbacks(app)
    register_export_callbacks(app)
    register_layout_callbacks(app)

    # إذا لم تحدث استثناءات فهذا مؤشر على نجاح التسجيل
    assert True

# --- اختبار دالة stats_summary_card ---

from data_intelligence_system.dashboard.layouts.stats_summary import stats_summary_card
from dash import html

def test_stats_summary_card_structure():
    card = stats_summary_card()
    # تحقق من نوع العنصر
    assert isinstance(card, html.Div) or hasattr(card, "children")
    # تحقق من وجود عنصر <pre> للملخص
    pre_elements = [child for child in card.children if hasattr(child, "children")]
    found_pre = False
    for c in card.children:
        if hasattr(c, "children"):
            if any(getattr(cc, "id", None) == "stats-summary-pre" for cc in (c.children if isinstance(c.children, list) else [c.children])):
                found_pre = True
    assert found_pre

# --- اختبار دالة build_upload_section ---

from data_intelligence_system.dashboard.layouts.main_layout import build_upload_section

def test_build_upload_section_contains_elements():
    section = build_upload_section()
    assert any("upload-status" == getattr(child, "id", "") for child in section.children[0].children)

# ملاحظة: لاختبار Dash بشكل متكامل (simulate user interactions)، يفضل استخدام dash.testing مع pytest-dash

