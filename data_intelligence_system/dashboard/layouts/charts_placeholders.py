from dash import dcc, html
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from typing import Optional, List, Dict, Union

# 🎨 إعدادات التصميم
BACKGROUND_COLOR = "#0A0F1A"
TEXT_COLOR = "#FFFFFF"
PRIMARY_COLOR = "#1E90FF"
MARGIN_DEFAULT = dict(l=40, r=40, t=40, b=40)
SHOW_MODEBAR = False


def get_base_layout(title: str = "رسم بياني",
                    is_placeholder: bool = True,
                    placeholder_text: Optional[str] = None) -> go.Layout:
    """
    توليد تخطيط موحد للرسم البياني مع دعم لإظهار نص بديل عند عدم وجود بيانات.

    :param title: عنوان الرسم البياني.
    :param is_placeholder: إذا كان الرسم احتياطيًا (فارغًا).
    :param placeholder_text: نص بديل يظهر في حالة عدم وجود بيانات.
    :return: كائن تخطيط Plotly.
    """
    if placeholder_text is None:
        placeholder_text = "⚠️ لا توجد بيانات بعد"

    layout = go.Layout(
        title=title,
        plot_bgcolor=BACKGROUND_COLOR,
        paper_bgcolor=BACKGROUND_COLOR,
        font=dict(color=TEXT_COLOR),
        margin=MARGIN_DEFAULT,
        hovermode="closest"
    )
    if is_placeholder:
        layout.annotations = [dict(
            text=placeholder_text,
            x=0.5, y=0.5, xref='paper', yref='paper',
            showarrow=False,
            font=dict(size=16, color="#AAAAAA")
        )]
    return layout


def create_placeholder_chart(chart_type: str, chart_id: str, title: str) -> dcc.Graph:
    """
    توليد رسم بياني فارغ (placeholder) حسب نوع الرسم المطلوب.

    :param chart_type: نوع الرسم (line, bar, pie, scatter, box, heatmap, area, bubble, dist).
    :param chart_id: معرف الرسم البياني.
    :param title: عنوان الرسم البياني.
    :return: عنصر dcc.Graph جاهز للعرض.
    :raises ValueError: إذا كان نوع الرسم غير مدعوم.
    """
    chart_map: Dict[str, List[go.BaseTraceType]] = {
        "line": [go.Scatter(x=[], y=[], mode='lines')],
        "bar": [go.Bar(x=[], y=[])],
        "pie": [go.Pie(labels=[], values=[], hole=0.3)],
        "scatter": [go.Scatter(x=[], y=[], mode='markers')],
        "box": [go.Box(y=[])],
        "heatmap": [go.Heatmap(z=[[]])],
        "area": [go.Scatter(x=[], y=[], fill='tozeroy')],
        "bubble": [go.Scatter(x=[], y=[], mode='markers', marker=dict(size=[]))],
        "dist": [go.Histogram(x=[], nbinsx=30)],
    }

    if chart_type not in chart_map:
        raise ValueError(f"نوع الرسم غير مدعوم: {chart_type}")

    fig = go.Figure(data=chart_map[chart_type], layout=get_base_layout(title))
    return dcc.Graph(
        id=chart_id,
        figure=fig,
        config={"displayModeBar": SHOW_MODEBAR, "responsive": True},
        style={"height": "400px"}
    )


def wrap_chart(title: str, chart: dcc.Graph) -> dbc.Card:
    """
    تغليف الرسم البياني داخل بطاقة (Card) موحدة التصميم.

    :param title: عنوان البطاقة.
    :param chart: عنصر الرسم البياني dcc.Graph.
    :return: بطاقة Bootstrap جاهزة للعرض.
    """
    return dbc.Card(
        [
            dbc.CardHeader(html.H5(title, className="mb-0")),
            dbc.CardBody([chart])
        ],
        className="mb-4 shadow-sm",
        color=BACKGROUND_COLOR,
        inverse=True
    )


def line_chart() -> dbc.Card:
    return wrap_chart("📈 الرسم الخطي", create_placeholder_chart("line", "line-chart", "الرسم الخطي"))


def bar_chart() -> dbc.Card:
    return wrap_chart("📊 الرسم العمودي", create_placeholder_chart("bar", "bar-chart", "الرسم العمودي"))


def pie_chart() -> dbc.Card:
    return wrap_chart("📉 الرسم الدائري", create_placeholder_chart("pie", "pie-chart", "الرسم الدائري"))


def scatter_chart() -> dbc.Card:
    return wrap_chart("🔘 مخطط الانتشار", create_placeholder_chart("scatter", "scatter-chart", "مخطط الانتشار"))


def box_plot() -> dbc.Card:
    return wrap_chart("📦 مخطط الصندوق", create_placeholder_chart("box", "box-plot", "مخطط الصندوق"))


def heatmap_chart() -> dbc.Card:
    return wrap_chart("🔥 الخريطة الحرارية", create_placeholder_chart("heatmap", "heatmap-chart", "الخريطة الحرارية"))


def area_chart() -> dbc.Card:
    return wrap_chart("📐 الرسم المساحي", create_placeholder_chart("area", "area-chart", "الرسم المساحي"))


def bubble_chart() -> dbc.Card:
    return wrap_chart("💬 مخطط الفقاعات", create_placeholder_chart("bubble", "bubble-chart", "مخطط الفقاعات"))


def forecast_chart() -> dbc.Card:
    return wrap_chart("⏳ الرسم التنبؤي", create_placeholder_chart("area", "forecast-chart", "الرسم التنبؤي"))


def distribution_chart() -> dbc.Card:
    return wrap_chart("📊 توزيع القيم", create_placeholder_chart("dist", "distribution-chart", "توزيع القيم"))
