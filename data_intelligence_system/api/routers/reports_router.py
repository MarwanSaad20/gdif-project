from fastapi import APIRouter, HTTPException, status, Query
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel, Field
from typing import Optional, Literal, Dict
import os

# ✅ استيراد اللوجر المركزي وإعدادات التقرير من جذر المشروع
from data_intelligence_system.utils.logger import get_logger
from data_intelligence_system.config.report_config import REPORT_CONFIG
from data_intelligence_system.api.services import reports_service

logger = get_logger("api.reports")

SAFE_REPORTS_DIR = str(REPORT_CONFIG["output_dir"])

router = APIRouter(
    prefix="/reports",
    tags=["Reports"],
    responses={404: {"description": "Report not found"}},
)

class ReportRequest(BaseModel):
    report_type: Literal["pdf", "excel", "html"] = Field(..., description="نوع التقرير المطلوب")
    dataset_name: Optional[str] = Field("default", description="اسم مجموعة البيانات")
    include_charts: Optional[bool] = Field(True, description="هل تدرج الرسوم البيانية؟")
    filters: Optional[Dict] = Field(default_factory=dict, description="فلاتر إضافية لتصفية البيانات")

@router.post("/generate", summary="توليد تقرير جديد")
async def generate_report(request: ReportRequest):
    try:
        logger.info(f"📝 توليد تقرير [{request.report_type}] لبيانات: {request.dataset_name} مع الفلاتر: {request.filters}")

        report_path = await reports_service.generate_report(
            report_type=request.report_type,
            dataset_name=request.dataset_name,
            include_charts=request.include_charts,
            filters=request.filters
        )

        if not os.path.isfile(report_path):
            logger.error(f"تقرير غير موجود بعد التوليد: {report_path}")
            raise FileNotFoundError(f"تقرير غير موجود بعد التوليد: {report_path}")

        logger.info(f"✅ تم توليد التقرير بنجاح: {report_path}")

        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={
                "report_path": report_path,
                "message": "📄 تم توليد التقرير بنجاح"
            }
        )
    except ValueError as ve:
        logger.warning(f"⚠️ خطأ في الطلب: {ve}")
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"❌ فشل توليد التقرير: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="فشل في توليد التقرير")

@router.get("/download", summary="تحميل تقرير موجود")
async def download_report(file_name: str = Query(..., description="اسم ملف التقرير فقط (بدون المسار الكامل)")):
    try:
        safe_file_name = os.path.basename(file_name)
        safe_path = os.path.join(SAFE_REPORTS_DIR, safe_file_name)

        if not os.path.isfile(safe_path):
            logger.warning(f"⚠️ تقرير غير موجود: {safe_path}")
            raise HTTPException(status_code=404, detail="لم يتم العثور على التقرير")

        file_size = os.path.getsize(safe_path)
        logger.info(f"📥 تحميل التقرير: {safe_path} (الحجم: {file_size} bytes)")

        def iterfile():
            with open(safe_path, mode="rb") as file_like:
                yield from file_like

        return StreamingResponse(
            iterfile(),
            media_type="application/octet-stream",
            headers={
                "Content-Disposition": f"attachment; filename={safe_file_name}"
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ فشل في تحميل التقرير: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="فشل في تحميل التقرير")
