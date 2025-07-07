from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Literal


class DescriptiveStatsRequest(BaseModel):
    dataset_name: str = Field(..., description="اسم مجموعة البيانات")
    columns: Optional[List[str]] = Field(
        None, description="أعمدة للتحليل، إذا لم تُحدد يتم التحليل الكامل"
    )
    include_correlations: bool = Field(
        default=False, description="هل يتم حساب مصفوفة الارتباطات؟"
    )


class ClusteringRequest(BaseModel):
    dataset_name: str = Field(..., description="اسم مجموعة البيانات")
    features: Optional[List[str]] = Field(
        None, description="قائمة الأعمدة التي تستخدم في التجميع"
    )
    algorithm: Literal["kmeans", "dbscan"] = Field(
        default="kmeans",
        description="خوارزمية التجميع (kmeans, dbscan, ...)"
    )
    n_clusters: int = Field(
        3,
        ge=1,
        description="عدد التجمعات (إذا كانت الخوارزمية تتطلب ذلك)"
    )


class ModelTrainingRequest(BaseModel):
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
        description="أعمدة الميزات لاستخدامها، إذا لم تُحدد تستخدم كل الأعمدة ما عدا الهدف"
    )
    hyperparameters: Dict[str, object] = Field(
        default_factory=dict,
        description="معاملات ضبط النموذج (هايبر باراميترز)"
    )


class ModelEvaluationRequest(BaseModel):
    model_id: str = Field(..., description="معرف النموذج المدرب")
    test_dataset_name: str = Field(..., description="اسم مجموعة بيانات الاختبار")
