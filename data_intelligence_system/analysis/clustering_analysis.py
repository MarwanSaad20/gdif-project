import os
import sys
import logging
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.cluster import KMeans, DBSCAN
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score

# ================= إعداد المسارات =================

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
DATA_DIR = os.path.join(BASE_DIR, "data_intelligence_system", "data", "processed")
OUTPUT_DIR = os.path.join(BASE_DIR, "data_intelligence_system", "analysis", "analysis_output")
CLUSTERING_RESULTS_DIR = os.path.join(OUTPUT_DIR, "clustering")

# ================= استيراد وحدات مساعدة من الجذر =================

from data_intelligence_system.analysis.analysis_utils import (
    ensure_output_dir,
    get_numerical_columns,
    save_dataframe,
    save_plot,
    log_basic_info
)
from data_intelligence_system.utils.data_loader import load_data

# ================= إعداد التسجيل =================

logging.basicConfig(level=logging.INFO, format="%(asctime)s — %(levelname)s — %(message)s")
logger = logging.getLogger(__name__)

# إنشاء مجلد الإخراج إن لم يكن موجودًا
ensure_output_dir(CLUSTERING_RESULTS_DIR)

# ================= دوال التجميع =================

def apply_kmeans(data, n_clusters=3):
    model = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    labels = model.fit_predict(data)
    inertia = model.inertia_
    silhouette = silhouette_score(data, labels) if n_clusters > 1 else None
    return labels, inertia, silhouette


def apply_dbscan(data, eps=0.5, min_samples=5):
    model = DBSCAN(eps=eps, min_samples=min_samples)
    labels = model.fit_predict(data)
    return labels


def reduce_dimensions(data, n_components=2):
    pca = PCA(n_components=n_components)
    return pca.fit_transform(data)


def plot_clusters(data_2d, labels, title, path):
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


def run_clustering(df: pd.DataFrame,
                   algorithm: str = "kmeans",
                   n_clusters: int = 3,
                   dbscan_eps: float = 0.5,
                   dbscan_min_samples: int = 5,
                   output_filename: str = "clustered_data.csv") -> dict:
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

        if algorithm.lower() == "kmeans":
            labels, inertia, silhouette = apply_kmeans(df_scaled, n_clusters=n_clusters)
            df.loc[df_clean.index, "cluster"] = labels
            algo_desc = f"kmeans_{n_clusters}"
            plot_title = f"KMeans Clustering (k={n_clusters})"
        elif algorithm.lower() == "dbscan":
            labels = apply_dbscan(df_scaled, eps=dbscan_eps, min_samples=dbscan_min_samples)
            df.loc[df_clean.index, "cluster"] = labels
            inertia = None
            silhouette = None
            algo_desc = f"dbscan_eps{dbscan_eps}_min{dbscan_min_samples}"
            plot_title = "DBSCAN Clustering"
        else:
            raise ValueError(f"❌ الخوارزمية غير مدعومة: {algorithm}")

        plot_name = f"{output_filename.replace('.csv', '')}_{algo_desc}.png"
        plot_path = os.path.join(CLUSTERING_RESULTS_DIR, plot_name)
        plot_clusters(df_2d, labels, plot_title, plot_path)

        result_path = os.path.join(CLUSTERING_RESULTS_DIR, output_filename)
        save_dataframe(df, result_path)

        logger.info(f"✅ تم حفظ نتائج التجميع: {result_path}")
        return {
            "algorithm": algorithm,
            "n_clusters": n_clusters if algorithm.lower() == "kmeans" else None,
            "cluster_counts": pd.Series(labels).value_counts().to_dict(),
            "clustered_file": result_path,
            "plot_file": plot_path,
            "inertia": inertia,
            "silhouette_score": silhouette
        }

    except Exception as e:
        logger.error(f"❌ خطأ في التجميع: {e}", exc_info=True)
        return {}


def run_batch_clustering():
    summary = []
    if not os.path.exists(DATA_DIR):
        logger.error(f"❌ مجلد البيانات غير موجود: {DATA_DIR}")
        return

    for fname in os.listdir(DATA_DIR):
        if fname.endswith(".csv"):
            file_path = os.path.join(DATA_DIR, fname)
            try:
                df = load_data(file_path)
                result = run_clustering(df, algorithm="kmeans", n_clusters=3,
                                        output_filename=f"{fname.replace('.csv','')}_clustered.csv")
                if result:
                    summary.append(result)
            except Exception as e:
                logger.error(f"❌ فشل تحميل الملف {fname}: {e}", exc_info=True)

    if summary:
        summary_df = pd.DataFrame(summary)
        summary_path = os.path.join(CLUSTERING_RESULTS_DIR, "clustering_summary.csv")
        summary_df.to_csv(summary_path, index=False)
        logger.info(f"📄 تم حفظ ملخص جميع التجميعات في: {summary_path}")
    else:
        logger.warning("⚠️ لم يتم تنفيذ أي تحليل تجميع بسبب نقص البيانات.")


if __name__ == "__main__":
    run_batch_clustering()
