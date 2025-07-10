import plotly.graph_objects as go
import numpy as np
from typing import List, Optional, Dict, Any

from data_intelligence_system.utils.logger import get_logger

logger = get_logger("Charts")


def create_empty_figure(message: str = "⚠️ لا توجد بيانات كافية للرسم",
                        height: int = 400, width: Optional[int] = None) -> go.Figure:
    """
    إنشاء شكل فارغ مع رسالة تنبيه.
    """
    fig = go.Figure()
    fig.update_layout(
        height=height,
        width=width,
        font=dict(color='white', size=16),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        annotations=[dict(
            text=message,
            showarrow=False,
            font=dict(size=20, color='red'),
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            align="center"
        )]
    )
    return fig


def create_common_layout(title: str, height: int = 400, width: Optional[int] = None,
                         margin: Optional[Dict[str, int]] = None,
                         xaxis_style: Optional[Dict[str, Any]] = None,
                         yaxis_style: Optional[Dict[str, Any]] = None,
                         extra_layout: Optional[Dict[str, Any]] = None) -> go.Layout:
    """
    إنشاء إعداد تخطيط مشترك لكل الرسومات.
    """
    default_margin = dict(l=50, r=20, t=50, b=40)
    default_xaxis = dict(showgrid=False, zeroline=False, color='lightblue')
    default_yaxis = dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)', zeroline=False, color='lightblue')

    layout_dict = dict(
        title=title,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white', family="Arial, sans-serif"),
        height=height,
        width=width,
        margin=margin or default_margin,
        xaxis=xaxis_style or default_xaxis,
        yaxis=yaxis_style or default_yaxis,
        hovermode='x unified',
        legend=dict(font=dict(color='white')),
    )

    if extra_layout:
        layout_dict.update(extra_layout)

    return go.Layout(**layout_dict)


def create_line_chart(x_data: List[Any], y_data: List[Optional[float]], title: str = "",
                      colors: Optional[Dict[str, str]] = None,
                      height: int = 400, width: Optional[int] = None, **kwargs) -> go.Figure:
    """
    إنشاء رسم خطي.
    """
    if not x_data or not y_data or len(x_data) != len(y_data):
        return create_empty_figure(message="⚠️ لا توجد بيانات كافية للرسم الخطي", height=height, width=width)

    if colors and not isinstance(colors, dict):
        raise ValueError("colors يجب أن يكون قاموسًا")

    x_clean = [str(x) if x is not None else '' for x in x_data]
    y_clean = [float(y) if y is not None else np.nan for y in y_data]
    line_color = colors.get('line', '#1f77b4') if colors else '#1f77b4'

    layout = create_common_layout(title, height, width, **kwargs)

    return go.Figure(data=[go.Scatter(
        x=x_clean,
        y=y_clean,
        mode='lines+markers',
        line=dict(color=line_color),
        hovertemplate='%{x}: %{y}<extra></extra>'
    )], layout=layout)


def create_bar_chart(categories: List[str], values: List[Optional[float]], title: str = "",
                     colors: Optional[Dict[str, str]] = None,
                     height: int = 400, width: Optional[int] = None, **kwargs) -> go.Figure:
    """
    إنشاء رسم عمودي.
    """
    if not categories or not values or len(categories) != len(values):
        return create_empty_figure(message="⚠️ لا توجد بيانات كافية للرسم العمودي", height=height, width=width)

    if colors and not isinstance(colors, dict):
        raise ValueError("colors يجب أن يكون قاموسًا")

    bar_color = colors.get('bar', '#007ACC') if colors else '#007ACC'
    layout = create_common_layout(title, height, width, **kwargs)

    return go.Figure(data=[go.Bar(
        x=categories,
        y=values,
        marker_color=bar_color,
        hovertemplate='%{x}: %{y}<extra></extra>'
    )], layout=layout)


def create_pie_chart(labels: List[str], values: List[Optional[float]], title: str = "",
                     colors: Optional[Dict[str, Any]] = None,
                     height: int = 400, width: Optional[int] = None, **kwargs) -> go.Figure:
    """
    إنشاء رسم دائري.
    """
    if not labels or not values or len(labels) != len(values):
        return create_empty_figure(message="⚠️ لا توجد بيانات كافية للرسم الدائري", height=height, width=width)

    if colors and not isinstance(colors, dict):
        raise ValueError("colors يجب أن يكون قاموسًا")

    default_pie_colors = [
        '#636efa', '#EF553B', '#00cc96', '#ab63fa',
        '#ffa15a', '#19d3f3', '#FF6692', '#B6E880',
        '#FF97FF', '#FECB52'
    ]
    pie_colors = colors.get('pie_colors', default_pie_colors) if colors else default_pie_colors

    extra_layout = dict(margin=dict(l=20, r=20, t=50, b=20))
    layout = create_common_layout(title, height, width, extra_layout=extra_layout, **kwargs)

    return go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        marker=dict(colors=pie_colors),
        hole=0.3,
        hoverinfo='label+percent+value',
        hovertemplate='%{label}: %{percent} (%{value})<extra></extra>'
    )], layout=layout)
