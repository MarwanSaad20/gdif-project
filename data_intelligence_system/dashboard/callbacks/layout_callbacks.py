from dash import Input, Output, State, no_update
from dash.exceptions import PreventUpdate

from data_intelligence_system.utils.logger import get_logger
from data_intelligence_system.config.dashboard_config import DEFAULT_THEME  # (للاستخدام المستقبلي لو احتجنا نمط الثيم)

logger = get_logger("LayoutCallbacks")

# الثوابت الافتراضية لتصميم الشريط الجانبي
SIDEBAR_DEFAULT_WIDTH = "250px"
SIDEBAR_DEFAULT_STYLE = {'display': 'block', 'width': SIDEBAR_DEFAULT_WIDTH}


def toggle_sidebar(n_clicks: int, current_style: dict | None) -> dict:
    """
    تبديل حالة إظهار/إخفاء القائمة الجانبية.
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


def enable_analysis_button_if_data_uploaded(path: str | None) -> bool:
    """
    تفعيل زر التحليل الكامل إذا تم رفع ملف.
    """
    if path:
        logger.info("تم رفع ملف بنجاح - زر التحليل أصبح مفعلًا.")
        return False
    return True


def clear_layout(n_clicks: int | None):
    """
    إعادة تهيئة واجهة التخطيط.
    """
    if not n_clicks:
        raise PreventUpdate
    logger.info("تم تنفيذ إعادة التهيئة الجزئية للتخطيط.")
    return no_update


def register_layout_callbacks(app):
    """
    تسجيل كولباكات التحكم بتخطيط الواجهة الموحدة.
    """
    app.callback(
        Output('sidebar-col', 'style'),
        Input('toggle-sidebar-btn', 'n_clicks'),
        State('sidebar-col', 'style'),
        prevent_initial_call=True
    )(toggle_sidebar)

    app.callback(
        Output("run-full-analysis-btn", "disabled"),
        Input("store_raw_data_path", "data"),
        prevent_initial_call=True
    )(enable_analysis_button_if_data_uploaded)

    app.callback(
        Output('full-analysis-status', 'children', allow_duplicate=True),
        Input('clear-layout-btn', 'n_clicks'),
        prevent_initial_call=True
    )(clear_layout)
