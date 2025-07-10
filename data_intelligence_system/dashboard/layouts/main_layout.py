from dash import html, dcc, dash_table
import dash_bootstrap_components as dbc
from datetime import datetime, timedelta

from data_intelligence_system.dashboard.components.filters import (
    create_dropdown, create_slider, create_date_picker
)
from data_intelligence_system.dashboard.components.upload_component import upload_section
from data_intelligence_system.dashboard.layouts.charts_placeholders import forecast_chart
from data_intelligence_system.dashboard.layouts.stats_summary import stats_summary_card
from data_intelligence_system.dashboard.layouts.theme import Theme  # استيراد الثيم من الملف المحدث


BACKGROUND_COLOR = Theme.BACKGROUND_COLOR
TEXT_COLOR = Theme.TEXT_COLOR
PRIMARY_COLOR = Theme.PRIMARY_COLOR


def build_title_section():
    return dbc.Row(dbc.Col(
        html.H1(
            "نظام تحليل البيانات العام - GDIF",
            className="text-center my-4",
            style={"color": PRIMARY_COLOR, "fontWeight": "bold"}
        ), width=12
    ))


def build_upload_section():
    return dbc.Row(dbc.Col([
        html.H3("📁 رفع البيانات", className="mb-3", style={"color": TEXT_COLOR}),
        dcc.Loading(children=upload_section(), type="circle", color=PRIMARY_COLOR),
        html.Div(id="upload-status", className="text-info text-center mt-2 mb-4"),
    ]))


def build_filters_section():
    return dbc.Row(dbc.Col([
        html.H4("🎛️ الفلاتر", style={"color": TEXT_COLOR}),
        create_dropdown("filter-category-dropdown", options=[], placeholder="اختر فئة"),
        html.Br(),
        create_slider("filter-value-slider", 0, 100, 1, 50),
        html.Br(),
        create_date_picker(
            "filter-date-picker",
            start_date=(datetime.today() - timedelta(days=30)).date(),
            end_date=datetime.today().date(),
        ),
        html.Br(),
        dbc.Button("↩️ إعادة تعيين الفلاتر", id="reset-filters-btn", color="warning", size="sm"),
        html.Hr(style={"borderColor": "#555"})
    ]))


def build_analysis_button():
    return dbc.Row(dbc.Col(
        dbc.Button(
            "🔄 تشغيل التحليل الكامل", id="run-full-analysis-btn", color="success",
            className="my-3", size="lg", n_clicks=0, disabled=True
        ),
        width={"size": 4, "offset": 4}, className="text-center"
    ))


def build_report_section():
    return dbc.Row(dbc.Col([
        html.H4("📤 تصدير التقرير", className="mt-4", style={"color": TEXT_COLOR}),
        dbc.InputGroup([
            dbc.Select(
                id="report-format-dropdown",
                options=[
                    {"label": "PDF", "value": "pdf"},
                    {"label": "Excel", "value": "excel"},
                    {"label": "HTML", "value": "html"},
                    {"label": "CSV", "value": "csv"},
                ],
                placeholder="اختر نوع التقرير",
            ),
            dbc.Button("تحميل التقرير", id="download-btn", color="primary"),
        ], size="md", className="mb-3"),
        html.Div(id="report-download-status", className="text-success mt-1 text-center"),
        dcc.Download(id="download-report")
    ]))


def build_data_table_section():
    return dbc.Row(dbc.Col([
        html.H4("📋 عرض البيانات", style={"color": TEXT_COLOR}),
        dcc.Loading(
            dash_table.DataTable(
                id="data-table",
                columns=[{"name": "⚠️ لا توجد بيانات بعد", "id": "no_data"}],
                data=[{"no_data": "يرجى رفع ملف لعرض البيانات هنا"}],
                page_size=10,
                virtualization=True,
                page_action='native',
                fixed_rows={"headers": True},
                style_table={"overflowX": "auto", "minWidth": "100%"},
                style_header={"backgroundColor": "#1e1e1e", "color": "white", "fontWeight": "bold"},
                style_cell={
                    "backgroundColor": "#2e2e2e", "color": "white", "textAlign": "center",
                    "fontFamily": "Tahoma"
                },
                row_selectable="multi",
                filter_action="native",
                sort_action="native",
                style_data_conditional=[
                    {'if': {'row_index': 'odd'}, 'backgroundColor': '#252525'},
                    {'if': {'state': 'selected'}, 'backgroundColor': PRIMARY_COLOR, 'color': 'white'}
                ]
            ),
            type="circle", color=PRIMARY_COLOR
        ),
        html.Hr(style={"borderColor": "#444"})
    ]))


def get_layout():
    """Builds the main layout of the GDIF dashboard"""
    return html.Div([
        # Stores for internal state
        dcc.Store(id="store_raw_data"),
        dcc.Store(id="store_filtered_data"),
        dcc.Store(id="store_filtered_multi"),
        dcc.Store(id="store_window_size"),
        dcc.Store(id="store_raw_data_path"),
        dcc.Store(id="store_analysis_done"),

        dbc.Container([
            build_title_section(),
            build_upload_section(),
            build_filters_section(),
            build_analysis_button(),
            dbc.Row(dbc.Col(html.Div(id="full-analysis-status", className="text-warning text-center mb-4"))),
            dbc.Row(dbc.Col(html.Div(id="kpi-container"))),
            build_report_section(),
            build_data_table_section(),
            dbc.Row([
                dbc.Col(dcc.Graph(id="line-chart", style={"height": "400px"}), md=6),
                dbc.Col(dcc.Graph(id="bar-chart", style={"height": "400px"}), md=6),
            ]),
            dbc.Row([
                dbc.Col(dcc.Graph(id="pie-chart", style={"height": "400px"}), md=6),
                dbc.Col(stats_summary_card(), md=6)
            ]),
            dbc.Row(dbc.Col(forecast_chart(), md=12)),
            dbc.Row(dbc.Col(
                html.Footer(
                    "© 2025 نظام تحليل البيانات العام - GDIF | جميع الحقوق محفوظة",
                    className="text-center text-muted py-4",
                    style={"color": TEXT_COLOR}
                ), width=12
            )),
            html.Div(style={"marginBottom": "100px"})
        ], fluid=True, style={
            "padding": "30px", "minHeight": "100vh", "backgroundColor": BACKGROUND_COLOR,
            "color": TEXT_COLOR, "direction": "rtl",
            "fontFamily": "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif"
        })
    ], style={
        "minHeight": "100vh", "overflowY": "auto", "backgroundColor": BACKGROUND_COLOR,
        "color": TEXT_COLOR, "direction": "rtl",
        "fontFamily": "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif"
    })
