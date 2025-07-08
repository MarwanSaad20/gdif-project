import pandas as pd
from dash import Input, Output
from dash.exceptions import PreventUpdate

from data_intelligence_system.utils.logger import get_logger  # ✅ نظام تسجيل موحد
from data_intelligence_system.dashboard.components import indicators
from data_intelligence_system.utils.preprocessing import fill_missing_values  # ✅ جديد

logger = get_logger("KPICallbacks")  # ⬅️ تخصيص اسم لوجر مميز


def parse_data(data_json):
    if not data_json:
        logger.warning("📭 لا توجد بيانات مخزنة")
        raise PreventUpdate
    try:
        df = pd.read_json(data_json, orient="split")
        if df.empty:
            raise PreventUpdate
        df = fill_missing(df)  # ✅ معالجة القيم المفقودة قبل التحليل
        return df
    except Exception as e:
        logger.error(f"❌ فشل في فك تشفير البيانات: {e}", exc_info=True)
        raise PreventUpdate


def register_kpi_callbacks(app):
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
        growth_rate = ((len(df) - 1) / len(df)) * 100 if len(df) > 1 else 0
        forecast_status = "🔮 سيتم التنبؤ لاحقًا"
        return (
            f"{total:,}",
            f"{nulls:,}",
            f"{avg_val:,.2f}" if avg_val is not None else "N/A",
            f"{growth_rate:.2f}%" if growth_rate else "N/A",
            forecast_status
        )
