import pandas as pd
import numpy as np

def get_sample_dataframe(rows: int = 100) -> pd.DataFrame:
    """
    يعيد DataFrame وهمي يحتوي على أعمدة عددية وفئوية لاستخدامه في الاختبارات.

    Args:
        rows (int): عدد الصفوف المراد إنشاؤها (افتراضي 100).

    Returns:
        pd.DataFrame: بيانات وهمية.
    """
    np.random.seed(42)  # لجعل النتائج ثابتة عبر كل تشغيل

    data = {
        "id": range(1, rows + 1),
        "age": np.random.randint(18, 70, size=rows),
        "income": np.random.normal(50000, 15000, size=rows).round(2),
        "gender": np.random.choice(["Male", "Female"], size=rows),
        "city": np.random.choice(["Baghdad", "Basra", "Mosul", "Erbil"], size=rows),
        "is_active": np.random.choice([True, False], size=rows),
        "signup_date": pd.date_range("2023-01-01", periods=rows, freq="D")
    }

    df = pd.DataFrame(data)
    return df
