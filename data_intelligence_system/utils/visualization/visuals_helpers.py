
import pandas as pd
import matplotlib.pyplot as plt
from typing import Optional, List

from data_intelligence_system.utils.logger import get_logger

logger = get_logger("Visualization")

def _handle_save_or_show(fig: plt.Figure, save_path: Optional[str]) -> None:
    try:
        if save_path:
            fig.savefig(save_path)
            plt.close(fig)
        else:
            plt.show()
    except Exception as e:
        logger.exception(f"Error displaying or saving figure: {e}")
        plt.close(fig)
        raise RuntimeError(f"Failed to save/show figure: {e}")

def _validate_columns(df: pd.DataFrame, columns: List[str]) -> pd.DataFrame:
    missing = [col for col in columns if col not in df.columns]
    if missing:
        raise ValueError(f"Missing columns: {missing}")
    if df.empty:
        raise ValueError("Input DataFrame is empty.")
    return df[columns].dropna()
