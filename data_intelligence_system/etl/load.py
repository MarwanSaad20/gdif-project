from pathlib import Path
from datetime import datetime
import logging
from typing import List, Tuple, Optional, Union
import pandas as pd
import os

try:
    from data_intelligence_system.data.raw.archive_raw_file import archive_file  # type: ignore
except ImportError:
    archive_file = None

try:
    from data_intelligence_system.data.processed.validate_clean_data import validate
except ImportError:
    validate = None

logger = logging.getLogger(__name__)


def create_output_dir(base_path: Path) -> Path:
    try:
        if not base_path.exists():
            base_path.mkdir(parents=True, exist_ok=True)
            logger.info(f"📁 تم إنشاء مجلد الإخراج: {base_path}")
    except Exception as e:
        logger.error(f"❌ خطأ أثناء إنشاء مجلد الإخراج {base_path}: {e}")
        raise
    return base_path


def generate_timestamped_filename(base_name: str, ext: str) -> str:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{base_name}_{timestamp}.{ext}"


def archive_old_files(output_dir: Path, base_name: str, ext: str, keep_latest: int = 3):
    try:
        files = sorted(
            [f for f in output_dir.glob(f"{base_name}_*.{ext}")],
            key=lambda f: f.stat().st_mtime,
            reverse=True
        )
        old_files = files[keep_latest:]
        for file_path in old_files:
            try:
                file_path.unlink()
                logger.info(f"🗑️ تم حذف الملف القديم: {file_path.name}")
            except Exception as e:
                logger.error(f"❌ خطأ أثناء حذف الملف {file_path.name}: {e}")
    except Exception as e:
        logger.error(f"❌ خطأ أثناء أرشفة الملفات القديمة في {output_dir}: {e}")


def save_dataframe(
    df: pd.DataFrame,
    output_dir: Union[str, Path],
    base_name: str,
    file_format: str = 'csv',
    archive: bool = True
) -> Optional[Path]:
    if isinstance(output_dir, str):
        output_dir = Path(output_dir)

    if df.empty or df.shape[1] == 0:
        logger.warning(f"⚠️ DataFrame فارغ أو لا يحتوي على أعمدة: {base_name}")
        return None

    try:
        output_dir = create_output_dir(output_dir)
    except Exception:
        return None

    ext = file_format.lower()
    filename = generate_timestamped_filename(base_name, ext)
    file_path = output_dir / filename

    try:
        logger.info(f"💾 بدء حفظ {base_name} بصيغة {ext}")
        if ext == 'csv':
            df.to_csv(file_path, index=False)
        elif ext == 'xlsx':
            df.to_excel(file_path, index=False)
        elif ext == 'parquet':
            try:
                df.to_parquet(file_path, index=False)
            except ImportError as ie:
                logger.error(f"❌ مكتبة pyarrow أو fastparquet غير مثبتة، لا يمكن حفظ بصيغة parquet: {ie}")
                return None
        else:
            logger.error(f"❌ صيغة الملف غير مدعومة: {ext}")
            return None

        logger.info(f"✅ تم حفظ الملف: {file_path}")

        if validate:
            try:
                validate(df)
            except Exception as e:
                logger.warning(f"⚠️ فشل التحقق من جودة البيانات بعد الحفظ: {e}")

        if archive:
            archive_old_files(output_dir, base_name, ext)

            potential_raw_dirs = [
                output_dir.parent / 'raw',
                output_dir.parent / 'external' / 'downloaded'
            ]
            for raw_dir in potential_raw_dirs:
                raw_file = raw_dir / f"{base_name.split('_cleaned')[0]}"
                if archive_file and raw_file.exists():
                    try:
                        archive_file(str(raw_file))
                        break
                    except Exception as e:
                        logger.warning(f"⚠️ لم يتم أرشفة الملف الأصلي {raw_file.name}: {e}")

        return file_path

    except Exception as e:
        logger.error(f"❌ خطأ أثناء حفظ الملف {file_path}: {e}", exc_info=True)
        return None


def save_multiple_datasets(
    datasets: List[Tuple[str, pd.DataFrame]],
    output_dir: Union[str, Path],
    file_format: str = 'csv',
    archive: bool = True
) -> bool:
    if not datasets:
        logger.error("🚫 لا توجد بيانات لحفظها.")
        return False

    success = True
    for name, df in datasets:
        logger.info(f"📦 حفظ مجموعة البيانات: {name} | الصفوف: {df.shape[0]}, الأعمدة: {df.shape[1]}")
        base_name = f"{name}_cleaned"
        path = save_dataframe(df, output_dir, base_name, file_format, archive)
        if path is None:
            logger.error(f"❌ فشل في حفظ: {name}")
            success = False
        else:
            logger.info(f"📁 تم حفظ: {name} إلى {path}")
    return success


def save_transformed_data(
    df: pd.DataFrame,
    output_dir: Union[str, Path],
    base_name: str = "processed_sample",
    file_format: str = "csv"
) -> Optional[Path]:
    return save_dataframe(df, output_dir, base_name, file_format, archive=True)


def save_uploaded_data(df: pd.DataFrame, filename: str = "uploaded.csv") -> str:
    """
    دالة لحفظ بيانات مرفوعة من المستخدم بصيغة CSV في مجلد processed
    - تستخدم مسار ثابت: data/processed
    """
    base_dir = Path(__file__).resolve().parents[1]
    processed_dir = base_dir / "data" / "processed"
    path = processed_dir / filename
    os.makedirs(processed_dir, exist_ok=True)

    try:
        df.to_csv(path, index=False, encoding='utf-8')
        logger.info(f"✅ تم حفظ البيانات بنجاح في {path}")
        return str(path)
    except Exception as e:
        logger.error(f"❌ فشل حفظ البيانات: {e}", exc_info=True)
        raise
