from pathlib import Path
from typing import Optional, List, Tuple

import pandas as pd

from data_intelligence_system.api.schemas.etl_schemas import (
    DataSourceSchema,
    ExtractParamsSchema,
    TransformParamsSchema,
    LoadParamsSchema
)
from data_intelligence_system.etl.extract import extract_file
from data_intelligence_system.etl.transform import transform_datasets
from data_intelligence_system.etl.load import save_multiple_datasets
from data_intelligence_system.utils.data_loader import load_data
from data_intelligence_system.data.raw.register_sources import main as register_sources_main
from data_intelligence_system.utils.logger import get_logger

logger = get_logger("etl.service")


class ETLService:
    def __init__(self, config: Optional[dict] = None):
        self.config = config or {}
        self.data: Optional[List[Tuple[str, pd.DataFrame]]] = None

    def run_etl(
        self,
        source: str,
        extract_params: Optional[ExtractParamsSchema] = None,
        transform_params: Optional[TransformParamsSchema] = None,
        load_params: Optional[LoadParamsSchema] = None
    ) -> bool:
        """
        تنفيذ تسلسل ETL الكامل (استخراج → تحويل → تحميل)
        """
        try:
            logger.info(f"🚀 بدء عملية ETL لمصدر: {source}")

            df = self._extract(source, extract_params)
            if df is None or df.empty:
                logger.error("❌ فشل في استخراج البيانات أو البيانات فارغة")
                return False

            datasets = [(Path(source).stem, df)]
            transformed = self._transform(datasets, transform_params)
            if not transformed:
                return False

            if not load_params or not load_params.target_table:
                logger.error("❌ load_params لا يحتوي على target_table")
                return False

            if not self._load(transformed, load_params):
                return False

            try:
                register_sources_main()
                logger.info("📘 تم تحديث سجل المصادر بعد التحميل.")
            except Exception as reg_err:
                logger.warning(f"⚠️ فشل في تحديث سجل المصادر: {reg_err}")

            self.data = transformed
            return True

        except Exception as e:
            logger.error(f"❌ فشل في تنفيذ ETL: {e}", exc_info=True)
            return False

    def _extract(self, source: str, params: Optional[ExtractParamsSchema]) -> Optional[pd.DataFrame]:
        try:
            if params and params.filters.get("use_load_data", False):
                df = load_data(source)
            else:
                source_path = Path(source)
                if params and params.filters.get("extract_from_external", False):
                    source_path = (
                        Path(__file__).resolve().parents[2] / "data" / "external" / "downloaded" / source
                    )
                df = extract_file(source_path)
            logger.info(f"✅ استخراج البيانات: {df.shape} - الأعمدة: {df.columns.tolist()}")
            return df
        except Exception as e:
            logger.error(f"❌ فشل في استخراج البيانات: {e}", exc_info=True)
            return None

    def _transform(self, datasets: List[Tuple[str, pd.DataFrame]], params: Optional[TransformParamsSchema]) -> Optional[List[Tuple[str, pd.DataFrame]]]:
        try:
            cleaning_level = params.cleaning_level if params else "standard"
            logger.info(f"🧹 بدء تحويل البيانات - مستوى التنظيف: {cleaning_level}")
            transformed = transform_datasets(datasets, cleaning_level=cleaning_level)
            if not transformed or not isinstance(transformed, list):
                logger.error("❌ تحويل البيانات فشل أو لم يرجع قائمة datasets")
                return None
            logger.info(f"✅ بعد التحويل: عدد المجموعات = {len(transformed)}")
            return transformed
        except Exception as e:
            logger.error(f"❌ خطأ في تحويل البيانات: {e}", exc_info=True)
            return None

    def _load(self, datasets: List[Tuple[str, pd.DataFrame]], params: LoadParamsSchema) -> bool:
        try:
            logger.info(f"💾 بدء حفظ البيانات إلى الوجهة: {params.target_table}")
            success = save_multiple_datasets(datasets, target_table=params.target_table, batch_size=params.batch_size)
            if success:
                logger.info("✅ تم حفظ البيانات بنجاح.")
                return True
            logger.error("❌ فشل في حفظ البيانات بعد التحويل")
            return False
        except Exception as e:
            logger.error(f"❌ خطأ في حفظ البيانات: {e}", exc_info=True)
            return False

    def get_data(self) -> Optional[List[Tuple[str, pd.DataFrame]]]:
        return self.data
