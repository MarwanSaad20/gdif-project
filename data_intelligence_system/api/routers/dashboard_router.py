from fastapi import APIRouter, HTTPException, status, Query
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date

from data_intelligence_system.utils.logger import get_logger
from data_intelligence_system.api.services import dashboard_service

logger = get_logger("api.dashboard")

router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"],
    responses={404: {"description": "Not Found"}},
)


class KPIsResponse(BaseModel):
    total_users: int = Field(..., description="إجمالي عدد المستخدمين")
    active_sessions: int = Field(..., description="عدد الجلسات النشطة")
    revenue: float = Field(..., description="الإيرادات")
    conversion_rate: float = Field(..., description="معدل التحويل")
    error_rate: float = Field(..., description="معدل الأخطاء")


class DashboardDataResponse(BaseModel):
    report_date: date = Field(..., description="تاريخ البيانات")
    metric: str = Field(..., description="نوع المقياس")
    values: List[int] = Field(..., description="قيم البيانات للمقياس")


class UpdateDashboardRequest(BaseModel):
    key: str = Field(..., description="المفتاح أو الخاصية المراد تحديثها")
    value: Optional[str] = Field(None, description="القيمة الجديدة")


@router.get("/kpis", response_model=KPIsResponse, summary="جلب مؤشرات الأداء الرئيسية (KPIs)")
async def get_kpis():
    try:
        logger.info("Fetching KPIs data")
        kpis = await dashboard_service.get_kpis()
        return kpis
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to fetch KPIs: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to fetch KPIs")


@router.get("/data", response_model=DashboardDataResponse, summary="جلب بيانات عامة للوحة التحكم مع دعم الفلاتر")
async def get_dashboard_data(
    filter_date: Optional[date] = Query(None, description="تصفية حسب تاريخ محدد (YYYY-MM-DD)"),
    metric: Optional[str] = Query(None, description="نوع المقياس المطلوب"),
):
    try:
        logger.info(f"Fetching dashboard data with filter_date={filter_date}, metric={metric}")
        data = await dashboard_service.get_dashboard_data(filter_date=filter_date, metric=metric)
        # يفترض هنا أن الخدمة تعيد المفتاح 'report_date' مباشرة

        return data
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to fetch dashboard data: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to fetch dashboard data")


@router.post("/update", summary="تحديث بيانات الداشبورد")
async def update_dashboard_data(payload: UpdateDashboardRequest):
    try:
        logger.info(f"Updating dashboard data with payload: {payload.dict()}")
        await dashboard_service.update_dashboard_data(payload.dict())
        return {"message": "Dashboard updated successfully."}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update dashboard data: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to update dashboard data")
