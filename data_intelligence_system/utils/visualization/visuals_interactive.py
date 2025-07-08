import pandas as pd
import plotly.express as px
from typing import Optional, List, Union

from data_intelligence_system.utils.visualization.visuals_helpers import _validate_columns


def interactive_scatter_matrix(df: pd.DataFrame, dimensions: List[str],
                               color: Optional[str] = None,
                               title: str = "Scatter Matrix",
                               save_path: Optional[str] = None) -> Union[px.scatter_matrix, None]:
    _validate_columns(df, dimensions)
    if color and color not in df.columns:
        raise ValueError(f"Color column '{color}' not found.")

    fig = px.scatter_matrix(df, dimensions=dimensions, color=color, title=title)
    fig.update_traces(diagonal_visible=False)

    if save_path:
        if not save_path.endswith('.html'):
            raise ValueError("Save path must end with .html for interactive Plotly graphs.")
        try:
            fig.write_html(save_path)
        except Exception as e:
            raise RuntimeError(f"Error saving HTML: {e}")
        return None
    else:
        fig.show()
        return fig