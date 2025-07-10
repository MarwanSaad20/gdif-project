import os
import sys
import logging
from pathlib import Path

import dash
import dash_bootstrap_components as dbc

# ========== إعداد المسارات الأساسية ========== #
CURRENT_FILE = Path(__file__).resolve()
PROJECT_ROOT = CURRENT_FILE.parents[1]

# ✅ إضافة مجلدات المشروع إلى sys.path لتسهيل الاستيراد الديناميكي
SUBMODULES = [
    'data', 'utils', 'etl', 'analysis', 'ml_models',
    'dashboard', 'core', 'reports', 'config'
]

for sub in SUBMODULES:
    sub_path = PROJECT_ROOT / 'data_intelligence_system' / sub
    if str(sub_path) not in sys.path:
        sys.path.insert(0, str(sub_path))

# ========== استيراد التخطيط والكولباكات ========== #
# تأكد من أن مجلد المشروع الجذري في sys.path قبل الاستيراد
PROJECT_PARENT = PROJECT_ROOT.parent
if str(PROJECT_PARENT) not in sys.path:
    sys.path.insert(0, str(PROJECT_PARENT))

# إضافة المسار الجذري للمشروع (حيث يوجد data_intelligence_system) إلى sys.path
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from data_intelligence_system.dashboard.layouts.main_layout import get_layout
from data_intelligence_system.dashboard.callbacks.layout_callbacks import register_layout_callbacks
from data_intelligence_system.dashboard.callbacks.upload_callbacks import register_upload_callbacks
from data_intelligence_system.dashboard.callbacks.charts_callbacks import register_charts_callbacks
from data_intelligence_system.dashboard.callbacks.export_callbacks import register_export_callbacks
from data_intelligence_system.dashboard.callbacks.kpi_callbacks import register_kpi_callbacks  # ✅ كولباك KPIs الثابتة

# ========== إعداد سجل التشغيل (Logging) ========== #
LOG_LEVEL = logging.DEBUG if os.getenv("ENV", "development").lower() == "development" else logging.INFO
logger = logging.getLogger("GDIF")
logger.setLevel(LOG_LEVEL)

# إزالة أي معالجات سابقة (Handlers) لتجنب التكرار
if logger.hasHandlers():
    logger.handlers.clear()

stream_handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter(
    "[%(asctime)s] %(levelname)s in %(module)s: %(message)s",
    datefmt="%H:%M:%S"
)
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
register_kpi_callbacks(app)         # ✅ الكولباك الخاص بالـ KPIs الثابتة
register_export_callbacks(app)

logger.info("✅ تم تسجيل جميع الكولباكات بنجاح.")

# ========== تشغيل التطبيق محليًا ========== #
if __name__ == "__main__":
    PORT = int(os.getenv("PORT", 8050))
    IS_DEV = os.getenv("ENV", "development").lower() == "development"

    logger.info(f"🌐 التطبيق يعمل على: http://127.0.0.1:{PORT} | الوضع: {'تطوير' if IS_DEV else 'إنتاج'}")

    app.run(
        debug=IS_DEV,
        port=PORT,
        use_reloader=IS_DEV,
        host="127.0.0.1"
    )
