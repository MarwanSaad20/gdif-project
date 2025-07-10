import logging
import pandas as pd
from dash import Input, Output, html
from dash.exceptions import PreventUpdate

from data_intelligence_system.dashboard.components import indicators

logger = logging.getLogger(__name__)

def parse_data(data_json: str) -> pd.DataFrame:
    """تحويل JSON إلى DataFrame أو إيقاف التنفيذ عند الفشل."""
    if not data_json:
        logger.warning("📭 لا توجد بيانات مخزنة")
        raise PreventUpdate
    try:
        df = pd.read_json(data_json, orient="split")
        if df.empty:
            logger.warning("📭 بيانات مفرغة داخل DataFrame")
            raise PreventUpdate
        return df
    except Exception as e:
        logger.error(f"❌ فشل في فك تشفير البيانات: {e}", exc_info=True)
        raise PreventUpdate


def register_kpi_callbacks(app):
    """
    كولباك موحد لتحديث جميع KPIs.
    يحسن الأداء ويقلل عدد الكولباكات المنفصلة.
    """
    @app.callback(
        Output("kpi-total-samples-value", "children"),
        Output("kpi-null-values-value", "children"),
        Output("kpi-avg-value-value", "children"),
        Output("kpi-growth-rate-value", "children"),
        Output("kpi-next-forecast-value", "children"),
        Input("store_raw_data", "data")
    )
    def update_kpi_cards(data_json):
        df = parse_data(data_json)

        total = len(df)
        nulls = df.isnull().sum().sum()
        numeric_df = df.select_dtypes(include="number")
        avg_val = numeric_df.mean().mean() if not numeric_df.empty else None

        try:
            growth_rate = ((len(df) - 1) / len(df)) * 100 if len(df) > 1 else 0
        except ZeroDivisionError:
            growth_rate = 0

        forecast_status = "🔮 سيتم التنبؤ لاحقًا"

        return (
            f"{total:,}",
            f"{nulls:,}",
            f"{avg_val:,.2f}" if avg_val is not None else "N/A",
            f"{growth_rate:.2f}%" if growth_rate else "N/A",
            forecast_status
        )


def generate_kpi_cards_layout() -> html.Div:
    """
    إنشاء مكونات بطاقات KPI بشكل احترافي.
    """
    card_config = [
        {
            "id": "kpi-total-samples",
            "title": "إجمالي العينات",
            "icon": "fa fa-database",
            "tooltip": "عدد الصفوف في مجموعة البيانات",
            "color": "#00cc96",
        },
        {
            "id": "kpi-null-values",
            "title": "القيم الفارغة",
            "icon": "fa fa-exclamation-triangle",
            "tooltip": "عدد القيم الفارغة في البيانات",
            "color": "#ff6347",
        },
        {
            "id": "kpi-avg-value",
            "title": "متوسط القيم الرقمية",
            "icon": "fa fa-calculator",
            "tooltip": "متوسط الأعمدة الرقمية في البيانات",
            "color": "#1E90FF",
        },
        {
            "id": "kpi-growth-rate",
            "title": "معدل النمو",
            "icon": "fa fa-chart-line",
            "tooltip": "معدل نمو الصفوف - افتراضي",
            "color": "#ffa500",
        },
        {
            "id": "kpi-next-forecast",
            "title": "التنبؤ القادم",
            "icon": "fa fa-bullseye",
            "tooltip": "قيمة التنبؤ التالي إن توفر",
            "color": "#9932CC",
        },
    ]

    cards = [
        indicators.create_kpi_card(
            id=conf["id"],
            title=conf["title"],
            icon=conf["icon"],
            tooltip=conf["tooltip"],
            color=conf["color"],
            style={"margin": "10px"},
        )
        for conf in card_config
    ]

    return html.Div(
        children=cards,
        style={
            "display": "flex",
            "flexWrap": "wrap",
            "justifyContent": "space-around",
            "gap": "10px",
            "marginTop": "20px",
            "padding": "10px",
        }
    )
