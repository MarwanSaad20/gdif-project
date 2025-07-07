import os
import pandas as pd
from typing import Dict, Any, Optional
from datetime import datetime

from data_intelligence_system.reports.report_config import REPORT_CONFIG
from data_intelligence_system.analysis.descriptive_stats import generate_descriptive_stats
from data_intelligence_system.analysis.correlation_analysis import generate_correlation_matrix
from data_intelligence_system.data.processed.validate_clean_data import validate  # ✅ مضاف حديثًا

class ReportDataLoader:
    """
    مسؤول عن تحميل وتجهيز البيانات المطلوبة لتوليد التقارير.
    يشمل تحميل ملفات CSV، توليد التحليلات الوصفية، والارتباطية.
    يحفظ البيانات المحمّلة لتفادي إعادة القراءة المتكررة.
    """

    def __init__(self, processed_data_path: Optional[str] = None):
        base_dir = os.path.abspath(os.path.dirname(__file__))
        default_data_path = os.path.join(base_dir, "..", "data", "processed")
        self.data_path = processed_data_path or default_data_path
        self.loaded_datasets: Dict[str, pd.DataFrame] = {}
        self.metadata: Dict[str, Any] = {}

    def load_all_csvs(self) -> Dict[str, pd.DataFrame]:
        """
        تحميل جميع ملفات CSV من مجلد البيانات المعالجة.
        يقوم بتخزين البيانات في self.loaded_datasets لتجنب إعادة القراءة.
        """
        if not os.path.exists(self.data_path):
            raise FileNotFoundError(f"المسار غير موجود: {self.data_path}")

        for file in os.listdir(self.data_path):
            if file.endswith(".csv"):
                filepath = os.path.join(self.data_path, file)
                try:
                    df = pd.read_csv(filepath)
                    if df.empty:
                        print(f"[تحذير] الملف فارغ: {file} -- تم تخطيه")
                        continue

                    # ✅ التحقق من جودة البيانات بعد التحميل
                    try:
                        validate(df)
                    except Exception as ve:
                        print(f"[تحذير] فشل التحقق من الملف {file}: {ve}")

                    self.loaded_datasets[file] = df

                except pd.errors.EmptyDataError:
                    print(f"[تحذير] لا يمكن قراءة الملف (فارغ): {file} -- تم تخطيه")
                except Exception as e:
                    print(f"[خطأ] فشل قراءة الملف {file}: {e} -- تم تخطيه")
        return self.loaded_datasets

    def get_dataset(self, filename: str) -> pd.DataFrame:
        """
        إرجاع DataFrame بناءً على اسم الملف.
        يحاول استخدام النسخة المحمّلة مسبقًا إن وجدت.
        """
        if filename in self.loaded_datasets:
            return self.loaded_datasets[filename]

        path = os.path.join(self.data_path, filename)
        if not os.path.exists(path):
            raise FileNotFoundError(f"الملف غير موجود: {path}")

        df = pd.read_csv(path)

        # ✅ التحقق من جودة البيانات بعد التحميل الفردي
        try:
            validate(df)
        except Exception as ve:
            print(f"[تحذير] فشل التحقق من الملف {filename}: {ve}")

        self.loaded_datasets[filename] = df
        return df

    def generate_statistics(self, filename: str) -> Dict[str, Any]:
        """
        استدعاء دالة التحليل الوصفي لتوليد إحصائيات ملف معين.
        """
        full_path = os.path.join(self.data_path, filename)
        generate_descriptive_stats(full_path, output_dir=REPORT_CONFIG["output_dir"])
        return {"status": "generated", "file": filename}

    def generate_correlation(self, filename: str, method: str = "pearson") -> pd.DataFrame:
        """
        توليد مصفوفة الارتباط من ملف معين باستخدام دالة generate_correlation_matrix.
        """
        df = self.get_dataset(filename)
        corr_matrix = generate_correlation_matrix(df, method=method)
        return corr_matrix

    def load_summary_for_report(self, filename: str) -> Dict[str, Any]:
        """
        تحميل وصف موجز (ملخص) لملف معين لاستخدامه في التقرير.
        """
        df = self.get_dataset(filename)
        summary = {
            "file_name": filename,
            "n_rows": df.shape[0],
            "n_cols": df.shape[1],
            "missing_values": int(df.isnull().sum().sum()),
            "missing_%": round(df.isnull().mean().mean() * 100, 2),
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        }
        return summary

    def get_kpi_summary(self, filename: str) -> Dict[str, Any]:
        """
        توليد بيانات ملخصات مؤشرات الأداء (KPIs) لاستخدامها في تقارير KPI.
        """
        df = self.get_dataset(filename)
        kpis = {
            "total_records": df.shape[0],
            "total_features": df.shape[1],
            "null_rate": round(df.isnull().mean().mean() * 100, 2),
            "last_updated": datetime.now().strftime("%Y-%m-%d"),
        }
        return kpis


if __name__ == "__main__":
    loader = ReportDataLoader()
    datasets = loader.load_all_csvs()
    for name, df in datasets.items():
        print(f"🔹 Dataset: {name} | Shape: {df.shape}")
