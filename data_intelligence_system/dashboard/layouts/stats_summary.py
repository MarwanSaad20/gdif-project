from dash import html
import dash_bootstrap_components as dbc

# 🎨 ألوان ثيم المشروع
BACKGROUND_COLOR = "#0A0F1A"
TEXT_COLOR = "#FFFFFF"
PRIMARY_COLOR = "#1E90FF"

BORDER_COLOR = "rgba(30, 144, 255, 0.2)"

PRE_STYLE = {
    "whiteSpace": "pre-wrap",
    "fontFamily": "'Courier New', Courier, monospace",
    "fontSize": "0.9rem",
    "color": TEXT_COLOR,
    "backgroundColor": "rgba(10, 15, 26, 0.8)",
    "padding": "1rem",
    "borderRadius": "5px",
    "overflowX": "auto",
    "overflowY": "auto",
    "maxHeight": "300px",
    "minHeight": "120px",
    "border": f"1px solid {BORDER_COLOR}",
    "direction": "ltr",
    "tabindex": 0  # HTML attribute should be lowercase
}


def stats_summary_card():
    """
    إنشاء بطاقة ملخص إحصائي للبيانات (مثل describe()).
    
    هذه البطاقة تعرض ملخصًا نصيًا يتم تحديثه ديناميكيًا عبر callback
    يظهر في عنصر <pre> معرف بـ id='stats-summary-pre'.
    
    Returns:
        dbc.Card: بطاقة Bootstrap تعرض الملخص الإحصائي.
    """
    return dbc.Card(
        [
            dbc.CardHeader(
                html.H5(
                    "📊 الملخص الإحصائي للبيانات",
                    className="mb-0",
                    style={"color": PRIMARY_COLOR}
                )
            ),
            dbc.CardBody(
                [
                    html.P(
                        "يُعرض أدناه ناتج الإحصائيات الوصفية (مثل: count, mean, std...) لكل عمود رقمي.",
                        className="text-muted",
                        style={"fontSize": "0.85rem"}
                    ),
                    html.Pre(
                        id="stats-summary-pre",
                        children=(
                            "⚠️ لا توجد بيانات حالياً.\n\n"
                            "يرجى رفع بيانات لاستخراج الملخص الإحصائي."
                        ),
                        style=PRE_STYLE,
                    )
                ]
            )
        ],
        className="shadow-sm rounded w-100",
        style={
            "backgroundColor": BACKGROUND_COLOR,
            "border": "none",
            "boxShadow": "0 4px 12px rgba(30, 144, 255, 0.15)",
        }
    )
