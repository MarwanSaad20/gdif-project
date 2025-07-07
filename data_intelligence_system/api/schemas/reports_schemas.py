from pydantic import BaseModel, Field
from typing import Optional, Dict, Literal


class ReportGenerationRequest(BaseModel):
    report_type: Literal["pdf", "excel", "html"] = Field(
        ..., description="نوع التقرير (pdf, excel, html)"
    )
    dataset_name: Optional[str] = Field(
        None, description="اسم مجموعة البيانات المرتبطة بالتقرير"
    )
    include_charts: Optional[bool] = Field(
        True, description="هل تضمّن الرسوم البيانية في التقرير؟"
    )
    filters: Optional[Dict] = Field(
        default_factory=dict, description="فلاتر مخصصة لتصفية البيانات داخل التقرير"
    )


class ReportDownloadRequest(BaseModel):
    file_name: str = Field(
        ..., description="اسم ملف التقرير فقط (بدون مسار كامل)، وسيتم تأمين المسار في الخدمة"
    )
