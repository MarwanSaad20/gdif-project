from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional, Dict, Any

import pandas as pd

from data_intelligence_system.utils.logger import get_logger
from data_intelligence_system.utils.data_loader import load_data
from data_intelligence_system.analysis.descriptive_stats import generate_descriptive_stats
from data_intelligence_system.analysis.correlation_analysis import run_correlation_analysis
from data_intelligence_system.analysis.outlier_detection import run_outlier_detection
from data_intelligence_system.analysis.clustering_analysis import run_clustering
from data_intelligence_system.analysis.target_relation_analysis import run_target_relation_analysis

from data_intelligence_system.config.paths_config import CLEAN_DATA_FILE

logger = get_logger("analysis.service")


@dataclass
class AnalysisService:
    data_path: Path
    data: Optional[pd.DataFrame] = field(default=None, init=False)

    def __post_init__(self) -> None:
        self.load_data()

    def load_data(self, force_reload: bool = False) -> pd.DataFrame:
        """
        تحميل أو إعادة تحميل البيانات المنظفة من المسار.
        Raises FileNotFoundError إذا لم يكن الملف موجودًا.
        Raises Exception لأي خطأ آخر أثناء التحميل.
        """
        if self.data is None or force_reload:
            if not self.data_path.exists():
                logger.error(f"❌ المسار غير موجود: {self.data_path}")
                raise FileNotFoundError(f"File not found: {self.data_path}")

            try:
                logger.info(f"📁 بدء تحميل الملف: {self.data_path}")
                self.data = load_data(str(self.data_path))
                if self.data.empty:
                    logger.warning(f"⚠️ الملف {self.data_path} تم تحميله لكنه فارغ.")
                else:
                    logger.info(f"✅ تم تحميل البيانات بنجاح من: {self.data_path}")
            except Exception as e:
                logger.exception(f"❌ فشل في تحميل البيانات من {self.data_path}: {e}")
                raise
        return self.data

    def run_descriptive_stats(self, df: pd.DataFrame) -> Dict[str, Any]:
        """تنفيذ التحليل الوصفي على DataFrame."""
        return generate_descriptive_stats(df)

    def descriptive_statistics(self) -> Dict[str, Any]:
        """تشغيل التحليل الوصفي على البيانات المحملة."""
        logger.info("🚀 بدء التحليل الوصفي...")
        df = self.load_data()
        if df.empty:
            logger.warning("⚠️ البيانات فارغة، لا يمكن إجراء التحليل الوصفي.")
            return {}
        return self.run_descriptive_stats(df)

    def correlation_analysis(self, method: str = "pearson") -> Dict[str, Any]:
        """تشغيل تحليل الارتباط على البيانات المحملة."""
        logger.info(f"🔍 تحليل الارتباط باستخدام {method}")
        df = self.load_data()
        if df.empty:
            logger.warning("⚠️ البيانات فارغة، لا يمكن إجراء تحليل الارتباط.")
            return {}
        return run_correlation_analysis(df, method=method)

    def outlier_detection(self, method: str = "iqr") -> Dict[str, Any]:
        """تشغيل كشف القيم الشاذة على البيانات المحملة."""
        logger.info(f"⚠️ كشف القيم الشاذة باستخدام {method}")
        df = self.load_data()
        if df.empty:
            logger.warning("⚠️ البيانات فارغة، لا يمكن إجراء كشف القيم الشاذة.")
            return {}
        return run_outlier_detection(df, method=method)

    def clustering_insights(self, algorithm: str = "kmeans", n_clusters: int = 3) -> Dict[str, Any]:
        """تشغيل تحليل التجميع على البيانات المحملة."""
        logger.info(f"📊 التجميع باستخدام {algorithm} بعدد {n_clusters} مجموعات")
        df = self.load_data()
        if df.empty:
            logger.warning("⚠️ البيانات فارغة، لا يمكن إجراء تحليل التجميع.")
            return {}
        return run_clustering(df, algorithm=algorithm, n_clusters=n_clusters)

    def target_relationship(self, target_column: Optional[str] = None) -> Dict[str, Any]:
        """
        تحليل العلاقة مع عمود الهدف المحدد أو العمود الأخير في البيانات.
        تعيد تحذير إذا كان العمود غير موجود أو البيانات فارغة.
        """
        df = self.load_data()
        if df.empty:
            logger.warning("⚠️ البيانات فارغة، لا يمكن تحليل العلاقة مع الهدف.")
            return {}

        target = target_column if target_column else (df.columns[-1] if len(df.columns) > 0 else None)
        if target is None or target not in df.columns:
            logger.warning(f"⚠️ لم يتم العثور على المتغير الهدف: {target}")
            return {"warning": f"Target column '{target}' not found in data."}

        logger.info(f"🎯 تحليل العلاقة مع الهدف: {target}")
        return run_target_relation_analysis(df, target_col=target)


if __name__ == "__main__":
    import sys

    logger = get_logger("analysis.cli", reset=True)

    data_file_path = Path(CLEAN_DATA_FILE)

    if not data_file_path.exists():
        logger.error(f"ملف البيانات غير موجود: {data_file_path}")
        sys.exit(1)

    service = AnalysisService(data_path=data_file_path)

    print("\n[1] Descriptive Statistics:")
    print(service.descriptive_statistics())

    print("\n[2] Correlation Analysis:")
    print(service.correlation_analysis())

    print("\n[3] Outlier Detection:")
    print(service.outlier_detection())

    print("\n[4] Clustering Insights:")
    print(service.clustering_insights())

    print("\n[5] Target Relationship Analysis:")
    print(service.target_relationship(target_column="species"))
