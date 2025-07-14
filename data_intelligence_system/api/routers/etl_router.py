from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Optional, Literal, Callable, Awaitable, Any, TypeVar
import functools

from data_intelligence_system.utils.logger import get_logger
from data_intelligence_system.api.services.etl_service import ETLService
from data_intelligence_system.data.raw.convert_format import convert_all_files

logger = get_logger("api.etl")

router = APIRouter(
    prefix="/etl",
    tags=["ETL"],
    responses={404: {"description": "المورد غير موجود"}},
)

etl_service = ETLService()

# ============ Models ============

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

# ============ Error Handling Decorator ============

F = TypeVar("F", bound=Callable[..., Awaitable[Any]])

def handle_etl_errors(func: F) -> F:
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except FileNotFoundError as e:
            logger.warning(f"[{func.__name__.upper()}] File not found: {e}")
            raise HTTPException(status_code=404, detail=str(e))
        except ValueError as e:
            logger.warning(f"[{func.__name__.upper()}] Invalid data: {e}")
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            logger.error(f"[{func.__name__.upper()} ERROR] {e}", exc_info=True)
            raise HTTPException(status_code=500, detail="فشل في معالجة الطلب")
    return wrapper  # type: ignore

# ============ Endpoints ============

@router.post("/load", summary="تحميل بيانات جديدة إلى النظام")
@handle_etl_errors
async def load_data(request: LoadDataRequest):
    logger.info(f"[LOAD] المصدر: {request.source_name} | مسار: {request.file_path} | استبدال: {request.overwrite}")
    result = etl_service.load_data(
        source_name=request.source_name,
        file_path=request.file_path,
        overwrite=request.overwrite
    )
    return JSONResponse(status_code=status.HTTP_200_OK, content={"message": result})

@router.post("/clean", summary="تنظيف البيانات الموجودة")
@handle_etl_errors
async def clean_data(request: CleanDataRequest):
    logger.info(f"[CLEAN] المستوى المطلوب: {request.cleaning_level}")
    result = etl_service.clean_data(level=request.cleaning_level)
    return JSONResponse(status_code=status.HTTP_200_OK, content={"message": result})

@router.post("/extract", summary="استخراج عينة من البيانات")
@handle_etl_errors
async def extract_data(request: ExtractDataRequest):
    logger.info(f"[EXTRACT] عدد السجلات: {request.limit}")
    data = etl_service.extract_data(limit=request.limit)
    return JSONResponse(status_code=status.HTTP_200_OK, content={"data": data})

@router.post("/convert", summary="تحويل صيغ الملفات الخام")
@handle_etl_errors
async def convert_data_format(request: ConvertFormatRequest):
    logger.info(f"[CONVERT] الصيغة المستهدفة: {request.target_format}")
    # تحقق إن كانت convert_all_files متزامنة، إذا كانت blocking من الأفضل تشغيلها في ThreadPoolExecutor
    convert_all_files(target_format=request.target_format)
    return JSONResponse(status_code=status.HTTP_200_OK, content={"message": f"تم التحويل إلى {request.target_format}"})
