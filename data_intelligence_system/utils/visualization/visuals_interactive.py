import pandas as pd
import plotly.express as px
from typing import Optional, List, Union

from data_intelligence_system.utils.visualization.visuals_helpers import _validate_columns


def interactive_scatter_matrix(
    df: pd.DataFrame,
    dimensions: List[str],
    color: Optional[str] = None,
    title: str = "Scatter Matrix",
    save_path: Optional[str] = None
) -> Union[px.scatter_matrix, None]:
    """
    يرسم مصفوفة نقاط تفاعلية (scatter matrix) للأعمدة المحددة في DataFrame.

    Args:
        df (pd.DataFrame): مجموعة البيانات.
        dimensions (List[str]): قائمة الأعمدة التي سيتم رسمها.
        color (Optional[str]): اسم عمود للاستخدام كلون النقاط.
        title (str): عنوان الرسم البياني.
        save_path (Optional[str]): مسار لحفظ الرسم بصيغة HTML. إذا لم يُعطَ، يتم عرض الرسم.

    Raises:
        ValueError: إذا لم توجد الأعمدة المطلوبة أو عمود اللون في DataFrame.
        RuntimeError: إذا فشل حفظ الملف.
    """
    if df.empty:
        raise ValueError("DataFrame فارغ، لا يمكن إنشاء الرسم.")
    if not dimensions:
        raise ValueError("قائمة الأعمدة 'dimensions' فارغة، الرجاء تحديد أعمدة صحيحة.")

    _validate_columns(df, dimensions)

    if color and color not in df.columns:
        raise ValueError(f"عمود اللون '{color}' غير موجود في البيانات.")

    fig = px.scatter_matrix(df, dimensions=dimensions, color=color, title=title)
    fig.update_traces(diagonal_visible=False)

    if save_path:
        if not save_path.endswith('.html'):
            raise ValueError("مسار الحفظ يجب أن ينتهي بامتداد .html لرسومات Plotly التفاعلية.")
        try:
            fig.write_html(save_path)
        except Exception as e:
            raise RuntimeError(f"حدث خطأ أثناء حفظ ملف HTML: {e}")
        return None
    else:
        fig.show()
        return fig
