import os
from io import BytesIO
from typing import Optional
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import seaborn as sns
from data_intelligence_system.config.report_config import REPORT_CONFIG  # ✅ مضاف للتكامل مع الإعدادات العامة


def ensure_dir(path: str) -> None:
    """Ensure that a directory exists; create it if it does not."""
    if not os.path.exists(path):
        os.makedirs(path)


def save_dataframe_to_csv(df: pd.DataFrame, filename: str, output_dir: Optional[str] = None) -> None:
    """
    Save a DataFrame to a CSV file with UTF-8 BOM encoding to support Arabic.

    Args:
        df (pd.DataFrame): DataFrame to save.
        filename (str): Name of the file without extension.
        output_dir (Optional[str]): Directory where the file will be saved. Defaults to REPORT_CONFIG["output_dir"].

    Raises:
        ValueError: If DataFrame is empty.
        OSError: If file saving fails.
    """
    if df.empty:
        raise ValueError("Cannot save empty DataFrame to CSV.")
    output_dir = output_dir or REPORT_CONFIG["output_dir"]
    ensure_dir(output_dir)
    full_path = os.path.join(output_dir, f"{filename}.csv")
    try:
        df.to_csv(full_path, index=False, encoding='utf-8-sig')
    except OSError as e:
        raise OSError(f"Failed to save CSV file at {full_path}: {e}")


def save_dataframe_to_excel(df: pd.DataFrame, filename: str, output_dir: Optional[str] = None, sheet_name: str = "Sheet1") -> None:
    """
    Save a DataFrame to an Excel file with auto-adjusted column widths.

    Args:
        df (pd.DataFrame): DataFrame to save.
        filename (str): Name of the file without extension.
        output_dir (Optional[str]): Directory where the file will be saved. Defaults to REPORT_CONFIG["output_dir"].
        sheet_name (str): Name of the Excel sheet.

    Raises:
        ValueError: If DataFrame is empty.
        OSError: If file saving fails.
    """
    if df.empty:
        raise ValueError("Cannot save empty DataFrame to Excel.")
    output_dir = output_dir or REPORT_CONFIG["output_dir"]
    ensure_dir(output_dir)
    full_path = os.path.join(output_dir, f"{filename}.xlsx")
    try:
        with pd.ExcelWriter(full_path, engine='xlsxwriter') as writer:
            df.to_excel(writer, sheet_name=sheet_name, index=False)
            worksheet = writer.sheets[sheet_name]
            for idx, col in enumerate(df.columns):
                max_len = max(df[col].astype(str).map(len).max(), len(str(col))) + 2
                worksheet.set_column(idx, idx, max_len)
    except OSError as e:
        raise OSError(f"Failed to save Excel file at {full_path}: {e}")


def save_plot(fig: Figure, filename: str, output_dir: Optional[str] = None, dpi: int = 300) -> None:
    """
    Save a Matplotlib figure to a PNG file.

    Args:
        fig (Figure): Matplotlib figure to save.
        filename (str): Name of the file (extension optional).
        output_dir (Optional[str]): Directory where the file will be saved. Defaults to REPORT_CONFIG["output_dir"].
        dpi (int): Dots per inch (resolution).

    Raises:
        OSError: If saving fails.
    """
    output_dir = output_dir or REPORT_CONFIG["output_dir"]
    ensure_dir(output_dir)
    if not filename.lower().endswith('.png'):
        filename += '.png'
    full_path = os.path.join(output_dir, filename)
    try:
        fig.savefig(full_path, dpi=dpi, bbox_inches='tight')
    except OSError as e:
        raise OSError(f"Failed to save plot image at {full_path}: {e}")
    finally:
        plt.close(fig)


def df_to_html_table(df: pd.DataFrame, classes: Optional[str] = None, index: bool = False) -> str:
    """
    Convert a DataFrame to a styled HTML table.

    Args:
        df (pd.DataFrame): DataFrame to convert.
        classes (Optional[str]): CSS classes to add to the table.
        index (bool): Whether to include the index.

    Returns:
        str: HTML string of the table.
    """
    return df.to_html(classes=classes, index=index, border=0, justify='center')


def plot_correlation_heatmap(df_corr: pd.DataFrame,
                             filename: str,
                             output_dir: Optional[str] = None,
                             cmap: str = "coolwarm",
                             annot: bool = True,
                             title: str = "Correlation Heatmap") -> None:
    """
    Plot and save a correlation heatmap from a correlation matrix.

    Args:
        df_corr (pd.DataFrame): Correlation matrix DataFrame.
        filename (str): Name of the output PNG file.
        output_dir (Optional[str]): Directory where the file will be saved. Defaults to REPORT_CONFIG["output_dir"].
        cmap (str): Colormap for the heatmap.
        annot (bool): Whether to annotate cells with correlation values.
        title (str): Title of the heatmap.

    Raises:
        ValueError: If df_corr is empty.
        OSError: If saving the plot fails.
    """
    if df_corr.empty:
        raise ValueError("Correlation DataFrame is empty.")
    output_dir = output_dir or REPORT_CONFIG["output_dir"]
    ensure_dir(output_dir)
    fig, ax = plt.subplots(figsize=(12, 10))
    sns.heatmap(df_corr, annot=annot, fmt=".2f", cmap=cmap, square=True, cbar_kws={"shrink": 0.8}, ax=ax)
    ax.set_title(title)
    fig.tight_layout()
    save_plot(fig, filename, output_dir)


def save_image_bytes(fig: Figure, dpi: int = 300) -> bytes:
    """
    Convert a Matplotlib figure to PNG bytes.

    Args:
        fig (Figure): Matplotlib figure to convert.
        dpi (int): Dots per inch (resolution).

    Returns:
        bytes: PNG image bytes.
    """
    buf = BytesIO()
    fig.savefig(buf, format='png', dpi=dpi, bbox_inches='tight')
    plt.close(fig)
    buf.seek(0)
    return buf.getvalue()
