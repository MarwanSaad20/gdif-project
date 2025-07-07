# utils/feature_utils.py

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.feature_selection import SelectKBest, f_classif, f_regression
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor

# ✅ تكامل مع لوجر النظام
from data_intelligence_system.utils.logger import get_logger

logger = get_logger(name="FeatureUtils")


def select_k_best_features(X, y, task='classification', k=10):
    """
    اختيار أفضل K ميزات باستخدام اختبارات إحصائية (ANOVA أو الانحدار).
    """
    if task == 'classification':
        selector = SelectKBest(score_func=f_classif, k=k)
    else:
        selector = SelectKBest(score_func=f_regression, k=k)

    selector.fit(X, y)
    scores = selector.scores_
    pvalues = selector.pvalues_
    support = selector.get_support()

    scores_df = pd.DataFrame({
        "Feature": X.columns,
        "Score": scores,
        "P-Value": pvalues,
        "Selected": support
    }).sort_values(by="Score", ascending=False)

    selected_features = scores_df[scores_df["Selected"]]["Feature"].tolist()
    return selected_features, scores_df


def plot_feature_scores(feature_names, scores, top_n=20, title="Top Feature Scores", save_path=None):
    """
    رسم شريطي لأفضل الميزات بناءً على الدرجات.
    """
    if len(feature_names) != len(scores):
        raise ValueError("Feature names and scores must have the same length.")

    scores_df = pd.DataFrame({"Feature": feature_names, "Score": scores})
    scores_df = scores_df.sort_values("Score", ascending=False).head(top_n)

    plt.figure(figsize=(10, 6))
    sns.barplot(x="Score", y="Feature", data=scores_df, palette="viridis")
    plt.title(title)
    plt.tight_layout()

    if save_path:
        plt.savefig(save_path)
        plt.close()
    else:
        plt.show()


def derive_features(df):
    """
    إنشاء ميزات جديدة بناءً على قواعد مخصصة (مثال).
    """
    df = df.copy()

    if 'income' in df.columns and 'expenses' in df.columns:
        df['net_savings'] = df['income'] - df['expenses']

    if 'clicks' in df.columns and 'impressions' in df.columns:
        df['ctr'] = df['clicks'] / (df['impressions'].replace(0, np.nan) + 1e-6)

    if 'city' in df.columns and 'country' in df.columns:
        df['location'] = df['city'].astype(str) + ', ' + df['country'].astype(str)

    return df


def select_features_by_importance(X, y, task='classification', top_n=10):
    """
    اختيار أفضل الميزات بناءً على أهمية النماذج باستخدام Random Forest.
    """
    if task == 'classification':
        model = RandomForestClassifier(n_estimators=100, random_state=42)
    else:
        model = RandomForestRegressor(n_estimators=100, random_state=42)

    model.fit(X, y)
    importances = model.feature_importances_

    feature_importance_df = pd.DataFrame({
        "Feature": X.columns,
        "Importance": importances
    }).sort_values(by="Importance", ascending=False)

    selected_features = feature_importance_df.head(top_n)["Feature"].tolist()
    return selected_features, feature_importance_df
