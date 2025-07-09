import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import logging
from pathlib import Path

# استيرادات من جذر المشروع
from data_intelligence_system.analysis.analysis_utils import (
    ensure_output_dir,
    get_numerical_columns,
    save_plot,
    save_dataframe,
    log_basic_info
)
from data_intelligence_system.utils.data_loader import load_data
from data_intelligence_system.utils.timer import Timer  # ⏱️

# إعداد المسارات
BASE_DIR = Path(__file__).resolve().parents[2]
OUTPUT_DIR = BASE_DIR / 'data_intelligence_system' / 'analysis' / 'analysis_output'

# إعداد اللوغ
logging.basicConfig(level=logging.INFO, format="%(asctime)s — %(levelname)s — %(message)s")
logger = logging.getLogger(__name__)


# ==================== دوال التحليل ====================

def calculate_correlation(df: pd.DataFrame, method: str = "pearson") -> pd.DataFrame:
    numerical_cols = get_numerical_columns(df)
    if not numerical_cols:
        raise ValueError("❌ لا توجد أعمدة رقمية لحساب الارتباط.")
    return df[numerical_cols].corr(method=method)


def plot_correlation_heatmap(corr_matrix: pd.DataFrame, method: str, filename: str, output_dir: Path = OUTPUT_DIR):
    if corr_matrix.empty:
        logger.warning("⚠️ مصفوفة الارتباط فارغة، تخطي الرسم.")
        return
    fig, ax = plt.subplots(figsize=(12, 10))
    sns.heatmap(
        corr_matrix,
        annot=True,
        fmt=".2f",
        cmap="coolwarm",
        square=True,
        cbar_kws={"shrink": 0.8},
        ax=ax
    )
    ax.set_title(f"{method.capitalize()} Correlation Matrix", fontsize=16)
    save_plot(fig, filename, output_dir)
    logger.info(f"✅ تم حفظ خريطة الارتباط: {output_dir / filename}")


@Timer("تحليل الارتباط")
def run_correlation_analysis(df: pd.DataFrame, method: str = "pearson", output_dir: Path = OUTPUT_DIR) -> dict:
    ensure_output_dir(output_dir)
    log_basic_info(df, "correlation_analysis")

    try:
        corr_matrix = calculate_correlation(df, method=method)
        if corr_matrix.empty:
            logger.warning("⚠️ مصفوفة الارتباط فارغة، لا يمكن المتابعة.")
            return {}

        matrix_filename = f"correlation_matrix_{method}"
        heatmap_filename = f"correlation_heatmap_{method}.png"

        save_dataframe(corr_matrix, matrix_filename, output_dir)
        plot_correlation_heatmap(corr_matrix, method, heatmap_filename, output_dir)

        return {
            "correlation_matrix": corr_matrix,
            "matrix_file": f"{matrix_filename}.csv",
            "heatmap_file": heatmap_filename
        }

    except Exception as e:
        logger.error(f"❌ خطأ في تحليل الارتباط: {e}", exc_info=True)
        return {}


def compute_correlations(df: pd.DataFrame, method: str = "pearson") -> pd.DataFrame:
    numeric_df = df.select_dtypes(include=np.number)
    if numeric_df.empty:
        raise ValueError("❌ لا توجد أعمدة رقمية لحساب الارتباط.")
    return numeric_df.corr(method=method)


def generate_correlation_matrix(df: pd.DataFrame, method: str = "pearson") -> pd.DataFrame:
    return compute_correlations(df, method)


if __name__ == "__main__":
    test_file = BASE_DIR / 'data_intelligence_system' / 'data' / 'processed' / 'clean_data.csv'
    if test_file.exists():
        df_test = load_data(str(test_file))  # ✅ استخدام الدالة الموحدة
        results = run_correlation_analysis(df_test, method="pearson")
        print(results)
    else:
        logger.error(f"❌ ملف الاختبار غير موجود: {test_file}")
