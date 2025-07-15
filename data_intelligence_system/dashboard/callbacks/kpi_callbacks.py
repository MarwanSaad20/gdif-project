import pandas as pd
from dash import Input, Output
from dash.exceptions import PreventUpdate
from io import StringIO  # إضافة هذه السطر

from data_intelligence_system.utils.logger import get_logger
from data_intelligence_system.utils.preprocessing import fill_missing_values
from data_intelligence_system.dashboard.components.indicators import create_kpi_card, create_kpi_container

logger = get_logger("KPICallbacks")


def parse_data(data_json):
    """
    تحويل JSON مخزن إلى DataFrame مع معالجة القيم المفقودة.
    """
    if not data_json:
        logger.warning("📭 لا توجد بيانات مخزنة")
        raise PreventUpdate
    try:
        # تعديل هنا لاستخدام StringIO لتجنب التحذير
        df = pd.read_json(StringIO(data_json), orient="split")
        if df.empty:
            logger.info("⚠️ DataFrame الناتج فارغ بعد فك التشفير.")
            raise PreventUpdate
        df = fill_missing_values(df)
        return df
    except Exception as e:
        logger.error(f"❌ فشل في فك تشفير البيانات: {e}", exc_info=True)
        raise PreventUpdate


def update_kpi_cards_func(df: pd.DataFrame):
    """
    دالة مستقلة لمعالجة DataFrame وإرجاع قيم بطاقات KPI.
    """
    total = len(df)
    nulls = df.isnull().sum().sum()

    numeric_df = df.select_dtypes(include="number")
    avg_val = numeric_df.mean().mean() if not numeric_df.empty else None

    growth_rate = ((total - 1) / total) * 100 if total > 1 else 0
    forecast_status = "🔮 سيتم التنبؤ لاحقًا"

    return (
        f"{total:,}",
        f"{nulls:,}",
        f"{avg_val:,.2f}" if avg_val is not None else "N/A",
        f"{growth_rate:.2f}%" if growth_rate else "N/A",
        forecast_status
    )


def register_kpi_callbacks(app):
    """
    تسجيل كولباكات تحديث بطاقات KPI في لوحة المعلومات.
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
        return update_kpi_cards_func(df)
