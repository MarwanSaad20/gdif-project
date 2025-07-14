from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import date


class KPIsRequest(BaseModel):
    """
    نموذج طلب للحصول على مؤشرات الأداء الرئيسية مع إمكانية التصفية بالتواريخ والفلاتر.
    """
    date_from: Optional[date] = Field(default=None, description="تاريخ البداية للتصفية (YYYY-MM-DD)")
    date_to: Optional[date] = Field(default=None, description="تاريخ النهاية للتصفية (YYYY-MM-DD)")
    filters: Dict[str, Any] = Field(default_factory=dict, description="فلاتر إضافية لتحديد البيانات")


class KPIsResponse(BaseModel):
    """
    نموذج رد يحتوي على مؤشرات الأداء الرئيسية الأساسية.
    """
    total_users: int = Field(..., description="إجمالي المستخدمين")
    active_sessions: int = Field(..., description="الجلسات النشطة")
    revenue: float = Field(..., description="الإيرادات")
    conversion_rate: float = Field(..., description="معدل التحويل")
    error_rate: float = Field(..., description="معدل الأخطاء")


class DashboardDataRequest(BaseModel):
    """
    نموذج طلب بيانات لوحة التحكم مع إمكانية التصفية.
    """
    filter_date: Optional[date] = Field(default=None, description="تصفية حسب تاريخ محدد (YYYY-MM-DD)")
    metric: Optional[str] = Field(default=None, description="نوع المقياس المطلوب")


class DashboardUpdateRequest(BaseModel):
    """
    نموذج طلب لتحديث بيانات لوحة التحكم.
    """
    payload: Dict[str, Any] = Field(..., description="البيانات لتحديث لوحة التحكم")
