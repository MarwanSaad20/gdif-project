from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, Literal


class ReportGenerationRequest(BaseModel):
    """
    طلب توليد تقرير جديد.
    """
    report_type: Literal["pdf", "excel", "html"] = Field(
        ..., description="نوع التقرير (pdf, excel, html)"
    )
    dataset_name: Optional[str] = Field(
        default=None, description="اسم مجموعة البيانات المرتبطة بالتقرير"
    )
    include_charts: bool = Field(
        default=True, description="هل تضمّن الرسوم البيانية في التقرير؟"
    )
    filters: Dict[str, Any] = Field(
        default_factory=dict,
        description="فلاتر مخصصة لتصفية البيانات داخل التقرير"
    )


class ReportDownloadRequest(BaseModel):
    """
    طلب تنزيل تقرير موجود.
    """
    file_name: str = Field(
        ..., description="اسم ملف التقرير فقط (بدون مسار كامل)، وسيتم تأمين المسار في الخدمة"
    )
