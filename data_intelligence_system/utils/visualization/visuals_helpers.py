import pandas as pd
import matplotlib.pyplot as plt
from typing import Optional, List
from data_intelligence_system.utils.logger import get_logger

logger = get_logger("Visualization")


def _handle_save_or_show(fig: plt.Figure, save_path: Optional[str]) -> None:
    """
    يعرض الشكل أو يحفظه حسب وجود مسار الحفظ.
    يغلق الشكل بعد العملية لمنع استهلاك الذاكرة.
    """
    try:
        if save_path:
            fig.savefig(save_path)
            logger.info(f"Figure saved to {save_path}")
            plt.close(fig)
        else:
            plt.show()
    except Exception as e:
        logger.exception(f"Error displaying or saving figure: {e}")
        plt.close(fig)
        raise RuntimeError(f"Failed to save/show figure: {e}")


def _validate_columns(df: pd.DataFrame, columns: List[str], dropna: bool = True) -> pd.DataFrame:
    """
    يتحقق من وجود الأعمدة المطلوبة في DataFrame.
    يعيد نسخة مفلترة تحتوي فقط على الأعمدة المطلوبة.
    يزيل الصفوف التي تحتوي على قيم مفقودة إذا dropna=True.
    
    :param df: DataFrame الإدخال.
    :param columns: قائمة الأعمدة المطلوبة.
    :param dropna: هل يتم حذف الصفوف التي تحتوي على NaN (افتراضي True).
    :return: DataFrame مفلتر.
    :raises ValueError: إذا كانت الأعمدة مفقودة أو DataFrame فارغ.
    """
    missing = [col for col in columns if col not in df.columns]
    if missing:
        raise ValueError(f"Missing columns: {missing}")
    if df.empty:
        raise ValueError("Input DataFrame is empty.")

    filtered_df = df[columns]
    if dropna:
        filtered_df = filtered_df.dropna()
    return filtered_df
