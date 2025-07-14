from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Literal


class BaseAnalysisRequest(BaseModel):
    """أساس لطلبات التحليل التي تحتاج اسم مجموعة البيانات"""
    dataset_name: str = Field(..., description="اسم مجموعة البيانات")
    features: Optional[List[str]] = Field(
        None, description="قائمة الأعمدة المستخدمة (اختيارية)"
    )


class DescriptiveStatsRequest(BaseAnalysisRequest):
    """
    طلب للحصول على إحصائيات وصفية، مع خيار حساب مصفوفة الارتباطات
    """
    include_correlations: bool = Field(
        default=False, description="هل يتم حساب مصفوفة الارتباطات؟"
    )


class ClusteringRequest(BaseAnalysisRequest):
    """
    طلب تنفيذ التجميع باستخدام خوارزمية محددة
    """
    algorithm: Literal["kmeans", "dbscan"] = Field(
        default="kmeans",
        description="خوارزمية التجميع (kmeans, dbscan, ...)"
    )
    n_clusters: Optional[int] = Field(
        default=None,
        ge=1,
        description="عدد التجمعات (مطلوب فقط في بعض الخوارزميات مثل kmeans)"
    )


class ModelTrainingRequest(BaseModel):
    """
    طلب تدريب نموذج تنبؤي مع تحديد النوع والمعاملات
    """
    model_type: Literal[
        "linear_regression",
        "random_forest",
        "xgboost",
        "svm",
        "decision_tree"
    ] = Field(..., description="نوع النموذج المدعوم")
    dataset_name: str = Field(..., description="اسم مجموعة البيانات")
    target_column: str = Field(..., description="اسم عمود الهدف")
    features: Optional[List[str]] = Field(
        None,
        description="أعمدة الميزات لاستخدامها، إذا لم تُحدد تُستخدم كل الأعمدة ما عدا الهدف"
    )
    hyperparameters: Dict[str, object] = Field(
        default_factory=dict,
        description="معاملات ضبط النموذج (هايبر باراميترز)"
    )


class ModelEvaluationRequest(BaseModel):
    """
    طلب تقييم نموذج باستخدام بيانات اختبار
    """
    model_id: str = Field(..., description="معرف النموذج المدرب")
    test_dataset_name: str = Field(..., description="اسم مجموعة بيانات الاختبار")
