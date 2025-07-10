import pandas as pd
from dash import Input, Output, State, html
from dash.exceptions import PreventUpdate

from data_intelligence_system.core.data_bindings import json_to_df, df_to_dash_json, filter_data_by_date
from data_intelligence_system.utils.logger import get_logger
from data_intelligence_system.utils.preprocessing import fill_missing_values

logger = get_logger("FiltersCallbacks")


def register_filters_callbacks(app):
    """
    تسجيل كولباكات التصفية الديناميكية المتكاملة مع التخزين الموحد (stored-data).
    """

    def _validate_df(stored_json, required_columns=None):
        df = json_to_df(stored_json)
        if df is None or df.empty:
            logger.warning("📭 البيانات الأصلية غير متوفرة أو فارغة.")
            raise PreventUpdate
        if required_columns:
            missing = [col for col in required_columns if col not in df.columns]
            if missing:
                logger.warning(f"⚠️ الأعمدة المطلوبة غير موجودة: {missing}")
                raise PreventUpdate
        return fill_missing_values(df)

    @app.callback(
        Output('filtered-data-store', 'data'),
        Input('filter-dropdown-category', 'value'),
        Input('filter-date-range', 'start_date'),
        Input('filter-date-range', 'end_date'),
        State('stored-data', 'data'),
        prevent_initial_call=True
    )
    def filter_by_category_and_date(category_value, start_date, end_date, stored_json):
        try:
            df = _validate_df(stored_json, required_columns=['category', 'date'])

            # تصفية حسب الفئة
            if category_value:
                df = df[df['category'].astype(str) == str(category_value)]

            # تصفية حسب التاريخ
            df = filter_data_by_date(df, start_date=start_date, end_date=end_date, date_column='date')

            if df.empty:
                logger.info("ℹ️ لا توجد بيانات بعد الفلترة.")
                return df_to_dash_json(None)

            return df_to_dash_json(df)

        except PreventUpdate:
            raise
        except Exception as e:
            logger.exception(f"❌ خطأ أثناء الفلترة حسب الفئة والتاريخ: {e}")
            return df_to_dash_json(None)

    @app.callback(
        Output('filter-dropdown-category', 'options'),
        Input('stored-data', 'data')
    )
    def update_category_options(stored_json):
        df = json_to_df(stored_json)
        if df is None or 'category' not in df.columns:
            logger.warning("⚠️ عمود 'category' غير متاح.")
            return []

        categories = df['category'].dropna().unique()
        options = [{'label': str(cat), 'value': cat} for cat in sorted(set(map(str, categories)))]
        logger.info(f"✅ تم تحديث الفئات: {len(options)} خيار.")
        return options

    @app.callback(
        Output('filtered-count', 'children'),
        Input('filtered-data-store', 'data')
    )
    def show_filtered_count(data_json):
        df = json_to_df(data_json)
        if df is None or df.empty:
            return html.Span("عدد العناصر: 0", style={"color": "gray"})
        return html.Span(f"عدد العناصر بعد التصفية: {len(df):,}", style={"color": "#00cc96"})

    @app.callback(
        Output('export-btn', 'disabled'),
        Input('filtered-data-store', 'data')
    )
    def toggle_export(data_json):
        df = json_to_df(data_json)
        disabled = df is None or df.empty
        logger.debug(f"🧩 حالة زر التصدير: {'معطل' if disabled else 'مفعل'}")
        return disabled

    @app.callback(
        Output('filtered-data-multi', 'data'),
        Input('filter-multi-select', 'value'),
        State('stored-data', 'data'),
        prevent_initial_call=True
    )
    def filter_by_type_multi(selected, stored_json):
        if not selected:
            logger.info("⚠️ لا توجد قيم محددة للنوع.")
            return df_to_dash_json(None)
        try:
            df = _validate_df(stored_json, required_columns=['type'])
            filtered = df[df['type'].isin(selected)]
            if filtered.empty:
                logger.info("ℹ️ الفلترة حسب النوع لم تُرجع بيانات.")
                return df_to_dash_json(None)
            return df_to_dash_json(filtered)
        except PreventUpdate:
            raise
        except Exception as e:
            logger.warning(f"⚠️ فشل الفلترة حسب النوع: {e}", exc_info=True)
            return df_to_dash_json(None)

    @app.callback(
        Output('filtered-multi-count', 'children'),
        Input('filtered-data-multi', 'data')
    )
    def show_multi_filter_count(data_json):
        df = json_to_df(data_json)
        if df is None or df.empty:
            return html.Span("عدد العناصر حسب النوع: 0", style={"color": "gray"})
        return html.Span(f"عدد العناصر حسب النوع: {len(df):,}", style={"color": "#1E90FF"})

    @app.callback(
        Output('filter-dropdown-category', 'value'),
        Output('filter-date-range', 'start_date'),
        Output('filter-date-range', 'end_date'),
        Output('filter-multi-select', 'value'),
        Input('reset-filters-btn', 'n_clicks'),
        prevent_initial_call=True
    )
    def reset_all_filters(n_clicks):
        logger.info("🔄 تم إعادة تعيين جميع الفلاتر.")
        return None, None, None, []
