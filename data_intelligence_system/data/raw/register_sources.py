from pathlib import Path
import csv
import json
import logging

# 📂 المسارات
BASE_DIR = Path(__file__).resolve().parents[1]
RAW_DIR = BASE_DIR / 'data' / 'raw'
REGISTRY_PATH = RAW_DIR / "sources_registry.csv"

HEADERS = [
    "filename", "acquisition_date", "source", "format",
    "row_count", "column_count", "verified", "description"
]

# 🛠️ إعداد اللوج
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("RegisterSources")


def load_existing_registry() -> set:
    """تحميل أسماء الملفات المسجلة مسبقًا"""
    if not REGISTRY_PATH.exists():
        return set()
    try:
        with REGISTRY_PATH.open("r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            return {row["filename"] for row in reader}
    except Exception as e:
        logger.error(f"❌ خطأ عند قراءة سجل المصادر: {e}")
        return set()


def get_metadata_files() -> list:
    """جلب جميع ملفات .metadata.json ضمن مجلد raw"""
    try:
        return [p for p in RAW_DIR.rglob("*.metadata.json") if p.is_file()]
    except Exception as e:
        logger.error(f"❌ خطأ عند جلب ملفات البيانات الوصفية: {e}")
        return []


def parse_metadata(path: Path) -> dict | None:
    """قراءة وتحليل ملف metadata"""
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"❌ خطأ عند قراءة ملف التعريف {path.name}: {e}")
        return None


def append_to_registry(metadata: dict) -> None:
    """إضافة مصدر جديد إلى السجل"""
    is_new_file = not REGISTRY_PATH.exists()
    try:
        with REGISTRY_PATH.open("a", encoding="utf-8", newline='') as f:
            writer = csv.DictWriter(f, fieldnames=HEADERS)
            if is_new_file:
                writer.writeheader()
            writer.writerow({
                "filename": metadata.get("filename", ""),
                "acquisition_date": metadata.get("acquisition_date", ""),
                "source": metadata.get("source", "Unknown"),
                "format": metadata.get("format", ""),
                "row_count": metadata.get("row_count", 0),
                "column_count": metadata.get("column_count", 0),
                "verified": metadata.get("verified", False),
                "description": metadata.get("description", "")
            })
        logger.info(f"✅ تم تسجيل المصدر: {metadata.get('filename')}")
    except Exception as e:
        logger.error(f"❌ خطأ عند تسجيل المصدر {metadata.get('filename')}: {e}")


def main() -> None:
    logger.info("📋 بدء تسجيل مصادر البيانات الخام...\n")

    existing = load_existing_registry()
    metadata_paths = get_metadata_files()

    for path in metadata_paths:
        metadata = parse_metadata(path)
        if not metadata:
            continue

        filename = metadata.get("filename")
        if filename in existing:
            logger.info(f"🟡 المصدر مسجل مسبقاً: {filename}")
            continue

        append_to_registry(metadata)

    logger.info(f"\n📘 تم تحديث سجل المصادر: {REGISTRY_PATH}")


if __name__ == "__main__":
    main()
