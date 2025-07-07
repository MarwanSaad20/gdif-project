from dash import html
from typing import Optional, Union, List

from data_intelligence_system.utils.logger import get_logger  # ✅ إضافة اللوجر المخصص

logger = get_logger("Indicators")  # جاهز للاستخدام عند الحاجة

def create_kpi_card(
    id: str,
    title: str,
    value: Union[str, int, float] = "—",
    icon: Optional[str] = None,
    tooltip: str = "",
    color: str = "#00cc96",
    style: Optional[dict] = None,
    title_style: Optional[dict] = None,
    value_style: Optional[dict] = None,
    class_name: Optional[Union[str, List[str]]] = None
) -> html.Div:
    base_card_style = {
        "backgroundColor": "#1a1a1a",
        "color": "white",
        "padding": "16px",
        "borderRadius": "12px",
        "boxShadow": "0 6px 12px rgba(0, 0, 0, 0.4)",
        "minWidth": "150px",
        "maxWidth": "250px",
        "boxSizing": "border-box",
        "textAlign": "center",
        "flex": "1 1 150px",
        "transition": "all 0.3s ease-in-out",
        "cursor": "default",
        "userSelect": "none"
    }

    base_title_style = {
        "fontSize": "1.1rem",
        "marginBottom": "6px",
        "color": "#9ecbff",
        "fontWeight": "600",
        "whiteSpace": "nowrap",
        "overflow": "hidden",
        "textOverflow": "ellipsis",
        "userSelect": "none"
    }

    base_value_style = {
        "fontSize": "2.3rem",
        "fontWeight": "bold",
        "color": color,
        "whiteSpace": "nowrap",
        "overflow": "hidden",
        "textOverflow": "ellipsis",
        "userSelect": "text"
    }

    final_card_style = {**base_card_style, **(style or {})}
    final_title_style = {**base_title_style, **(title_style or {})}
    final_value_style = {**base_value_style, **(value_style or {})}
    final_class = " ".join(class_name) if isinstance(class_name, list) else (class_name or "")

    children = []

    if icon:
        children.append(html.I(className=icon, style={
            "fontSize": "1.8rem",
            "marginBottom": "6px",
            "display": "block",
            "aria-hidden": "true"
        }))

    children.append(html.Div(title, style=final_title_style))

    children.append(
        html.Div(
            str(value),
            id=f"{id}-value",
            style=final_value_style,
            title=tooltip,
            role="text",
            **({"aria-label": tooltip} if tooltip else {})
        )
    )

    return html.Div(children=children, id=id, style=final_card_style, className=final_class)


def create_kpi_container(kpi_cards: List[html.Div]) -> html.Div:
    container_style = {
        "display": "flex",
        "flexWrap": "wrap",
        "gap": "15px",
        "justifyContent": "center",
        "padding": "15px",
        "marginTop": "20px",
        "overflowX": "auto",
        "maxWidth": "100%",
        "boxSizing": "border-box",
        "-webkit-overflow-scrolling": "touch"
    }

    return html.Div(children=kpi_cards, style=container_style)


def dashboard_kpis_default() -> html.Div:
    cards = [
        create_kpi_card(
            id="kpi-users",
            title="عدد المستخدمين",
            value="—",
            icon="fa fa-users",
            color="#00cc96",
            tooltip="عدد المستخدمين المسجلين"
        ),
        create_kpi_card(
            id="kpi-sales",
            title="إجمالي المبيعات",
            value="—",
            icon="fa fa-dollar-sign",
            color="#ff6347",
            tooltip="إجمالي المبيعات بالدولار"
        ),
        create_kpi_card(
            id="kpi-performance",
            title="نسبة الأداء",
            value="—",
            icon="fa fa-chart-line",
            color="#ffa500",
            tooltip="مؤشر الأداء الإجمالي"
        )
    ]
    return create_kpi_container(cards)
