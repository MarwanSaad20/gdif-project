from typing import Optional, Dict, Any, List, Tuple
from pathlib import Path
import pandas as pd

from data_intelligence_system.etl.extract import extract_file
from data_intelligence_system.etl.transform import transform_datasets
from data_intelligence_system.etl.load import save_multiple_datasets
from data_intelligence_system.utils.data_loader import load_data
from data_intelligence_system.data.raw.register_sources import main as register_sources_main

from data_intelligence_system.utils.logger import get_logger

logger = get_logger("etl.service")


class ETLService:
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.data: Optional[List[Tuple[str, pd.DataFrame]]] = None

    def run_etl(
        self,
        source: str,
        extract_params: Optional[Dict[str, Any]] = None,
        transform_params: Optional[Dict[str, Any]] = None,
        load_params: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        تنفيذ تسلسل ETL الكامل (استخراج → تحويل → تحميل)
        """
        try:
            logger.info(f"🚀 بدء عملية ETL لمصدر: {source}")

            # ===== استخراج البيانات =====
            df = None
            ep = extract_params or {}

            if ep.get("use_load_data", False):
                df = load_data(source)
            else:
                # دعم ملفات external
                source_path = Path(source)
                if ep.get("extract_from_external", False):
                    source_path = (
                        Path(__file__).resolve().parents[2]
                        / "data" / "external" / "downloaded" / source
                    )
                df = extract_file(source_path)

            logger.info(f"✅ تم استخراج البيانات: {df.shape} - الأعمدة: {df.columns.tolist()}")

            # ===== تحويل البيانات =====
            datasets = [(Path(source).stem, df)]
            logger.info(f"🧹 بدء تحويل البيانات مع المعاملات: {transform_params}")
            transformed_datasets = transform_datasets(datasets, **(transform_params or {}))
            if not transformed_datasets or not isinstance(transformed_datasets, list):
                logger.error("❌ تحويل البيانات فشل أو لم يرجع قائمة datasets")
                return False

            logger.info(f"✅ بعد التحويل: عدد المجموعات = {len(transformed_datasets)}")
            for name, d in transformed_datasets:
                logger.info(f"📊 {name}: {d.shape} - الأعمدة: {d.columns.tolist()}")

            # ===== تحميل البيانات =====
            if not load_params or 'output_dir' not in load_params:
                logger.error("❌ load_params لا يحتوي على 'output_dir'")
                return False

            logger.info(f"💾 بدء حفظ البيانات مع المعاملات: {load_params}")
            success = save_multiple_datasets(transformed_datasets, **load_params)
            if not success:
                logger.error("❌ فشل في حفظ البيانات بعد التحويل")
                return False

            # ✅ تسجيل الملفات في سجل المصادر بعد حفظها
            try:
                register_sources_main()
                logger.info("📘 تم تحديث سجل المصادر بعد التحميل.")
            except Exception as reg_err:
                logger.warning(f"⚠️ فشل في تحديث سجل المصادر: {reg_err}")

            self.data = transformed_datasets
            return True

        except Exception as e:
            logger.error(f"❌ فشل في تنفيذ ETL: {e}", exc_info=True)
            return False

    def get_data(self) -> Optional[List[Tuple[str, pd.DataFrame]]]:
        return self.data
