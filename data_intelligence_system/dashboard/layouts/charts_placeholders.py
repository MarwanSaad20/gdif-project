from dash import dcc, html
import dash_bootstrap_components as dbc
import plotly.graph_objects as go

# 🎨 إعدادات التصميم
BACKGROUND_COLOR = "#0A0F1A"
TEXT_COLOR = "#FFFFFF"
PRIMARY_COLOR = "#1E90FF"
MARGIN_DEFAULT = dict(l=40, r=40, t=40, b=40)
SHOW_MODEBAR = False

# 🧠 دالة توليد layout موحد مع دعم annotation
def get_base_layout(title="رسم بياني", is_placeholder=True):
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
            text="⚠️ لا توجد بيانات بعد",
            x=0.5, y=0.5, xref='paper', yref='paper',
            showarrow=False,
            font=dict(size=16, color="#AAAAAA")
        )]
    return layout

# 🧱 دالة رئيسية لتوليد الرسوم
def create_placeholder_chart(chart_type, chart_id, title):
    if chart_type == "line":
        data = [go.Scatter(x=[], y=[], mode='lines')]
    elif chart_type == "bar":
        data = [go.Bar(x=[], y=[])]
    elif chart_type == "pie":
        data = [go.Pie(labels=[], values=[], hole=0.3)]
    elif chart_type == "scatter":
        data = [go.Scatter(x=[], y=[], mode='markers')]
    elif chart_type == "box":
        data = [go.Box(y=[])]
    elif chart_type == "heatmap":
        data = [go.Heatmap(z=[[]])]
    elif chart_type == "area":
        data = [go.Scatter(x=[], y=[], fill='tozeroy')]
    elif chart_type == "bubble":
        data = [go.Scatter(x=[], y=[], mode='markers', marker=dict(size=[]))]
    else:
        raise ValueError(f"نوع الرسم غير مدعوم: {chart_type}")

    fig = go.Figure(data=data, layout=get_base_layout(title))
    return dcc.Graph(id=chart_id, figure=fig, config={"displayModeBar": SHOW_MODEBAR, "responsive": True},
                     style={"height": "400px"})

# 🧱 لف الرسوم في Card موحد
def wrap_chart(title, chart):
    return dbc.Card([
        dbc.CardHeader(html.H5(title, className="mb-0")),
        dbc.CardBody([chart])
    ], className="mb-4 shadow-sm", color=BACKGROUND_COLOR, inverse=True)

# 📦 دوال للواجهة
def line_chart():
    return wrap_chart("📈 الرسم الخطي", create_placeholder_chart("line", "line-chart", "الرسم الخطي"))

def bar_chart():
    return wrap_chart("📊 الرسم العمودي", create_placeholder_chart("bar", "bar-chart", "الرسم العمودي"))

def pie_chart():
    return wrap_chart("📉 الرسم الدائري", create_placeholder_chart("pie", "pie-chart", "الرسم الدائري"))

def scatter_chart():
    return wrap_chart("🔘 مخطط الانتشار", create_placeholder_chart("scatter", "scatter-chart", "مخطط الانتشار"))

def box_plot():
    return wrap_chart("📦 مخطط الصندوق", create_placeholder_chart("box", "box-plot", "مخطط الصندوق"))

def heatmap_chart():
    return wrap_chart("🔥 الخريطة الحرارية", create_placeholder_chart("heatmap", "heatmap-chart", "الخريطة الحرارية"))

def area_chart():
    return wrap_chart("📐 الرسم المساحي", create_placeholder_chart("area", "area-chart", "الرسم المساحي"))

def bubble_chart():
    return wrap_chart("💬 مخطط الفقاعات", create_placeholder_chart("bubble", "bubble-chart", "مخطط الفقاعات"))

def forecast_chart():
    return wrap_chart("⏳ الرسم التنبؤي", create_placeholder_chart("area", "forecast-chart", "الرسم التنبؤي"))
