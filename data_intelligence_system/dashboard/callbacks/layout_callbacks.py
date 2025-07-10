from dash import Input, Output, State, no_update
from dash.exceptions import PreventUpdate

from data_intelligence_system.utils.logger import get_logger  # نظام تسجيل موحد

logger = get_logger("LayoutCallbacks")  # تخصيص اسم للوجر

# الثوابت الافتراضية لتصميم الشريط الجانبي
SIDEBAR_DEFAULT_WIDTH = "250px"
SIDEBAR_DEFAULT_STYLE = {'display': 'block', 'width': SIDEBAR_DEFAULT_WIDTH}


def register_layout_callbacks(app):
    """
    تسجيل كولباكات التحكم بتخطيط الواجهة الموحدة (single-page app).

    تشمل:
    - إظهار/إخفاء الشريط الجانبي.
    - تفعيل زر التحليل الكامل بعد رفع ملف.
    - إعادة تهيئة واجهة التخطيط (مسح الرسائل أو التفريغ) مستقبلًا.

    Parameters:
        app (dash.Dash): كائن التطبيق الذي سيتم تسجيل الكولباكات عليه.
    """

    @app.callback(
        Output('sidebar-col', 'style'),
        Input('toggle-sidebar-btn', 'n_clicks'),
        State('sidebar-col', 'style'),
        prevent_initial_call=True
    )
    def toggle_sidebar(n_clicks: int, current_style: dict | None) -> dict:
        """
        تبديل حالة إظهار/إخفاء القائمة الجانبية باستخدام زر التنقل.

        Args:
            n_clicks (int): عدد مرات النقر على زر التبديل.
            current_style (dict | None): النمط الحالي للشريط الجانبي.

        Returns:
            dict: النمط الجديد للشريط الجانبي.
        """
        if not isinstance(current_style, dict):
            current_style = SIDEBAR_DEFAULT_STYLE.copy()

        current_display = current_style.get('display', 'block')
        new_display = 'none' if current_display == 'block' else 'block'

        new_style = current_style.copy()
        new_style['display'] = new_display
        new_style['width'] = SIDEBAR_DEFAULT_WIDTH if new_display == 'block' else '0px'

        logger.info(f"تبديل الشريط الجانبي إلى: {new_display}")
        return new_style

    @app.callback(
        Output("run-full-analysis-btn", "disabled"),
        Input("store_raw_data_path", "data"),
        prevent_initial_call=True
    )
    def enable_analysis_button_if_data_uploaded(path: str | None) -> bool:
        """
        تفعيل زر التحليل الكامل إذا تم رفع ملف وحفظ المسار بنجاح.

        Args:
            path (str | None): مسار البيانات المرفوعة.

        Returns:
            bool: False إذا تم تفعيل الزر، True إذا بقي معطلاً.
        """
        if path:
            logger.info("تم رفع ملف بنجاح - زر التحليل أصبح مفعلًا.")
            return False
        return True

    @app.callback(
        Output('full-analysis-status', 'children', allow_duplicate=True),
        Input('clear-layout-btn', 'n_clicks'),
        prevent_initial_call=True
    )
    def clear_layout(n_clicks: int | None):
        """
        إعادة تهيئة واجهة التخطيط (مسح الرسائل أو تفريغ مكونات).

        Args:
            n_clicks (int | None): عدد النقرات على زر إعادة التهيئة.

        Returns:
            dash.no_update: لا يتم تحديث المكون الحالي.
        """
        if not n_clicks:
            raise PreventUpdate
        logger.info("تم تنفيذ إعادة التهيئة الجزئية للتخطيط.")
        return no_update
