from pathlib import Path
from typing import Optional
import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output

from data_intelligence_system.utils.logger import get_logger
from data_intelligence_system.config.paths_config import PROCESSED_DATA_DIR

logger = get_logger("dashboard.service")

DEFAULT_FILE = "clean_data.csv"


def load_processed_data(filename: Optional[str] = DEFAULT_FILE) -> pd.DataFrame:
    """
    Load processed data from CSV.
    Raises FileNotFoundError if file does not exist.
    """
    path = PROCESSED_DATA_DIR / filename
    if not path.exists():
        logger.error(f"❌ ملف البيانات غير موجود: {path}")
        raise FileNotFoundError(f"الملف غير موجود: {path}")
    try:
        df = pd.read_csv(path, encoding="utf-8")
        logger.info(f"✅ تم تحميل البيانات: {filename} (عدد الصفوف: {len(df)})")
        return df
    except Exception as e:
        logger.error(f"❌ فشل في تحميل الملف {filename}: {e}", exc_info=True)
        raise


def start_dashboard():
    """
    Start interactive dashboard with numeric scatter plot and histogram.
    """
    df = load_processed_data()

    if df.empty:
        logger.error("❌ البيانات فارغة، لا يمكن إطلاق لوحة التحكم.")
        raise ValueError("البيانات فارغة.")

    numeric_cols = df.select_dtypes(include='number').columns.tolist()
    cat_cols = df.select_dtypes(include='object').columns.tolist()

    if len(numeric_cols) < 2:
        logger.error("❌ عدد الأعمدة الرقمية أقل من 2، لا يمكن إنشاء المخططات.")
        raise ValueError("عدد الأعمدة الرقمية أقل من 2")

    app = Dash(__name__)
    app.title = "📊 Data Intelligence Dashboard"

    app.layout = html.Div([
        html.H1("لوحة التحكم الذكية", style={"textAlign": "center"}),

        html.Div([
            html.Label("📌 اختر المتغير على المحور X:"),
            dcc.Dropdown(numeric_cols, id='x-axis', value=numeric_cols[0]),
        ], style={'width': '48%', 'display': 'inline-block'}),

        html.Div([
            html.Label("📌 اختر المتغير على المحور Y:"),
            dcc.Dropdown(numeric_cols, id='y-axis', value=numeric_cols[1]),
        ], style={'width': '48%', 'display': 'inline-block'}),

        html.Div([
            html.Label("🎨 تلوين حسب المتغير (اختياري):"),
            dcc.Dropdown(cat_cols, id='color-by', value=None, placeholder="اختياري"),
        ], style={'width': '48%', 'marginTop': '10px'}),

        dcc.Graph(id='scatter-plot'),

        html.H2("📈 توزيع المتغيرات العددية"),
        dcc.Dropdown(numeric_cols, id='dist-column', value=numeric_cols[0]),
        dcc.Graph(id='histogram')
    ])

    @app.callback(
        Output('scatter-plot', 'figure'),
        [Input('x-axis', 'value'),
         Input('y-axis', 'value'),
         Input('color-by', 'value')]
    )
    def update_scatter(x_col: str, y_col: str, color_col: Optional[str]):
        """
        Update scatter plot based on selected columns.
        """
        try:
            logger.info(f"⏳ تحديث scatter: {x_col} مقابل {y_col}, color={color_col}")
            if x_col not in df.columns or y_col not in df.columns:
                logger.warning(f"⚠️ الأعمدة غير موجودة: {x_col}, {y_col}")
                return px.scatter(title="⚠️ الأعمدة المختارة غير موجودة")
            return px.scatter(df, x=x_col, y=y_col, color=color_col, title=f"{y_col} مقابل {x_col}")
        except Exception as e:
            logger.error(f"❌ خطأ في تحديث scatter: {e}", exc_info=True)
            return px.scatter(title="⚠️ خطأ في إنشاء الرسم البياني")

    @app.callback(
        Output('histogram', 'figure'),
        Input('dist-column', 'value')
    )
    def update_histogram(col: str):
        """
        Update histogram for selected column.
        """
        try:
            logger.info(f"⏳ تحديث histogram للعمود: {col}")
            if col not in df.columns:
                logger.warning(f"⚠️ العمود غير موجود: {col}")
                return px.histogram(title="⚠️ العمود غير موجود")
            return px.histogram(df, x=col, nbins=30, title=f"توزيع {col}", color_discrete_sequence=['teal'])
        except Exception as e:
            logger.error(f"❌ خطأ في تحديث histogram: {e}", exc_info=True)
            return px.histogram(title="⚠️ خطأ في إنشاء الرسم البياني")

    app.run(debug=True, port=8050)


if __name__ == "__main__":
    start_dashboard()
