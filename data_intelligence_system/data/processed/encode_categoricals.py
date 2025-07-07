from pathlib import Path
import pandas as pd
import logging
from sklearn.preprocessing import LabelEncoder

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("EncodeCategoricals")

def encode_categoricals(df: pd.DataFrame) -> pd.DataFrame:
    """
    ترميز الأعمدة النصية في DataFrame.
    - الأعمدة التي تحتوي على قيمتين فريدتين تُرمّز باستخدام Label Encoding.
    - الأعمدة التي تحتوي أكثر من قيمتين تُرمّز باستخدام One-Hot Encoding (إلا إذا تجاوزت حدًا معينًا).

    Args:
        df (pd.DataFrame): DataFrame يحتوي على بيانات خام.

    Returns:
        pd.DataFrame: نسخة جديدة من DataFrame مع الأعمدة المشفرة.
    """
    if df.empty:
        logger.warning("DataFrame فارغ، لا يوجد شيء لترميزه.")
        return df

    df_encoded = df.copy()
    categorical_cols = df_encoded.select_dtypes(include=['object', 'category']).columns.tolist()

    if not categorical_cols:
        logger.info("لا توجد أعمدة نصية لترميزها.")
        return df_encoded

    one_hot_cols = []

    for col in categorical_cols:
        if df_encoded[col].isnull().any():
            logger.warning(f"عمود '{col}' يحتوي على قيم فارغة سيتم ملؤها مؤقتًا بـ 'missing'")
            df_encoded[col] = df_encoded[col].fillna('missing')

        unique_vals = df_encoded[col].nunique(dropna=False)
        if unique_vals <= 2:
            le = LabelEncoder()
            df_encoded[col] = le.fit_transform(df_encoded[col])
            logger.info(f"تم ترميز العمود '{col}' باستخدام Label Encoding")
        else:
            one_hot_cols.append(col)

    if one_hot_cols:
        # ✅ التعديل: تجاهل الأعمدة التي تحتوي على عدد ضخم من القيم الفريدة
        MAX_UNIQUE_THRESHOLD = 1000
        one_hot_cols = [col for col in one_hot_cols if df_encoded[col].nunique() <= MAX_UNIQUE_THRESHOLD]

        if not one_hot_cols:
            logger.warning("🚫 تم تجاهل جميع الأعمدة متعددة القيم لتجنب استهلاك الذاكرة المفرط.")
        else:
            dummies = pd.get_dummies(df_encoded[one_hot_cols], prefix=one_hot_cols, drop_first=False)
            df_encoded = df_encoded.drop(columns=one_hot_cols)
            df_encoded = pd.concat([df_encoded, dummies], axis=1)
            logger.info(f"تم ترميز الأعمدة {one_hot_cols} باستخدام One-Hot Encoding")

    return df_encoded


def main(input_file: Path = None, output_file: Path = None):
    """
    الوظيفة الرئيسية لتحميل ملف CSV، ترميز الأعمدة النصية، وحفظ النتيجة.
    """
    BASE_DIR = Path(__file__).resolve().parent  # مجلد processed

    input_file = input_file or (BASE_DIR / "clean_data_filled.csv")
    output_file = output_file or (BASE_DIR / "clean_data_encoded.csv")

    if not input_file.exists():
        logger.error(f"❌ الملف غير موجود: {input_file}")
        return

    try:
        logger.info(f"📂 قراءة الملف: {input_file}")
        df = pd.read_csv(input_file, encoding="utf-8")

        logger.info("🔄 ترميز المتغيرات النوعية...")
        df_encoded = encode_categoricals(df)

        output_file.parent.mkdir(parents=True, exist_ok=True)
        df_encoded.to_csv(output_file, index=False, encoding="utf-8")
        logger.info(f"✅ تم الحفظ: {output_file}")

    except Exception as e:
        logger.error(f"❌ خطأ أثناء المعالجة: {e}")


if __name__ == "__main__":
    main()
