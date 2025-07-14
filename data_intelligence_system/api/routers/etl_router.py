from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Optional, Literal

# ✅ استيراد اللوجر المركزي بدلاً من logging.getLogger
from data_intelligence_system.utils.logger import get_logger
from data_intelligence_system.api.services.etl_service import ETLService
from data_intelligence_system.data.raw.convert_format import convert_all_files

logger = get_logger("api.etl")

router = APIRouter(
    prefix="/etl",
    tags=["ETL"],
    responses={404: {"description": "المورد غير موجود"}},
)

etl_service = ETLService()  # كائن الخدمة المشترك

# ======================== النماذج ========================

class LoadDataRequest(BaseModel):
    source_name: Literal["raw", "external"] = Field(..., description="اسم مصدر البيانات (raw أو external)")
    file_path: Optional[str] = Field(None, description="المسار الكامل للملف (اختياري)")
    overwrite: bool = Field(False, description="هل يتم استبدال البيانات القديمة؟")

class CleanDataRequest(BaseModel):
    cleaning_level: Literal["basic", "standard", "advanced"] = Field("standard", description="مستوى التنظيف")

class ExtractDataRequest(BaseModel):
    limit: int = Field(1000, ge=1, le=10000, description="عدد السجلات المراد استخراجها")

class ConvertFormatRequest(BaseModel):
    target_format: Literal[".csv", ".xlsx", ".json"] = Field(..., description="الصيغة المطلوبة للتحويل")

# ======================== المسارات ========================

@router.post("/load", summary="تحميل بيانات جديدة إلى النظام")
async def load_data(request: LoadDataRequest):
    try:
        logger.info(f"[LOAD] المصدر: {request.source_name} | مسار: {request.file_path} | استبدال: {request.overwrite}")
        result = etl_service.load_data(
            source_name=request.source_name,
            file_path=request.file_path,
            overwrite=request.overwrite
        )
        return JSONResponse(status_code=status.HTTP_200_OK, content={"message": result})
    except FileNotFoundError as e:
        logger.warning(f"[LOAD] File not found: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        logger.warning(f"[LOAD] Invalid data: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"[LOAD ERROR] {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="فشل في تحميل البيانات")

@router.post("/clean", summary="تنظيف البيانات الموجودة")
async def clean_data(request: CleanDataRequest):
    try:
        logger.info(f"[CLEAN] المستوى المطلوب: {request.cleaning_level}")
        result = etl_service.clean_data(level=request.cleaning_level)
        return JSONResponse(status_code=status.HTTP_200_OK, content={"message": result})
    except Exception as e:
        logger.error(f"[CLEAN ERROR] {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="فشل في تنظيف البيانات")

@router.post("/extract", summary="استخراج عينة من البيانات")
async def extract_data(request: ExtractDataRequest):
    try:
        logger.info(f"[EXTRACT] عدد السجلات: {request.limit}")
        data = etl_service.extract_data(limit=request.limit)
        return JSONResponse(status_code=status.HTTP_200_OK, content={"data": data})
    except Exception as e:
        logger.error(f"[EXTRACT ERROR] {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="فشل في استخراج البيانات")

@router.post("/convert", summary="تحويل صيغ الملفات الخام")
async def convert_data_format(request: ConvertFormatRequest):
    try:
        logger.info(f"[CONVERT] الصيغة المستهدفة: {request.target_format}")
        convert_all_files(target_format=request.target_format)
        return JSONResponse(status_code=status.HTTP_200_OK, content={"message": f"تم التحويل إلى {request.target_format}"})
    except Exception as e:
        logger.error(f"[CONVERT ERROR] {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="فشل في تحويل الملفات")
