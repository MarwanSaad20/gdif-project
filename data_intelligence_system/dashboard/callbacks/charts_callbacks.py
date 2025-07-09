import pandas as pd
from dash import Input, Output, html
from dash.exceptions import PreventUpdate

from data_intelligence_system.dashboard.components import charts, indicators
from data_intelligence_system.core.data_bindings import json_to_df
from data_intelligence_system.data.external.external_data_utils import (
    drop_empty_rows,
    drop_empty_columns,
    standardize_column_names,
    remove_duplicates,
    convert_column_types,
    filter_rows_by_condition,
    sample_data,
    describe_data,
)
from data_intelligence_system.utils.data_loader import load_data
from data_intelligence_system.utils.preprocessing import fill_missing_values
from data_intelligence_system.utils.visualization.visuals_static import plot_distribution
from data_intelligence_system.analysis.correlation_analysis import generate_correlation_matrix
from data_intelligence_system.analysis.outlier_detection import detect_outliers_iqr
from data_intelligence_system.analysis.target_relation_analysis import analyze_target_relation
from data_intelligence_system.ml_models.regression.ridge_regression import RidgeRegressionModel
from data_intelligence_system.ml_models.classification.logistic_regression import LogisticRegressionModel
from data_intelligence_system.ml_models.classification.random_forest import RandomForestModel
from data_intelligence_system.utils.logger import get_logger

import matplotlib.pyplot as plt
from pathlib import Path
import uuid

logger = get_logger("ChartsCallback")


def filter_numeric_df(df: pd.DataFrame) -> pd.DataFrame:
    numeric_df = df.select_dtypes(include="number")
    return numeric_df if not numeric_df.empty else pd.DataFrame()


def sanitize_id(name: str) -> str:
    return name.strip().lower().replace(" ", "_").replace(".", "").replace("-", "_")


def register_charts_callbacks(app):
    @app.callback(
        Output("data-table", "data"),
        Output("data-table", "columns"),
        Output("line-chart", "figure"),
        Output("bar-chart", "figure"),
        Output("pie-chart", "figure"),
        Output("stats-summary-pre", "children"),
        Output("kpi-container", "children"),
        Input("store_raw_data", "data"),
        prevent_initial_call=True,
    )
    def update_charts(stored_json):
        if not stored_json:
            raise PreventUpdate

        df = json_to_df(stored_json)
        if df is None or df.empty:
            logger.warning("⚠️ البيانات غير صالحة أو فارغة.")
            return [], [], {}, {}, {}, "", []

        try:
            df = drop_empty_rows(df)
            df = drop_empty_columns(df)
            df = standardize_column_names(df)
            df = fill_missing_values(df)
            df = remove_duplicates(df)

            outliers_mask = detect_outliers_iqr(df)
            outliers_count = outliers_mask.sum()
            logger.info(f"✅ تم اكتشاف {outliers_count} صف شاذ باستخدام IQR")

            try:
                relation_summary = analyze_target_relation(df, target="target")
                logger.info(f"📊 تحليل العلاقة مع الهدف:\n{relation_summary}")
            except Exception as e:
                logger.warning(f"⚠️ فشل تحليل العلاقة مع الهدف: {e}")

            table_data = df.to_dict("records")
            table_columns = [{"name": str(col), "id": str(col)} for col in df.columns]

            numeric_df = filter_numeric_df(df)
            if numeric_df.empty:
                raise ValueError("❌ لا توجد أعمدة رقمية صالحة للتحليل.")

            try:
                corr_matrix = generate_correlation_matrix(df)
                logger.info(f"✅ مصفوفة الارتباط المحسوبة:\n{corr_matrix}")
            except Exception as e:
                logger.warning(f"⚠️ فشل في حساب مصفوفة الارتباط: {e}")
                corr_matrix = pd.DataFrame()

            date_col = next((col for col in df.columns if str(col).lower() == "date"), None)
            if date_col:
                df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
                df = df.dropna(subset=[date_col])
                x_axis = df[date_col].dt.strftime('%Y-%m-%d').tolist()
            else:
                x_axis = list(range(len(df)))

            y_axis = numeric_df.columns[0]

            line_graph_figure = charts.create_line_chart(
                x_data=x_axis,
                y_data=df[y_axis].fillna(0).tolist(),
                title=f"الرسم الخطي - {y_axis}",
                colors={"line": "#1E90FF"},
                height=400,
            )

            bar_graph_figure = charts.create_bar_chart(
                categories=numeric_df.columns.tolist(),
                values=[numeric_df[col].mean() for col in numeric_df.columns],
                title="الرسم العمودي - المتوسطات",
                colors={"bar": "#FF4500"},
                height=400,
            )

            pie_graph_figure = {}
            cat_df = df.select_dtypes(include=["object", "category"])
            if not cat_df.empty:
                first_cat = cat_df.columns[0]
                counts = df[first_cat].value_counts().nlargest(6)
                pie_graph_figure = charts.create_pie_chart(
                    labels=counts.index.tolist(),
                    values=counts.values.tolist(),
                    title=f"الرسم الدائري - {first_cat}",
                    colors={"pie_colors": ["#636efa", "#EF553B", "#00cc96", "#ab63fa", "#ffa15a", "#19d3f3"]},
                    height=400,
                )

            stats_summary = describe_data(df).to_string()

            palette = ["#00cc96", "#1E90FF", "#9932CC", "#ff6347", "#ffa500"]
            kpi_cards = [
                indicators.create_kpi_card(
                    id=f"kpi-{sanitize_id(col)}",
                    title=col,
                    value=f"{numeric_df[col].mean():,.2f}",
                    icon="fa fa-chart-bar",
                    color=palette[i % len(palette)],
                    style={"margin": "6px"}
                )
                for i, col in enumerate(numeric_df.columns)
            ]

            kpi_div = html.Div(
                children=kpi_cards,
                style={
                    "display": "flex",
                    "flexWrap": "wrap",
                    "gap": "10px",
                    "padding": "10px",
                    "justifyContent": "center"
                }
            )

            logger.info("✅ تم عرض الرسوم البيانية والبطاقات بنجاح.")
            return (
                table_data,
                table_columns,
                line_graph_figure,
                bar_graph_figure,
                pie_graph_figure,
                stats_summary,
                kpi_div,
            )

        except Exception as e:
            logger.exception(
                f"❌ خطأ أثناء تحليل البيانات: Columns: {list(df.columns)}, "
                f"Numeric: {list(numeric_df.columns) if 'numeric_df' in locals() else 'N/A'}, Error: {e}"
            )
            return [], [], {}, {}, {}, "", []
