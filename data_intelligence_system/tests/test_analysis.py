import pytest
import pandas as pd
import numpy as np
from unittest.mock import patch

# استيراد مطلق من جذر المشروع
from data_intelligence_system.analysis import (
    descriptive_stats,
    correlation_analysis,
    outlier_detection,
    clustering_analysis,
    target_relation_analysis,
    analysis_utils
)


# ---- بيانات مساعدة للاختبارات ----

@pytest.fixture
def sample_numeric_df():
    return pd.DataFrame({
        "A": [1, 2, 3, 4, 5],
        "B": [5, 4, 3, 2, 1]
    })


@pytest.fixture
def sample_mixed_df():
    return pd.DataFrame({
        "num": [1, 2, 3, 4],
        "cat": ["a", "b", "a", "b"],
        "flag": [True, False, True, False]
    })


@pytest.fixture
def sample_target_df():
    return pd.DataFrame({
        "feature": [1, 2, 3, 4],
        "target": [10, 20, 30, 40]
    })


# ---- descriptive_stats.py ----

def test_analyze_numerical_columns(sample_numeric_df):
    summary = descriptive_stats.analyze_numerical_columns(sample_numeric_df)
    assert isinstance(summary, pd.DataFrame)
    assert not summary.empty
    assert "mean" in summary.columns or "std" in summary.columns


def test_analyze_categorical_columns(sample_mixed_df):
    summary = descriptive_stats.analyze_categorical_columns(sample_mixed_df[["cat"]])
    assert isinstance(summary, pd.DataFrame)
    assert "count" in summary.columns


def test_analyze_datetime_columns():
    df = pd.DataFrame({
        "dates": pd.date_range("2023-01-01", periods=5, freq="D")
    })
    summary = descriptive_stats.analyze_datetime_columns(df)
    assert isinstance(summary, pd.DataFrame)
    assert "min" in summary.columns or "max" in summary.columns


# ---- correlation_analysis.py ----

def test_calculate_correlations(sample_numeric_df):
    corr = correlation_analysis.calculate_correlations(sample_numeric_df)
    assert isinstance(corr, pd.DataFrame)
    assert "A" in corr.columns and "B" in corr.columns


# ---- outlier_detection.py ----

def test_detect_outliers(sample_numeric_df):
    outliers = outlier_detection.detect_outliers(sample_numeric_df, method="zscore", threshold=2.0)
    assert isinstance(outliers, pd.DataFrame)
    assert set(outliers.columns) == set(sample_numeric_df.columns)


# ---- clustering_analysis.py ----

def test_perform_clustering(sample_numeric_df):
    clustered = clustering_analysis.perform_clustering(sample_numeric_df, n_clusters=2)
    assert isinstance(clustered, pd.DataFrame)
    assert "cluster" in clustered.columns


# ---- target_relation_analysis.py ----

def test_analyze_relation_to_target(sample_target_df):
    summary = target_relation_analysis.analyze_relation_to_target(
        sample_target_df, feature_col="feature", target_col="target"
    )
    assert isinstance(summary, dict)
    assert "correlation" in summary


# ---- analysis_utils.py ----

def test_normalize_dataframe(sample_numeric_df):
    norm_df = analysis_utils.normalize_dataframe(sample_numeric_df)
    assert isinstance(norm_df, pd.DataFrame)
    assert np.allclose(norm_df.mean(), 0, atol=1e-1) or np.allclose(norm_df.std(), 1, atol=1e-1)


def test_calculate_iqr(sample_numeric_df):
    iqr_values = analysis_utils.calculate_iqr(sample_numeric_df)
    assert isinstance(iqr_values, dict)
    assert all(isinstance(v, (int, float)) for v in iqr_values.values())


if __name__ == "__main__":
    pytest.main(["-v", __file__])
