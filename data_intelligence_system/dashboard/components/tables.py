from dash import dash_table, html
from typing import List, Dict, Optional, Union

from data_intelligence_system.utils.logger import get_logger  # ✅ إضافة الاستيراد الموحد للّوجر

logger = get_logger("Tables")  # ✅ logger مخصص للملف

def create_data_table(
    id: str,
    columns: Union[List[str], List[Dict]],
    data: Optional[List[Dict]] = None,
    page_size: int = 10,
    style_table: Optional[Dict] = None,
    style_header: Optional[Dict] = None,
    style_cell: Optional[Dict] = None,
    style_data_conditional: Optional[List[Dict]] = None,
    tooltip_data: Optional[List[Dict]] = None,
    tooltip_duration: int = 1500,
    row_selectable: Optional[str] = None,
    selected_rows: Optional[List[int]] = None,
    editable: bool = False,
    page_action: str = "native",
    sort_mode: str = "single",
) -> dash_table.DataTable:
    if not columns or len(columns) == 0:
        raise ValueError("❌ يجب تمرير قائمة أعمدة تحتوي على عنصر واحد على الأقل.")

    if isinstance(columns[0], dict):
        for col in columns:
            if not isinstance(col, dict) or 'id' not in col or 'name' not in col:
                raise ValueError("❌ كل عنصر في الأعمدة يجب أن يحتوي على المفتاحين 'id' و 'name'.")
        column_defs = columns
    else:
        column_defs = [{"name": col, "id": col} for col in columns]

    if data is None:
        data = []
    elif not isinstance(data, list) or not all(isinstance(row, dict) for row in data):
        raise ValueError("❌ بيانات الجدول يجب أن تكون قائمة من القواميس.")

    default_style_table = {
        'overflowX': 'auto',
        'maxHeight': '600px',
        'overflowY': 'auto',
        'border': '1px solid #444',
    }

    default_style_header = {
        'backgroundColor': '#1a1a2e',
        'color': 'lightblue',
        'fontWeight': 'bold',
        'borderBottom': '1px solid #333',
        'textAlign': 'center',
        'whiteSpace': 'nowrap',
    }

    default_style_cell = {
        'backgroundColor': '#121212',
        'color': 'white',
        'textAlign': 'center',
        'padding': '8px',
        'border': 'none',
        'whiteSpace': 'normal',
        'height': 'auto',
    }

    default_style_data_conditional = [
        {
            'if': {'row_index': 'odd'},
            'backgroundColor': '#1c1c2a',
        }
    ]

    style_table = {**default_style_table, **(style_table or {})}
    style_header = {**default_style_header, **(style_header or {})}
    style_cell = {**default_style_cell, **(style_cell or {})}
    style_data_conditional = style_data_conditional or default_style_data_conditional

    return dash_table.DataTable(
        id=id,
        columns=column_defs,
        data=data,
        page_size=page_size,
        page_action=page_action,
        filter_action="native",
        sort_action="native",
        sort_mode=sort_mode,
        export_format="csv",
        export_headers="display",
        merge_duplicate_headers=True,
        fixed_rows={'headers': True},
        style_as_list_view=True,
        style_table=style_table,
        style_header=style_header,
        style_cell=style_cell,
        style_data_conditional=style_data_conditional,
        tooltip_data=tooltip_data,
        tooltip_duration=tooltip_duration,
        row_selectable=row_selectable,
        selected_rows=selected_rows or [],
        editable=editable,
    )


def reports_table():
    return html.Div(
        children=[
            html.H3("📊 قسم التقارير قيد التطوير", style={"color": "#888", "textAlign": "center", "marginTop": "50px"}),
            html.P("سيتم عرض تقارير مفصلة وتحليلات هنا قريبًا...", style={"textAlign": "center"})
        ],
        style={"padding": "30px"}
    )
