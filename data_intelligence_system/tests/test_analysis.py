# data_intelligence_system/tests/test_analysis.py

import pytest
import pandas as pd
import numpy as np
from pathlib import Path

# استيرادات التحليل من جذر المشروع
from data_intelligence_system.analysis import (
    descriptive_stats,
    correlation_analysis,
    outlier_detection,
    clustering_analysis,
    target_relation_analysis
)

# إعداد بيانات تجريبية بسيطة
@pytest.fixture(scope="module")
def sample_df():
    np.random.seed(42)
    df = pd.DataFrame({
        "age": np.random.randint(20, 60, size=50),
        "income": np.random.normal(5000, 1000, size=50),
        "gender": np.random.choice(["Male", "Female"], size=50),
        "date": pd.date_range("2024-01-01", periods=50, freq="D"),
        "target": np.random.choice(["A", "B"], size=50)
    })
    return df


def test_descriptive_stats(sample_df):
    result = descriptive_stats.generate_descriptive_stats(sample_df, save_outputs=False)
    assert "general_info" in result
    assert "numeric_summary" in result
    assert isinstance(result["general_info"], dict)
    assert len(result["numeric_summary"]) > 0


def test_correlation_analysis(sample_df):
    corr_df = correlation_analysis.generate_correlation_matrix(sample_df, method="pearson")
    assert isinstance(corr_df, pd.DataFrame)
    assert corr_df.shape[0] > 0
    # التحقق من وجود القيمة 1 على الأقل (الارتباط مع نفسه)
    assert np.allclose(np.diag(corr_df), 1)


def test_outlier_detection(sample_df):
    # تجربة IQR
    mask_iqr = outlier_detection.detect_outliers_iqr(sample_df)
    assert isinstance(mask_iqr, pd.Series)
    assert mask_iqr.dtype == bool

    # تجربة Z-Score
    mask_z = outlier_detection.detect_outliers_zscore(sample_df)
    assert isinstance(mask_z, (pd.Series, np.ndarray))  # ✅ التحديث هنا
    # إذا رجعت كـ ndarray تأكد أنها dtype=bool أيضًا
    if isinstance(mask_z, np.ndarray):
        assert mask_z.dtype == bool

    # تجربة Isolation Forest
    mask_iso = outlier_detection.detect_outliers_isolation_forest(sample_df)
    assert isinstance(mask_iso, pd.Series)



def test_clustering_kmeans(sample_df):
    result = clustering_analysis.run_clustering(sample_df, algorithm="kmeans", n_clusters=2,
                                                output_filename="test_clustered.csv")
    assert isinstance(result, dict)
    assert result["algorithm"] == "kmeans"
    assert "cluster_counts" in result
    assert "clustered_file" in result
    assert Path(result["clustered_file"]).suffix == ".csv"


def test_clustering_dbscan(sample_df):
    result = clustering_analysis.run_clustering(sample_df, algorithm="dbscan", dbscan_eps=0.3,
                                                output_filename="test_dbscan.csv")
    assert isinstance(result, dict)
    assert result["algorithm"] == "dbscan"
    assert "cluster_counts" in result
    assert "clustered_file" in result


def test_target_relation_analysis(sample_df):
    # إضافة عمود هدف بسيط للاختبار
    df_copy = sample_df.copy()
    summary = target_relation_analysis.run_target_relation_analysis(df_copy, target_col="target")
    assert isinstance(summary, pd.DataFrame)
    assert "feature" in summary.columns
    assert "p_value" in summary.columns


# ✅ يمكن إضافة اختبارات إضافية لدوال analysis_utils.py لاحقًا
# مثل: ensure_output_dir, save_plot, save_dataframe

