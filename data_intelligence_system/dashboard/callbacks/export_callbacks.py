import pandas as pd
import uuid
from dash import Input, Output, State
from dash.exceptions import PreventUpdate
from dash.dcc import send_bytes

from data_intelligence_system.reports.report_dispatcher import generate_report
from data_intelligence_system.utils.logger import get_logger
from data_intelligence_system.utils.preprocessing import fill_missing_values  # ✅ جديد

logger = get_logger("ExportCallback")


def register_export_callbacks(app):
    """
    تسجيل كولباك توليد وتحميل التقرير بناءً على البيانات المخزنة أو المفلترة.
    """

    def is_json_empty(data_json):
        return not data_json or str(data_json).strip() in ("", "{}", "null")

    def get_available_json_data(filtered_json, stored_json):
        """ترجيح البيانات المفلترة أولًا ثم العامة."""
        if not is_json_empty(filtered_json):
            return filtered_json
        if not is_json_empty(stored_json):
            return stored_json
        return None

    @app.callback(
        Output("download-report", "data"),
        Input("download-btn", "n_clicks"),
        State("filtered-data-store", "data"),
        State("stored-data", "data"),
        State("report-format-dropdown", "value"),
        prevent_initial_call=True
    )
    def download_report(n_clicks, filtered_data_json, stored_data_json, report_format):
        logger.info("⬇️ بدء عملية توليد التقرير للتصدير ...")

        data_json = get_available_json_data(filtered_data_json, stored_data_json)
        if is_json_empty(data_json):
            logger.warning("⚠️ لا توجد بيانات متاحة لإنشاء التقرير.")
            raise PreventUpdate

        if not report_format:
            logger.warning("⚠️ لم يتم اختيار صيغة التقرير.")
            raise PreventUpdate

        supported_formats = {"pdf", "excel", "html", "csv"}
        report_format = report_format.lower()

        if report_format not in supported_formats:
            logger.warning(f"⚠️ نوع التقرير '{report_format}' غير مدعوم.")
            raise PreventUpdate

        try:
            df = pd.read_json(data_json, orient="split")
            if df.empty:
                logger.warning("⚠️ البيانات المحولة فارغة.")
                raise PreventUpdate

            # ✅ معالجة القيم المفقودة باستخدام النظام الجديد
            df = fill_missing_values(df)

        except Exception as e:
            logger.error(f"❌ فشل في تحويل JSON إلى DataFrame أو معالجته: {e}", exc_info=True)
            raise PreventUpdate

        try:
            timestamp = pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')
            unique_id = uuid.uuid4().hex[:6]
            config = {
                "filename": f"data_report_{timestamp}_{unique_id}",
                "title": "تقرير البيانات العام",
                "cover_image": None
            }

            output_bytes, filename = generate_report(
                data=df,
                report_type=report_format,
                config=config
            )

            if not output_bytes or not filename:
                logger.error("❌ الدالة generate_report لم تُرجع بيانات صالحة.")
                raise PreventUpdate

            mime_types = {
                "pdf": "application/pdf",
                "excel": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                "html": "text/html",
                "csv": "text/csv"
            }
            mime_type = mime_types[report_format]

            logger.info(f"📄 تم توليد التقرير بنجاح: {filename}")
            return send_bytes(output_bytes, filename=filename, mime_type=mime_type)

        except Exception as e:
            logger.error(f"❌ خطأ أثناء توليد التقرير: {e}", exc_info=True)
            raise PreventUpdate
