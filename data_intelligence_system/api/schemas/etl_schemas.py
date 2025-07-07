from pydantic import BaseModel, Field, field_validator
from typing import Optional, Dict


class DataSourceSchema(BaseModel):
    source_name: str = Field(..., description="اسم مصدر البيانات مثل raw, external, api")
    file_path: Optional[str] = Field(None, description="مسار الملف إذا كان محددًا")
    overwrite: bool = Field(False, description="هل يجب استبدال البيانات القديمة؟")


class ExtractParamsSchema(BaseModel):
    limit: Optional[int] = Field(1000, ge=1, le=10000, description="عدد السجلات المطلوب استخراجها")
    filters: Optional[Dict[str, object]] = Field(default_factory=dict, description="معايير فلترة لاستخراج البيانات")


class TransformParamsSchema(BaseModel):
    cleaning_level: str = Field("standard", description="مستوى تنظيف البيانات (basic, standard, advanced)")

    @field_validator('cleaning_level')
    @classmethod
    def check_cleaning_level(cls, v: str) -> str:
        allowed = {"basic", "standard", "advanced"}
        if v not in allowed:
            raise ValueError(f"cleaning_level يجب أن يكون واحدًا من {allowed}")
        return v


class LoadParamsSchema(BaseModel):
    target_table: Optional[str] = Field(None, description="اسم جدول أو وجهة التحميل")
    batch_size: int = Field(500, ge=1, description="حجم دفعات التحميل")


class ETLJobSchema(BaseModel):
    """
    نموذج شامل يمثل عملية ETL بكامل مراحلها:
    - المصدر
    - معلمات الاستخراج
    - معلمات التحويل
    - معلمات التحميل
    """
    source: DataSourceSchema
    extract_params: ExtractParamsSchema = Field(default_factory=ExtractParamsSchema)
    transform_params: TransformParamsSchema = Field(default_factory=TransformParamsSchema)
    load_params: LoadParamsSchema = Field(default_factory=LoadParamsSchema)
