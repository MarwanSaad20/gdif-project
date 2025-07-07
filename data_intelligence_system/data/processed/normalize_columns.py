import os
import re
import pandas as pd
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("NormalizeColumns")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PROCESSED_DIR = os.path.join(BASE_DIR, 'data', 'processed')

DEFAULT_INPUT_FILE = os.path.join(PROCESSED_DIR, "clean_data.csv")
DEFAULT_OUTPUT_FILE = os.path.join(PROCESSED_DIR, "clean_data_normalized.csv")

def normalize_column_name(col: str) -> str:
    """
    Normalize a column name by:
    - converting to lowercase,
    - replacing spaces, hyphens, dots, slashes with underscores,
    - removing non-alphanumeric and underscore characters,
    - collapsing multiple underscores,
    - trimming leading/trailing underscores.

    Args:
        col (str): Original column name.

    Returns:
        str: Normalized column name.
    """
    col = col.lower()
    col = re.sub(r"[ \-\./]+", "_", col)
    col = re.sub(r"[^a-z0-9_]", "", col)
    col = re.sub(r"_+", "_", col)
    col = col.strip("_")
    return col

def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalize all column names in the DataFrame, avoiding duplicates by adding suffixes.

    Args:
        df (pd.DataFrame): Input DataFrame with original columns.

    Returns:
        pd.DataFrame: DataFrame with normalized and unique column names.
    """
    normalized_cols = []
    seen = set()
    for col in df.columns:
        norm_col = normalize_column_name(col)
        suffix = 1
        orig_norm_col = norm_col
        # Avoid duplicates by adding suffixes
        while norm_col in seen:
            suffix += 1
            norm_col = f"{orig_norm_col}_{suffix}"
        seen.add(norm_col)
        normalized_cols.append(norm_col)

    if len(set(normalized_cols)) != len(normalized_cols):
        logger.warning("⚠️ تعارضات في أسماء الأعمدة بعد التوحيد. يرجى التحقق.")

    df.columns = normalized_cols
    return df

def main(input_file: str = DEFAULT_INPUT_FILE, output_file: str = DEFAULT_OUTPUT_FILE):
    """
    Load CSV file, normalize columns, and save the normalized DataFrame.

    Args:
        input_file (str): مسار ملف الإدخال CSV.
        output_file (str): مسار ملف الإخراج CSV.
    """
    if not os.path.exists(input_file):
        logger.error(f"❌ الملف غير موجود: {input_file}")
        return

    try:
        logger.info(f"📂 قراءة الملف: {input_file}")
        df = pd.read_csv(input_file, encoding='utf-8')

        if df.empty:
            logger.warning(f"⚠️ الملف {input_file} فارغ.")
            return

        logger.info("🔄 توحيد أسماء الأعمدة...")
        df = normalize_columns(df)
        df.to_csv(output_file, index=False, encoding='utf-8')
        logger.info(f"✅ تم الحفظ: {output_file}")

    except Exception as e:
        logger.error(f"❌ حدث خطأ أثناء المعالجة: {e}")

if __name__ == "__main__":
    main()
