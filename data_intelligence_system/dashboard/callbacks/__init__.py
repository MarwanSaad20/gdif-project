import logging

# 🧩 كولباكات منفصلة حسب الوظيفة
from .charts_callbacks import register_charts_callbacks
from .filters_callbacks import register_filters_callbacks
from .export_callbacks import register_export_callbacks
from .upload_callbacks import register_upload_callbacks
from ..layouts.kpi_cards import register_kpi_callbacks

logger = logging.getLogger(__name__)

def register_callbacks(app):
    """
    تسجيل جميع كولباكات التحليل والتفاعل داخل واجهة النظام.
    يشمل رفع البيانات، الفلاتر، الرسوم البيانية، تصدير التقارير، ومؤشرات الأداء.
    يُستدعى هذا من app.py لتجميع كل الكولباكات في نقطة واحدة.
    """
    callback_modules = [
        ("رفع البيانات", register_upload_callbacks),
        ("الفلاتر", register_filters_callbacks),
        ("الرسوم البيانية", register_charts_callbacks),
        ("تصدير التقارير", register_export_callbacks),
        ("مؤشرات الأداء (KPIs)", register_kpi_callbacks),
    ]

    for name, func in callback_modules:
        try:
            func(app)
            logger.info(f"✅ تم تسجيل كولباكات {name} بنجاح.")
        except Exception as e:
            logger.error(f"❌ خطأ أثناء تسجيل كولباكات {name}: {e}", exc_info=True)

__all__ = ["register_callbacks"]
