# utils/feature_utils.py

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.feature_selection import SelectKBest, f_classif, f_regression
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from typing import Tuple, List, Literal, Optional

from data_intelligence_system.utils.logger import get_logger

logger = get_logger(name="FeatureUtils")


def select_k_best_features(
    X: pd.DataFrame,
    y: pd.Series,
    task: Literal['classification', 'regression'] = 'classification',
    k: int = 10
) -> Tuple[List[str], pd.DataFrame]:
    """
    اختيار أفضل K ميزات باستخدام SelectKBest.

    Args:
        X: بيانات الإدخال.
        y: الهدف.
        task: نوع المهمة ("classification" أو "regression").
        k: عدد الميزات المراد اختيارها.

    Returns:
        قائمة بأسماء الميزات المختارة، وجدول مفصل بالدرجات والقيم الاحتمالية.
    """
    if X.isnull().any().any() or y.isnull().any():
        logger.warning("X أو y تحتوي على قيم مفقودة. تأكد من المعالجة المسبقة.")
    
    if task == 'classification':
        selector = SelectKBest(score_func=f_classif, k=k)
    else:
        selector = SelectKBest(score_func=f_regression, k=k)

    selector.fit(X, y)
    scores_df = pd.DataFrame({
        "Feature": X.columns,
        "Score": selector.scores_,
        "P-Value": selector.pvalues_,
        "Selected": selector.get_support()
    }).sort_values(by="Score", ascending=False)

    selected_features = scores_df[scores_df["Selected"]]["Feature"].tolist()
    logger.info(f"تم اختيار {len(selected_features)} من الميزات باستخدام SelectKBest.")
    return selected_features, scores_df


def plot_feature_scores(
    feature_names: List[str],
    scores: List[float],
    top_n: int = 20,
    title: str = "Top Feature Scores",
    save_path: Optional[str] = None
) -> None:
    """
    رسم شريطي لأفضل الميزات بناءً على الدرجات.

    Raises:
        ValueError: إذا لم تتطابق أطوال الميزات والدرجات.
    """
    if len(feature_names) != len(scores):
        logger.error("عدم تطابق بين عدد الميزات وعدد الدرجات.")
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
        logger.info(f"تم حفظ الرسم في {save_path}")
    else:
        plt.show()


def generate_derived_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    إنشاء ميزات جديدة بناءً على قواعد مخصصة.

    Returns:
        DataFrame معدل بميزات جديدة.
    """
    df = df.copy()
    new_cols = []

    if {'income', 'expenses'}.issubset(df.columns):
        df['net_savings'] = df['income'] - df['expenses']
        new_cols.append('net_savings')

    if {'clicks', 'impressions'}.issubset(df.columns):
        df['ctr'] = df['clicks'] / (df['impressions'].replace(0, np.nan) + 1e-6)
        new_cols.append('ctr')

    if {'city', 'country'}.issubset(df.columns):
        df['location'] = df['city'].astype(str) + ', ' + df['country'].astype(str)
        new_cols.append('location')

    logger.info(f"تم توليد الميزات التالية: {new_cols}" if new_cols else "لم يتم توليد ميزات.")
    return df


def select_features_by_importance(
    X: pd.DataFrame,
    y: pd.Series,
    task: Literal['classification', 'regression'] = 'classification',
    top_n: int = 10
) -> Tuple[List[str], pd.DataFrame]:
    """
    اختيار الميزات بناءً على أهمية نموذج Random Forest.

    Returns:
        قائمة بالميزات المختارة، وجدول تفصيلي بالأهمية.
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
    logger.info(f"تم اختيار {len(selected_features)} من الميزات بناءً على أهمية النموذج.")
    return selected_features, feature_importance_df
