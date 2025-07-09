from pathlib import Path
import logging
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.cluster import KMeans, DBSCAN
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score

from data_intelligence_system.analysis.analysis_utils import (
    ensure_output_dir,
    get_numerical_columns,
    save_dataframe,
    save_plot,
    log_basic_info
)
from data_intelligence_system.utils.data_loader import load_data
from data_intelligence_system.utils.timer import Timer
from data_intelligence_system.ml_models.clustering.kmeans import KMeansClusteringModel  # تحديث الاستيراد لاستخدام الكلاس

logging.basicConfig(level=logging.INFO, format="%(asctime)s — %(levelname)s — %(message)s")
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data" / "processed"
OUTPUT_DIR = BASE_DIR / "analysis" / "analysis_output"
CLUSTERING_RESULTS_DIR = OUTPUT_DIR / "clustering"

ensure_output_dir(CLUSTERING_RESULTS_DIR)


def apply_kmeans(data: np.ndarray, n_clusters: int = 3) -> tuple[np.ndarray, float, float | None]:
    """
    تطبق خوارزمية KMeans على البيانات باستخدام كلاس KMeansClusteringModel.

    Returns:
        labels (np.ndarray): تسميات المجموعات.
        inertia (float): مجموع المربعات داخل المجموعات.
        silhouette (float | None): درجة السيلويت (None إذا كانت المجموعات أقل من 2).
    """
    model = KMeansClusteringModel(n_clusters=n_clusters, random_state=42)
    model.fit(pd.DataFrame(data))  # تحويل np.ndarray إلى DataFrame لاستخدام المعالجة الداخلية
    labels = model.predict(pd.DataFrame(data))
    inertia = model.model.inertia_
    silhouette = model.evaluate(pd.DataFrame(data)) if n_clusters > 1 else None
    return labels, inertia, silhouette


def apply_dbscan(data: np.ndarray, eps: float = 0.5, min_samples: int = 5) -> np.ndarray:
    """
    تطبق خوارزمية DBSCAN على البيانات.

    Returns:
        labels (np.ndarray): تسميات المجموعات، -1 تعني ضوضاء.
    """
    model = DBSCAN(eps=eps, min_samples=min_samples)
    labels = model.fit_predict(data)
    return labels


def reduce_dimensions(data: np.ndarray, n_components: int = 2) -> np.ndarray:
    """
    تقليل الأبعاد باستخدام PCA.

    Returns:
        data_2d (np.ndarray): بيانات منخفضة الأبعاد.
    """
    pca = PCA(n_components=n_components)
    return pca.fit_transform(data)


def plot_clusters(data_2d: np.ndarray, labels: np.ndarray, title: str, path: Path) -> None:
    """
    رسم المجموعات ثنائية الأبعاد وحفظ الرسم.

    Args:
        data_2d: بيانات ثنائية الأبعاد.
        labels: تسميات المجموعات.
        title: عنوان الرسم.
        path: مسار حفظ الصورة.
    """
    plt.figure(figsize=(8, 6))
    unique_labels = np.unique(labels)
    palette = sns.color_palette('Set2', n_colors=len(unique_labels))
    sns.scatterplot(x=data_2d[:, 0], y=data_2d[:, 1], hue=labels, palette=palette, legend="full")
    plt.title(title)
    plt.xlabel("Component 1")
    plt.ylabel("Component 2")
    plt.legend(loc='best', fontsize='small')
    plt.tight_layout()
    save_plot(plt.gcf(), path)
    plt.close()


@Timer("تشغيل تحليل التجميع")
def run_clustering(df: pd.DataFrame,
                   algorithm: str = "kmeans",
                   n_clusters: int = 3,
                   dbscan_eps: float = 0.5,
                   dbscan_min_samples: int = 5,
                   output_filename: str = "clustered_data.csv") -> dict:
    """
    تنفيذ تحليل التجميع على DataFrame وحفظ النتائج.

    Returns:
        dict: ملخص النتائج مع مسارات الملفات.
    """
    try:
        log_basic_info(df, output_filename)

        num_cols = get_numerical_columns(df)
        if len(num_cols) < 2:
            logger.warning("📉 لا يوجد أعمدة رقمية كافية للتجميع.")
            return {}

        df_clean = df[num_cols].dropna()
        if df_clean.shape[0] < 10:
            logger.warning("📉 عدد الصفوف بعد تنظيف القيم المفقودة قليل جداً.")
            return {}

        df_scaled = StandardScaler().fit_transform(df_clean)
        df_2d = reduce_dimensions(df_scaled)

        algo_lower = algorithm.lower()
        if algo_lower == "kmeans":
            labels, inertia, silhouette = apply_kmeans(df_scaled, n_clusters=n_clusters)
            df.loc[df_clean.index, "cluster"] = labels
            algo_desc = f"kmeans_{n_clusters}"
            plot_title = f"KMeans Clustering (k={n_clusters})"
        elif algo_lower == "dbscan":
            labels = apply_dbscan(df_scaled, eps=dbscan_eps, min_samples=dbscan_min_samples)
            df.loc[df_clean.index, "cluster"] = labels
            inertia = None
            silhouette = None
            algo_desc = f"dbscan_eps{dbscan_eps}_min{dbscan_min_samples}"
            plot_title = "DBSCAN Clustering"
        else:
            raise ValueError(f"❌ الخوارزمية غير مدعومة: {algorithm}")

        plot_name = f"{output_filename.replace('.csv', '')}_{algo_desc}.png"
        plot_path = CLUSTERING_RESULTS_DIR / plot_name
        plot_clusters(df_2d, labels, plot_title, plot_path)

        result_path = CLUSTERING_RESULTS_DIR / output_filename
        save_dataframe(df, result_path)

        logger.info(f"✅ تم حفظ نتائج التجميع: {result_path}")
        return {
            "algorithm": algorithm,
            "n_clusters": n_clusters if algo_lower == "kmeans" else None,
            "cluster_counts": pd.Series(labels).value_counts().to_dict(),
            "clustered_file": str(result_path),
            "plot_file": str(plot_path),
            "inertia": inertia,
            "silhouette_score": silhouette
        }

    except Exception as e:
        logger.error(f"❌ خطأ في التجميع: {e}", exc_info=True)
        return {}


def run_batch_clustering() -> None:
    """
    تشغيل التجميع على دفعة من ملفات CSV في مجلد البيانات وحفظ الملخص.
    """
    summary = []
    if not DATA_DIR.exists():
        logger.error(f"❌ مجلد البيانات غير موجود: {DATA_DIR}")
        return

    for file_path in DATA_DIR.glob("*.csv"):
        try:
            df = load_data(str(file_path))
            result = run_clustering(df, algorithm="kmeans", n_clusters=3,
                                    output_filename=f"{file_path.stem}_clustered.csv")
            if result:
                summary.append(result)
        except Exception as e:
            logger.error(f"❌ فشل تحميل الملف {file_path.name}: {e}", exc_info=True)

    if summary:
        summary_df = pd.DataFrame(summary)
        summary_path = CLUSTERING_RESULTS_DIR / "clustering_summary.csv"
        summary_df.to_csv(summary_path, index=False)
        logger.info(f"📄 تم حفظ ملخص جميع التجميعات في: {summary_path}")
    else:
        logger.warning("⚠️ لم يتم تنفيذ أي تحليل تجميع بسبب نقص البيانات.")


if __name__ == "__main__":
    run_batch_clustering()
