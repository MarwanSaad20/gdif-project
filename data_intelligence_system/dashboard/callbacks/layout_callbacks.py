from dash import Input, Output, State, html, no_update
from dash.exceptions import PreventUpdate

from data_intelligence_system.utils.logger import get_logger  # ✅ نظام تسجيل موحد

logger = get_logger("LayoutCallbacks")  # ⬅️ تخصيص اسم للّوجر

# القيم الافتراضية لتصميم الشريط الجانبي
SIDEBAR_DEFAULT_WIDTH = "250px"
SIDEBAR_DEFAULT_STYLE = {'display': 'block', 'width': SIDEBAR_DEFAULT_WIDTH}


def register_layout_callbacks(app):
    """
    ✅ تسجيل كولباكات التحكم بتخطيط الواجهة الموحدة (single-page app).
    يشمل:
    - إظهار/إخفاء الشريط الجانبي.
    - تفعيل زر التحليل الكامل بعد رفع ملف.
    - إعادة تهيئة واجهة التخطيط (مسح الرسائل أو التفريغ) مستقبلًا.
    """

    @app.callback(
        Output('sidebar-col', 'style'),
        Input('toggle-sidebar-btn', 'n_clicks'),
        State('sidebar-col', 'style'),
        prevent_initial_call=True
    )
    def toggle_sidebar(n_clicks, current_style):
        """
        إظهار/إخفاء القائمة الجانبية باستخدام زر التنقل العلوي.
        """
        if not isinstance(current_style, dict):
            current_style = SIDEBAR_DEFAULT_STYLE.copy()

        current_display = current_style.get('display', 'block')
        new_display = 'none' if current_display == 'block' else 'block'

        new_style = current_style.copy()
        new_style['display'] = new_display
        new_style['width'] = SIDEBAR_DEFAULT_WIDTH if new_display == 'block' else '0px'

        logger.info(f"✅ تبديل الشريط الجانبي إلى: {new_display}")
        return new_style

    # ✅ تفعيل زر التحليل الكامل تلقائيًا بعد رفع ملف صالح
    @app.callback(
        Output("run-full-analysis-btn", "disabled"),
        Input("store_raw_data_path", "data"),
        prevent_initial_call=True
    )
    def enable_analysis_button_if_data_uploaded(path):
        """
        إذا تم رفع ملف وحُفظ المسار بنجاح → فعّل زر التحليل.
        """
        if path:
            logger.info("🟢 تم رفع ملف بنجاح - زر التحليل أصبح مفعلًا.")
            return False  # الزر غير معطل
        return True  # الزر يبقى معطلًا

    # ✅ كولباك مستقبلي لإعادة ضبط التخطيط أو إفراغ مكونات معينة إن لزم
    @app.callback(
        Output('full-analysis-status', 'children', allow_duplicate=True),
        Input('clear-layout-btn', 'n_clicks'),
        prevent_initial_call=True
    )
    def clear_layout(n_clicks):
        """
        (اختياري) مسح الرسائل أو إعادة تعيين التخطيط – مخصص لتوسعة مستقبلية.
        """
        logger.info("🔄 تم تنفيذ إعادة التهيئة الجزئية للتخطيط.")
        return no_update
