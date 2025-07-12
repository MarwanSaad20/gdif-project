"""
🚀 GDIF Dashboard Application Entry Point
Author: Your Name
Description: Initializes the Dash app, registers callbacks, and runs the server.
"""

import os
import sys
import logging
from pathlib import Path

import dash
import dash_bootstrap_components as dbc

# ✅ استيراد إعدادات النظام المركزية
from data_intelligence_system.config.config_loader import CONFIG

# ========== إعداد المسارات الأساسية ========== #
def configure_sys_path():
    current_file = Path(__file__).resolve()
    project_root = current_file.parents[1]
    project_parent = project_root.parent

    submodules = [
        'data', 'utils', 'etl', 'analysis', 'ml_models',
        'dashboard', 'core', 'reports', 'config'
    ]

    for sub in submodules:
        sub_path = project_root / 'data_intelligence_system' / sub
        if str(sub_path) not in sys.path:
            sys.path.insert(0, str(sub_path))

    for path in [project_root, project_parent]:
        if str(path) not in sys.path:
            sys.path.insert(0, str(path))

configure_sys_path()

# ========== استيراد التخطيط والكولباكات ========== #
from data_intelligence_system.dashboard.layouts.main_layout import get_layout
from data_intelligence_system.dashboard.callbacks.layout_callbacks import register_layout_callbacks
from data_intelligence_system.dashboard.callbacks.upload_callbacks import register_upload_callbacks
from data_intelligence_system.dashboard.callbacks.charts_callbacks import register_charts_callbacks
from data_intelligence_system.dashboard.callbacks.export_callbacks import register_export_callbacks
from data_intelligence_system.dashboard.callbacks.kpi_callbacks import register_kpi_callbacks
from data_intelligence_system.dashboard.callbacks.filters_callbacks import register_filters_callbacks  # ✅ جديد

# ========== إعداد سجل التشغيل (Logging) ========== #
env_mode = CONFIG.env.ENV_MODE or "development"
log_level = logging.DEBUG if env_mode == "development" else logging.INFO
logger = logging.getLogger("GDIF")
logger.setLevel(log_level)

if logger.hasHandlers():
    logger.handlers.clear()

stream_handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter("[%(asctime)s] %(levelname)s in %(module)s: %(message)s", datefmt="%H:%M:%S")
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)

logger.info("🚀 بدء تشغيل تطبيق GDIF - نظام تحليل البيانات العام")

# ========== إنشاء تطبيق Dash ========== #
external_stylesheets = [dbc.themes.DARKLY]

app = dash.Dash(
    __name__,
    server=True,
    external_stylesheets=external_stylesheets,
    suppress_callback_exceptions=True,
    title="نظام تحليل البيانات العام - GDIF",
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1"},
        {"name": "theme-color", "content": "#0A0F1A"},
        {"charset": "UTF-8"}
    ]
)

server = app.server

# ========== تعيين التخطيط الرئيسي ========== #
app.layout = get_layout()

# ========== تسجيل جميع الكولباكات ========== #
register_layout_callbacks(app)
register_upload_callbacks(app)
register_charts_callbacks(app)
register_kpi_callbacks(app)
register_export_callbacks(app)
register_filters_callbacks(app)  # ✅ جديد

logger.info("✅ تم تسجيل جميع الكولباكات بنجاح.")

# ========== تشغيل التطبيق محليًا ========== #
if __name__ == "__main__":
    port = int(getattr(CONFIG.env, "DASHBOARD_PORT", 8050))
    is_dev = env_mode == "development"

    logger.info(f"🌐 التطبيق يعمل على: http://127.0.0.1:{port} | الوضع: {'تطوير' if is_dev else 'إنتاج'}")

    try:
        app.run(
            debug=is_dev,
            port=port,
            use_reloader=is_dev,
            host="127.0.0.1"
        )
    except Exception as e:
        logger.exception(f"❌ خطأ أثناء تشغيل التطبيق: {e}")
