import json
import logging
from pathlib import Path
from typing import Optional
import pandas as pd

# 🛠️ إعداد اللوجنغ
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("LoadExternalFiles")

# 🗂️ إعداد المسارات
BASE_DIR = Path(__file__).resolve().parent
EXTERNAL_FILES_DIR = BASE_DIR / "downloaded"
EXTERNAL_FILES_DIR.mkdir(parents=True, exist_ok=True)


def load_csv(filepath: Path, **kwargs) -> pd.DataFrame:
    try:
        df = pd.read_csv(filepath, **kwargs)
        logger.info(f"📄 تم تحميل CSV: {filepath.name} ({len(df)} صفوف)")
        return df
    except Exception as e:
        logger.error(f"❌ خطأ في تحميل CSV {filepath.name}: {e}")
        return pd.DataFrame()


def load_excel(filepath: Path, sheet_name: Optional[str] = 0, **kwargs) -> pd.DataFrame:
    try:
        df = pd.read_excel(filepath, sheet_name=sheet_name, **kwargs)
        logger.info(f"📄 تم تحميل Excel: {filepath.name} (ورقة: {sheet_name}) - ({len(df)} صفوف)")
        return df
    except Exception as e:
        logger.error(f"❌ خطأ في تحميل Excel {filepath.name}: {e}")
        return pd.DataFrame()


def load_json(filepath: Path, **kwargs) -> pd.DataFrame:
    try:
        with filepath.open('r', encoding='utf-8') as f:
            raw = json.load(f)

        data = raw[1] if isinstance(raw, list) and len(raw) == 2 and isinstance(raw[1], list) else raw
        df = pd.DataFrame(data)
        logger.info(f"📄 تم تحميل JSON: {filepath.name} ({len(df)} صفوف)")
        return df
    except Exception as e:
        logger.error(f"❌ خطأ في تحميل JSON {filepath.name}: {e}")
        return pd.DataFrame()


def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        logger.warning("⚠️ DataFrame فارغ. لا حاجة للتنظيف.")
        return df
    df = df.dropna(how='all')
    df.columns = [str(col).strip().lower().replace(" ", "_") for col in df.columns]
    logger.info("🧹 تم تنظيف البيانات: حذف الصفوف الفارغة وتوحيد أسماء الأعمدة.")
    return df


def load_file(filepath: Path, file_type: Optional[str] = None) -> pd.DataFrame:
    if not filepath.exists():
        logger.warning(f"⚠️ الملف غير موجود: {filepath.name}")
        return pd.DataFrame()

    ext = file_type.lower() if file_type else filepath.suffix.lower().lstrip(".")

    loader_map = {
        'csv': load_csv,
        'xlsx': load_excel,
        'xls': load_excel,
        'json': load_json,
    }

    loader = loader_map.get(ext)
    if loader:
        df = loader(filepath)
    else:
        logger.warning(f"⚠️ نوع غير مدعوم: {ext}")
        return pd.DataFrame()

    return clean_dataframe(df)


def main():
    logger.info(f"📂 بدء تحميل الملفات من: {EXTERNAL_FILES_DIR}")
    success_count = 0
    fail_count = 0

    for filepath in EXTERNAL_FILES_DIR.iterdir():
        if not filepath.is_file():
            continue
        df = load_file(filepath)
        if not df.empty:
            logger.info(f"✅ تم تجهيز البيانات من: {filepath.name}")
            success_count += 1
        else:
            logger.warning(f"⚠️ لم يتم تحميل بيانات من: {filepath.name}")
            fail_count += 1

    logger.info(f"📊 النتائج النهائية - ناجحة: {success_count}, فاشلة: {fail_count}")


if __name__ == "__main__":
    main()
