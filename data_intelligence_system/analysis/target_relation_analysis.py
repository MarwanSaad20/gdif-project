from pathlib import Path
import pandas as pd
import numpy as np
import logging
import seaborn as sns
import matplotlib.pyplot as plt

from scipy.stats import chi2_contingency, f_oneway
from sklearn.preprocessing import LabelEncoder

# ✅ استيرادات من جذر المشروع
from data_intelligence_system.analysis.analysis_utils import (
    ensure_output_dir,
    get_numerical_columns,
    get_categorical_columns,
    save_dataframe,
    save_plot,
    log_basic_info
)
from data_intelligence_system.utils.data_loader import load_data
from data_intelligence_system.utils.timer import Timer
from data_intelligence_system.config.paths_config import (
    PROCESSED_DATA_DIR as DATA_DIR,
    ANALYSIS_DIR
)

# إعداد المسارات
FILE_PATH = DATA_DIR / "clean_data.csv"
OUTPUT_DIR = ANALYSIS_DIR / "analysis_output"
SUMMARY_PATH = OUTPUT_DIR / "target_relation_summary.csv"

# إعداد السجل
logging.basicConfig(level=logging.INFO, format="%(asctime)s — %(levelname)s — %(message)s")
logger = logging.getLogger(__name__)


def anova_test(df, target, numerical_cols):
    logger.info("🔍 تحليل ANOVA بين الأعمدة الرقمية والمتغير الهدف")
    results = []
    groups = df[target].dropna().unique()

    for col in numerical_cols:
        try:
            group_samples = [df[df[target] == g][col].dropna() for g in groups]
            if any(len(s) < 2 for s in group_samples):
                logger.warning(f"⚠️ تجاهل ANOVA للعمود {col} بسبب قلة العينات")
                continue
            f_val, p_val = f_oneway(*group_samples)
            results.append((col, f_val, p_val))
        except Exception as e:
            logger.warning(f"⚠️ فشل ANOVA للعمود {col}: {e}")

    return pd.DataFrame(results, columns=['feature', 'f_statistic', 'p_value'])


def chi_square_test(df, target, categorical_cols):
    logger.info("🔍 تحليل Chi-Square بين الأعمدة الفئوية والمتغير الهدف")
    results = []
    for col in categorical_cols:
        try:
            contingency_table = pd.crosstab(df[col], df[target])
            chi2, p, dof, expected = chi2_contingency(contingency_table)
            if (expected < 5).any():
                logger.warning(f"⚠️ نتائج Chi-Square للعمود {col} قد تكون غير دقيقة (قيم متوقعة منخفضة)")
            results.append((col, chi2, p))
        except Exception as e:
            logger.warning(f"⚠️ فشل Chi-Square للعمود {col}: {e}")

    return pd.DataFrame(results, columns=['feature', 'chi2_statistic', 'p_value'])


def encode_target(df, target):
    if df[target].dtype == 'object' or df[target].nunique() < 15:
        le = LabelEncoder()
        df[target] = le.fit_transform(df[target])
    return df


@Timer("تحليل العلاقة مع الهدف")
def run_target_relation_analysis(df=None, target_col=None):
    ensure_output_dir(OUTPUT_DIR)

    if df is None:
        if not FILE_PATH.exists():
            logger.error(f"❌ لم يتم العثور على الملف: {FILE_PATH}")
            return
        try:
            df = load_data(FILE_PATH)
        except Exception as e:
            logger.error(f"⚠️ خطأ في تحميل الملف: {e}")
            return

    if df.empty or df.shape[1] == 0:
        logger.warning("⚠️ لا توجد بيانات صالحة للتحليل.")
        return

    fname = FILE_PATH.name
    log_basic_info(df, fname)

    target = target_col if target_col else df.columns[-1]
    if target not in df.columns:
        logger.warning(f"⚠️ لم يتم العثور على المتغير الهدف: {target}")
        return

    df = encode_target(df, target)

    num_cols = [col for col in get_numerical_columns(df) if col != target]
    cat_cols = [col for col in get_categorical_columns(df) if col != target]

    anova_results = anova_test(df, target, num_cols)
    chi2_results = chi_square_test(df, target, cat_cols)

    anova_results['test_type'] = 'ANOVA'
    chi2_results['test_type'] = 'Chi-Square'

    summary = pd.concat([anova_results, chi2_results], ignore_index=True)
    summary['file'] = fname

    top_features = summary.sort_values(by='p_value').head(3)['feature']

    for feature in top_features:
        plt.figure(figsize=(6, 4))
        try:
            if df[target].nunique() < 10:
                sns.boxplot(data=df, x=target, y=feature)
            else:
                sns.scatterplot(data=df, x=target, y=feature)
            plt.title(f"{feature} vs {target}")
            plot_path = OUTPUT_DIR / f"{fname}_{feature}_relation.png"
            save_plot(plt.gcf(), plot_path)
            plt.close()
            logger.info(f"✅ تم حفظ الرسم: {plot_path}")
        except Exception as e:
            logger.warning(f"⚠️ فشل رسم العلاقة بين {feature} و {target}: {e}")

    save_dataframe(summary, SUMMARY_PATH)
    logger.info(f"✅ تم حفظ ملخص العلاقة مع الهدف في: {SUMMARY_PATH}")
    return summary


def analyze_target_relation(df: pd.DataFrame, target: str = "target"):
    return run_target_relation_analysis(df, target_col=target)


if __name__ == "__main__":
    run_target_relation_analysis()
