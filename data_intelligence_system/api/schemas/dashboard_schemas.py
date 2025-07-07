from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import date

# ✅ تم التحقق من التكامل مع نظام التسجيل الجديد utils.logger
# (لا حاجة لتعديل مباشر لأن هذا الملف لا يحتوي على لوجر، فقط تأكد من قابلية الاستيراد دون تعارض)

class KPIsRequest(BaseModel):
    date_from: Optional[date] = Field(None, description="تاريخ البداية للتصفية (YYYY-MM-DD)")
    date_to: Optional[date] = Field(None, description="تاريخ النهاية للتصفية (YYYY-MM-DD)")
    filters: Optional[Dict[str, Any]] = Field(default_factory=dict, description="فلاتر إضافية لتحديد البيانات")


class KPIsResponse(BaseModel):
    total_users: int = Field(..., description="إجمالي المستخدمين")
    active_sessions: int = Field(..., description="الجلسات النشطة")
    revenue: float = Field(..., description="الإيرادات")
    conversion_rate: float = Field(..., description="معدل التحويل")
    error_rate: float = Field(..., description="معدل الأخطاء")


class DashboardDataRequest(BaseModel):
    filter_date: Optional[date] = Field(None, description="تصفية حسب تاريخ محدد (YYYY-MM-DD)")
    metric: Optional[str] = Field(None, description="نوع المقياس المطلوب")


class DashboardUpdateRequest(BaseModel):
    payload: Dict[str, Any] = Field(..., description="البيانات لتحديث لوحة التحكم")
