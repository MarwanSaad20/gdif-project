import pandas as pd
import numpy as np
import logging
from sklearn.ensemble import IsolationForest
from scipy import stats
from pathlib import Path

# استيرادات من جذر المشروع
from data_intelligence_system.analysis.analysis_utils import (
    ensure_output_dir,
    get_numerical_columns,
    save_dataframe,
    log_basic_info
)
from data_intelligence_system.utils.data_loader import load_data
from data_intelligence_system.utils.preprocessing import fill_missing_values
from data_intelligence_system.utils.timer import Timer

# استيراد المسارات المحدثة من config
from data_intelligence_system.config.paths_config import (
    PROCESSED_DATA_DIR as DATA_DIR,
    ANALYSIS_DIR,
)

OUTPUT_DIR = ANALYSIS_DIR / "analysis_output"
OUTLIER_REPORT_PATH = OUTPUT_DIR / "outliers_summary_report.csv"

# ===================== إعداد التسجيل =====================
logging.basicConfig(level=logging.INFO, format="%(asctime)s — %(levelname)s — %(message)s")
logger = logging.getLogger(__name__)


def detect_outliers_zscore(df: pd.DataFrame, threshold=3) -> pd.Series:
    logger.info("🧮 اكتشاف القيم الشاذة باستخدام Z-Score")
    df = fill_missing_values(df)
    numeric_cols = get_numerical_columns(df)
    if not numeric_cols:
        logger.warning("⚠️ لا توجد أعمدة رقمية لاكتشاف القيم الشاذة باستخدام Z-Score.")
        return pd.Series(False, index=df.index)

    z_scores = np.abs(stats.zscore(df[numeric_cols]))
    return (z_scores > threshold).any(axis=1)


def detect_outliers_iqr(df: pd.DataFrame, factor=1.5) -> pd.Series:
    logger.info("🧮 اكتشاف القيم الشاذة باستخدام IQR")
    df = fill_missing_values(df)
    numeric_cols = get_numerical_columns(df)
    if not numeric_cols:
        logger.warning("⚠️ لا توجد أعمدة رقمية لاكتشاف القيم الشاذة باستخدام IQR.")
        return pd.Series(False, index=df.index)

    Q1 = df[numeric_cols].quantile(0.25)
    Q3 = df[numeric_cols].quantile(0.75)
    IQR = Q3 - Q1
    return ((df[numeric_cols] < (Q1 - factor * IQR)) | (df[numeric_cols] > (Q3 + factor * IQR))).any(axis=1)


def detect_outliers_isolation_forest(df: pd.DataFrame, contamination=0.05) -> pd.Series:
    logger.info("🌲 اكتشاف القيم الشاذة باستخدام Isolation Forest")
    df = fill_missing_values(df)
    numeric_cols = get_numerical_columns(df)
    if not numeric_cols:
        logger.warning("⚠️ لا توجد أعمدة رقمية لاكتشاف القيم الشاذة باستخدام Isolation Forest.")
        return pd.Series(False, index=df.index)

    model = IsolationForest(contamination=contamination, random_state=42)
    preds = model.fit_predict(df[numeric_cols])  # ndarray من -1 و 1
    mask = preds == -1  # ndarray من قيم boolean
    return pd.Series(mask, index=df.index)  # تحويل إلى Series مع نفس الفهرس



@Timer("تحليل القيم الشاذة الفردي")
def run_outlier_detection(df: pd.DataFrame, method: str = "iqr", output_dir: Path = OUTPUT_DIR) -> dict:
    ensure_output_dir(output_dir)
    log_basic_info(df, "outlier_detection")

    if method == "iqr":
        mask = detect_outliers_iqr(df)
    elif method == "zscore":
        mask = detect_outliers_zscore(df)
    elif method in ["isolation", "isolation_forest"]:
        mask = detect_outliers_isolation_forest(df)
    else:
        raise ValueError(f"❌ الطريقة غير مدعومة: {method}")

    outliers_df = df[mask].copy()
    file_name = f"outliers_{method}.csv"
    save_dataframe(outliers_df, file_name, output_dir)

    logger.info(f"✅ تم حفظ النتائج في: {output_dir / file_name}")

    return {
        "method": method,
        "outliers_detected": len(outliers_df),
        "file_saved": str(output_dir / file_name),
        "outlier_rows": outliers_df
    }


@Timer("تحليل القيم الشاذة - دفعة كاملة")
def run_batch_detection():
    ensure_output_dir(OUTPUT_DIR)
    if not DATA_DIR.exists():
        logger.error(f"❌ مجلد البيانات غير موجود: {DATA_DIR}")
        return

    report = []
    for file_path in DATA_DIR.glob("*.csv"):
        try:
            df = load_data(str(file_path))
        except Exception as e:
            logger.error(f"⚠️ فشل في قراءة الملف {file_path.name}: {e}")
            continue

        if df.empty:
            logger.warning(f"⚠️ الملف {file_path.name} فارغ.")
            continue

        log_basic_info(df, file_path.name)

        summary = {
            'filename': file_path.name,
            'total_rows': len(df),
            'numeric_columns': len(get_numerical_columns(df)),
            'zscore_outliers': detect_outliers_zscore(df).sum(),
            'iqr_outliers': detect_outliers_iqr(df).sum(),
            'isolationforest_outliers': detect_outliers_isolation_forest(df).sum()
        }

        report.append(pd.DataFrame([summary]))

    if report:
        final_report = pd.concat(report, ignore_index=True)
        save_dataframe(final_report, "outliers_summary_report.csv", OUTPUT_DIR)
        logger.info(f"📊 تم حفظ التقرير الكامل: {OUTLIER_REPORT_PATH}")
    else:
        logger.warning("❗ لم يتم اكتشاف ملفات قابلة للمعالجة.")


if __name__ == "__main__":
    run_batch_detection()
