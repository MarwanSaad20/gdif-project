from dash import html, dcc, dash_table
import dash_bootstrap_components as dbc
from datetime import datetime, timedelta

# 🧩 المكونات التفاعلية
from data_intelligence_system.dashboard.components.filters import (
    create_dropdown, create_slider, create_date_picker
)
from data_intelligence_system.dashboard.components.upload_component import upload_section

# 🧩 مكونات التخطيط الثابتة
from data_intelligence_system.dashboard.layouts.charts_placeholders import forecast_chart

from data_intelligence_system.dashboard.layouts.stats_summary import stats_summary_card

# 🎨 ثيم الألوان
BACKGROUND_COLOR = "#0A0F1A"
TEXT_COLOR = "#FFFFFF"
PRIMARY_COLOR = "#1E90FF"


def get_layout():
    """واجهة النظام الكاملة – متكاملة وقابلة للتمرير"""
    return html.Div([

        # 🧠 تخزين بيانات داخلية (dcc.Store)
        dcc.Store(id="store_raw_data"),
        dcc.Store(id="store_filtered_data"),
        dcc.Store(id="store_filtered_multi"),
        dcc.Store(id="store_window_size"),
        dcc.Store(id="store_raw_data_path"),      # تخزين مسار الملف المرفوع
        dcc.Store(id="store_analysis_done"),      # حالة الانتهاء من التحليل

        dbc.Container([

            # 🟦 العنوان الرئيسي
            dbc.Row(dbc.Col(
                html.H1("نظام تحليل البيانات العام - GDIF", className="text-center my-4",
                        style={"color": PRIMARY_COLOR, "fontWeight": "bold"}),
                width=12
            )),

            # 📁 مقطع رفع البيانات
            dbc.Row(dbc.Col([
                html.H3("📁 رفع البيانات", className="mb-3", style={"color": TEXT_COLOR}),
                dcc.Loading(children=upload_section(), type="circle", color=PRIMARY_COLOR),
                html.Div(id="upload-status", className="text-info text-center mt-2 mb-4"),
            ])),

            # 🎛️ الفلاتر
            dbc.Row(dbc.Col([
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
                dbc.Button("↩️ إعادة تعيين الفلاتر", id="reset-filters-btn", color="warning", size="sm",
                           title="زر إعادة تعيين الفلاتر"),
                html.Hr(style={"borderColor": "#555"})
            ])),

            # 🟢 زر التحليل الكامل
            dbc.Row(dbc.Col(
                dbc.Button("🔄 تشغيل التحليل الكامل", id="run-full-analysis-btn", color="success",
                           className="my-3", size="lg", n_clicks=0, disabled=True,
                           title="زر تشغيل التحليل الكامل (يُفعل بعد رفع الملف)"),
                width={"size": 4, "offset": 4},
                className="text-center"
            )),

            # عرض حالة التحليل الكامل
            dbc.Row(dbc.Col(html.Div(id="full-analysis-status", className="text-warning text-center mb-4"))),

            # 📊 مؤشرات الأداء (KPI Cards) – قسم ديناميكي يُحدث بالكولباك
            dbc.Row(dbc.Col(html.Div(id="kpi-container"))),

            # 📤 تصدير التقارير
            dbc.Row(dbc.Col([
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
                    dbc.Button("تحميل التقرير", id="download-btn", color="primary",
                               title="زر تحميل التقرير"),
                ], size="md", className="mb-3"),
                html.Div(id="report-download-status", className="text-success mt-1 text-center"),
                dcc.Download(id="download-report")
            ])),

            # 📋 جدول عرض البيانات
            dbc.Row(dbc.Col([
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
                        style_header={
                            "backgroundColor": "#1e1e1e",
                            "color": "white",
                            "fontWeight": "bold"
                        },
                        style_cell={
                            "backgroundColor": "#2e2e2e",
                            "color": "white",
                            "textAlign": "center",
                            "fontFamily": "Tahoma",
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
            ])),

            # 📈 الرسوم البيانية
            dbc.Row([
                dbc.Col(dcc.Graph(id="line-chart", style={"height": "400px"}), md=6),
                dbc.Col(dcc.Graph(id="bar-chart", style={"height": "400px"}), md=6),
            ]),
            dbc.Row([
                dbc.Col(dcc.Graph(id="pie-chart", style={"height": "400px"}), md=6),
                dbc.Col(stats_summary_card(), md=6)
            ]),

            # 🔮 التنبؤ الزمني
            dbc.Row(dbc.Col(forecast_chart(), md=12)),

            # 🦶 الفوتر
            dbc.Row(dbc.Col(
                html.Footer("© 2025 نظام تحليل البيانات العام - GDIF | جميع الحقوق محفوظة",
                            className="text-center text-muted py-4",
                            style={"color": TEXT_COLOR}),
                width=12
            )),

            # ⬇️ هامش سفلي
            html.Div(style={"marginBottom": "100px"})

        ], fluid=True, style={
            "padding": "30px",
            "minHeight": "100vh",
            "backgroundColor": BACKGROUND_COLOR,
            "color": TEXT_COLOR,
            "direction": "rtl",
            "fontFamily": "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif",
        })

    ], style={
        "minHeight": "100vh",
        "overflowY": "auto",
        "backgroundColor": BACKGROUND_COLOR,
        "color": TEXT_COLOR,
        "direction": "rtl",
        "fontFamily": "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif",
    })
