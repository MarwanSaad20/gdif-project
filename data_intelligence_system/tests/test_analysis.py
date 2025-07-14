import pytest
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler

from data_intelligence_system.analysis.descriptive_stats import compute_statistics
from data_intelligence_system.analysis.correlation_analysis import generate_correlation_matrix
from data_intelligence_system.analysis.outlier_detection import detect_outliers_iqr
from data_intelligence_system.analysis.clustering_analysis import apply_kmeans, apply_dbscan
from data_intelligence_system.analysis.target_relation_analysis import analyze_target_relation


# ============================
# 📄 بيانات اختبار وهمية
# ============================
@pytest.fixture
def sample_df():
    return pd.DataFrame({
        "feature1": [10, 20, 30, 40, 50],
        "feature2": [1, 2, 3, 4, 5],
        "feature3": [5, 6, 7, 8, 9],
        "target": [0, 1, 1, 0, 1]
    })


# ============================
# 🧪 descriptive_stats
# ============================
def test_compute_statistics(sample_df):
    stats = compute_statistics(sample_df)
    assert isinstance(stats, dict)
    assert "general_info" in stats
    assert "numeric_summary" in stats
    assert isinstance(stats["numeric_summary"], dict)
    assert stats["general_info"]["Number of Rows"] == 5
    assert "feature1" in stats["numeric_summary"]


def test_compute_statistics_empty():
    stats = compute_statistics(pd.DataFrame())
    # نتوقع أن تعود إما dict فارغة أو تحتوي على تحذير معين
    assert isinstance(stats, dict)
    # أو حسب السلوك الفعلي: مثلاً عدم وجود إحصائيات رقمية
    assert "numeric_summary" in stats
    assert stats["numeric_summary"] == {} or not stats["numeric_summary"]


# ============================
# 🧪 correlation_analysis
# ============================
def test_compute_correlations(sample_df):
    corr = generate_correlation_matrix(sample_df.drop(columns=["target"]))
    assert isinstance(corr, pd.DataFrame)
    assert not corr.isnull().values.any()
    assert corr.shape[0] == corr.shape[1]
    assert "feature1" in corr.columns
    assert "feature2" in corr.index


def test_compute_correlations_non_numeric():
    df = pd.DataFrame({"col1": ["a", "b", "c"]})
    with pytest.raises(Exception):
        generate_correlation_matrix(df)


# ============================
# 🧪 outlier_detection
# ============================
def test_detect_outliers_iqr(sample_df):
    outliers_mask = detect_outliers_iqr(sample_df.drop(columns=["target"]))
    assert isinstance(outliers_mask, pd.Series)
    assert outliers_mask.dtype == bool
    assert len(outliers_mask) == len(sample_df)


# ============================
# 🧪 clustering_analysis
# ============================
def test_kmeans_clustering(sample_df):
    data_scaled = StandardScaler().fit_transform(sample_df.drop(columns=["target"]))
    labels, inertia, silhouette = apply_kmeans(data_scaled, n_clusters=2)
    assert isinstance(labels, np.ndarray)
    assert len(labels) == sample_df.shape[0]
    assert isinstance(inertia, (int, float))
    assert silhouette is None or isinstance(silhouette, float)


def test_dbscan_clustering(sample_df):
    data_scaled = StandardScaler().fit_transform(sample_df.drop(columns=["target"]))
    labels = apply_dbscan(data_scaled, eps=0.5, min_samples=1)
    assert isinstance(labels, np.ndarray)
    assert len(labels) == sample_df.shape[0]


def test_kmeans_invalid_clusters(sample_df):
    data_scaled = StandardScaler().fit_transform(sample_df.drop(columns=["target"]))
    with pytest.raises(ValueError):
        apply_kmeans(data_scaled, n_clusters=0)


# ============================
# 🧪 target_relation_analysis
# ============================
def test_analyze_target_relation(sample_df):
    result = analyze_target_relation(sample_df, target="target")
    assert isinstance(result, pd.DataFrame)
    assert not result.empty
    assert "feature" in result.columns
    assert "p_value" in result.columns
    assert "test_type" in result.columns


def test_analyze_target_relation_invalid():
    df = pd.DataFrame({
        "f1": [1, 2, 3],
        "target": ["a", "b", "c"]  # غير رقمي
    })
    result = analyze_target_relation(df, target="target")
    assert isinstance(result, pd.DataFrame)
    assert set(result.columns) >= {"feature", "test_type", "p_value"}
