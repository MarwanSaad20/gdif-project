from pathlib import Path
import pandas as pd
import logging
from typing import List, Tuple, Union, Dict, Optional

# ✅ استيراد مطلق من جذر المشروع
from data_intelligence_system.etl.etl_utils import log_step, get_all_files, detect_file_type
from data_intelligence_system.utils.file_manager import extract_file_name, read_file
from data_intelligence_system.config.paths_config import RAW_DATA_PATHS, SUPPORTED_EXTENSIONS

try:
    from data_intelligence_system.data.raw.validate_structure import validate_file_structure  # type: ignore
except ImportError:
    validate_file_structure = None

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def is_valid_file(file_path: Path) -> bool:
    return file_path.suffix.lower() in SUPPORTED_EXTENSIONS and file_path.exists()


def try_validate(filepath: Path, validator: Optional[callable]):
    if validator and callable(validator):
        try:
            validator(str(filepath))
        except Exception as e:
            logger.warning(f"⚠️ فشل التحقق من بنية الملف {filepath.name}: {e}")


@log_step
def extract_all_data(validate: bool = True) -> List[Tuple[str, pd.DataFrame]]:
    datasets = []

    for data_path in RAW_DATA_PATHS:
        if not data_path.exists():
            logger.warning(f"⚠️ مجلد البيانات غير موجود: {data_path}")
            continue

        all_files = get_all_files(data_path, extensions=SUPPORTED_EXTENSIONS)
        if not all_files:
            logger.warning(f"⚠️ لا توجد ملفات في المجلد: {data_path}")
            continue

        for file_path in map(Path, all_files):
            if not is_valid_file(file_path):
                logger.info(f"⏩ تم تجاهل ملف غير مدعوم أو غير موجود: {file_path.name}")
                continue

            try:
                if validate:
                    try_validate(file_path, validate_file_structure)

                df = read_file(str(file_path))
                if not isinstance(df, pd.DataFrame):
                    logger.warning(f"⚠️ لم يتم استخراج DataFrame صالح من: {file_path.name}")
                    continue

                missing = int(df.isnull().sum().sum())
                logger.info(f"✅ {file_path.name} → شكل: {df.shape}, أعمدة: {len(df.columns)}, مفقودات: {missing}")
                datasets.append((file_path.name, df))

            except Exception as e:
                logger.exception(f"❌ خطأ أثناء استخراج {file_path.name}: {e}")

    return datasets


@log_step
def extract_file(source_path: Union[str, Path], validate: bool = True) -> Dict[str, pd.DataFrame]:
    file_path = Path(source_path)
    if not is_valid_file(file_path):
        raise FileNotFoundError(f"❌ الملف غير موجود أو غير مدعوم: {file_path}")

    try:
        if validate:
            try_validate(file_path, validate_file_structure)

        df = read_file(str(file_path))
        if not isinstance(df, pd.DataFrame):
            raise ValueError(f"⚠️ الملف {file_path.name} لم يتم تحويله إلى DataFrame بشكل صحيح")

        file_key = extract_file_name(str(file_path))
        logger.info(f"📄 تم استخراج ملف: {file_path.name} → {df.shape}")
        return {file_key: df}

    except Exception as e:
        logger.exception(f"❌ فشل استخراج الملف {file_path.name}: {e}")
        raise
