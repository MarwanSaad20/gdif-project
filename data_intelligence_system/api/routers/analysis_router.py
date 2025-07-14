from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Literal, Any

# ✅ استخدام اللوجر المركزي
from data_intelligence_system.utils.logger import get_logger
from data_intelligence_system.api.services import analysis_service

logger = get_logger("api.analysis")

router = APIRouter(
    prefix="/analysis",
    tags=["Analysis"],
    responses={404: {"description": "Not Found"}},
)

# ======== نماذج الطلب ========

class DescriptiveStatsRequest(BaseModel):
    dataset_name: str = Field(..., description="اسم مجموعة البيانات")
    columns: Optional[List[str]] = Field(None, description="قائمة أعمدة للتحليل، إذا لم تُحدد يتم التحليل الكامل")
    include_correlations: bool = Field(False, description="هل يشمل تحليل الارتباط؟")

class TrainModelRequest(BaseModel):
    model_type: Literal["linear_regression", "random_forest", "xgboost", "svm", "decision_tree"] = Field(
        ..., description="نوع النموذج المدعوم"
    )
    dataset_name: str = Field(..., description="اسم مجموعة البيانات")
    target_column: str = Field(..., description="اسم عمود الهدف")
    features: Optional[List[str]] = Field(None, description="قائمة الميزات لاستخدامها، إذا لم تُحدد تستخدم كل الأعمدة ما عدا الهدف")
    hyperparameters: Optional[Dict[str, Any]] = Field(default_factory=dict, description="إعدادات هايبر باراميترز للنموذج")

class EvaluateModelRequest(BaseModel):
    model_id: str = Field(..., description="معرف النموذج المدرب")
    test_dataset_name: str = Field(..., description="اسم مجموعة بيانات الاختبار")

# ======== نقاط النهاية ========

@router.post("/descriptive_stats", summary="تحليل إحصائي وصفي للبيانات")
async def descriptive_stats(request: DescriptiveStatsRequest):
    try:
        logger.info(f"Starting descriptive stats on dataset {request.dataset_name} with columns {request.columns}")
        result = await analysis_service.perform_descriptive_stats(
            dataset_name=request.dataset_name,
            columns=request.columns,
            include_correlations=request.include_correlations,
        )
        return JSONResponse(status_code=status.HTTP_200_OK, content=result)
    except Exception as e:
        logger.error(f"Error in descriptive_stats: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to perform descriptive stats")

@router.post("/train_model", summary="تدريب نموذج تعلم آلة")
async def train_model(request: TrainModelRequest):
    try:
        logger.info(f"Training model {request.model_type} on dataset {request.dataset_name}")
        model_id = await analysis_service.train_model(
            model_type=request.model_type,
            dataset_name=request.dataset_name,
            target_column=request.target_column,
            features=request.features,
            hyperparameters=request.hyperparameters,
        )
        return JSONResponse(status_code=status.HTTP_201_CREATED, content={"model_id": model_id})
    except Exception as e:
        logger.error(f"Error in train_model: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to train model")

@router.post("/evaluate_model", summary="تقييم نموذج تعلم آلة")
async def evaluate_model(request: EvaluateModelRequest):
    try:
        logger.info(f"Evaluating model {request.model_id} on dataset {request.test_dataset_name}")
        metrics = await analysis_service.evaluate_model(
            model_id=request.model_id,
            test_dataset_name=request.test_dataset_name,
        )
        return JSONResponse(status_code=status.HTTP_200_OK, content=metrics)
    except Exception as e:
        logger.error(f"Error in evaluate_model: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to evaluate model")
