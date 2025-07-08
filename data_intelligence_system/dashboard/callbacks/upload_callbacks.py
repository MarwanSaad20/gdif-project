from dash import Input, Output, State, callback_context, html, dash
from dash.exceptions import PreventUpdate

from data_intelligence_system.utils.logger import get_logger
from data_intelligence_system.utils.data_loader import load_data
from data_intelligence_system.dashboard.components.upload_component import save_uploaded_file
from data_intelligence_system.core.data_bindings import df_to_dash_json
from data_intelligence_system.etl import pipeline as etl_pipeline
from data_intelligence_system.analysis.descriptive_stats import compute_statistics
from data_intelligence_system.reports import report_dispatcher

from data_intelligence_system.utils.preprocessing import fill_missing_values  # ✅ جديد

logger = get_logger("UploadCallbacks")


def register_upload_callbacks(app):
    """
    📦 كولباك موحد للتعامل مع رفع الملفات وتحليلها داخل لوحة التحكم.
    """

    @app.callback(
        Output("upload-status", "children"),
        Output("full-analysis-status", "children"),
        Output("store_raw_data", "data", allow_duplicate=True),
        Output("store_raw_data_path", "data", allow_duplicate=True),
        Output("run-full-analysis-btn", "disabled", allow_duplicate=True),
        Input("upload-data", "contents"),
        Input("run-full-analysis-btn", "n_clicks"),
        State("upload-data", "filename"),
        State("store_raw_data_path", "data"),
        prevent_initial_call=True,
    )
    def unified_upload_and_analysis(upload_contents, run_analysis_clicks, filename, last_uploaded_path):
        triggered_id = callback_context.triggered_id

        # 📁 [1] عملية رفع الملف
        if triggered_id == "upload-data":
            if not upload_contents or not filename:
                raise PreventUpdate

            try:
                save_path = save_uploaded_file(upload_contents, filename)

                df = load_data(str(save_path))
                df = fill_missing_values(df)  # ✅ تنظيف بعد التحميل

                if df.empty or df.shape[1] == 0:
                    msg = f"⚠️ الملف {filename} لا يحتوي على بيانات!"
                    logger.warning(msg)
                    return html.Div(msg, style={"color": "orange"}), dash.no_update, None, None, True

                if any(str(col).strip() == "" for col in df.columns):
                    msg = "⚠️ الملف يحتوي على أعمدة بدون أسماء. يرجى التحقق."
                    logger.warning(msg)
                    return html.Div(msg, style={"color": "orange"}), dash.no_update, None, None, True

                logger.info(f"✅ تم رفع الملف وحفظه: {save_path}")
                msg = f"✅ تم رفع الملف — الصفوف: {len(df):,}، الأعمدة: {len(df.columns)}"

                return (
                    html.Div(msg, style={"color": "green"}),
                    dash.no_update,
                    df_to_dash_json(df),
                    str(save_path),
                    False,
                )

            except Exception as e:
                logger.exception("❌ فشل أثناء رفع الملف")
                return (
                    html.Div(f"❌ خطأ أثناء رفع الملف: {e}", style={"color": "red"}),
                    dash.no_update,
                    None,
                    None,
                    True,
                )

        # 🧠 [2] تشغيل التحليل الكامل
        elif triggered_id == "run-full-analysis-btn":
            if not run_analysis_clicks or not last_uploaded_path:
                return (
                    dash.no_update,
                    html.Div("⚠️ لا يوجد ملف لتحليله. يرجى رفع ملف أولاً.", style={"color": "orange"}),
                    None,
                    None,
                    dash.no_update,
                )

            try:
                logger.info(f"🚀 بدء التحليل الكامل من: {last_uploaded_path}")
                df = load_data(str(last_uploaded_path))
                df = fill_missing_values(df)  # ✅ تنظيف قبل التحليل

                if df.empty:
                    return (
                        dash.no_update,
                        html.Div("⚠️ الملف المرفوع فارغ.", style={"color": "orange"}),
                        None,
                        last_uploaded_path,
                        dash.no_update,
                    )

                etl_pipeline.run(df)
                logger.info("✅ ETL اكتمل بنجاح.")

                compute_statistics(df)
                logger.info("📊 التحليل الإحصائي تم بنجاح.")

                report_dispatcher.generate_reports(
                    df,
                    {
                        "pdf_filename": "data_report",
                        "pdf_title": "تقرير البيانات التحليلي",
                        "excel_filename": "data_export",
                        "html_filename": "data_view",
                    },
                )
                logger.info("📄 التقارير تم توليدها بنجاح.")

                final_msg = html.Div(
                    [
                        html.Div("✅ تم تنفيذ التحليل الكامل بنجاح!",
                                 style={"color": "green", "fontWeight": "bold", "marginBottom": "10px"}),
                        html.Div("🧠 التحليل شمل كل الأعمدة الممكنة بغض النظر عن نوعها.",
                                 style={"color": "#2980b9"}),
                        html.Div("🔍 الأعمدة غير القابلة للتحليل تم تجاوزها تلقائيًا.",
                                 style={"color": "#f39c12"}),
                    ]
                )

                return dash.no_update, final_msg, df_to_dash_json(df), last_uploaded_path, dash.no_update

            except Exception as e:
                logger.exception("❌ خطأ أثناء التحليل الكامل")
                return (
                    dash.no_update,
                    html.Div(f"❌ خطأ أثناء التحليل الكامل: {e}", style={"color": "red"}),
                    None,
                    last_uploaded_path,
                    dash.no_update,
                )

        raise PreventUpdate
