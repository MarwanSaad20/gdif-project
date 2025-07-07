from dash import dcc
import datetime

from data_intelligence_system.utils.logger import get_logger  # ✅ استيراد اللوجر الموحد

logger = get_logger("Filters")  # ✅ يمكن استخدامه لاحقًا لتسجيل تحذيرات أو معلومات


def create_dropdown(id, options, value=None, multi=False, placeholder="اختر قيمة", style=None, disabled=False):
    if options and isinstance(options[0], str):
        options = [{"label": opt, "value": opt} for opt in options]

    if multi:
        if value is None:
            value = []
        elif not isinstance(value, (list, tuple)):
            value = [value]
    else:
        if isinstance(value, (list, tuple)):
            value = value[0] if value else None

    dropdown_style = {
        "color": "white",
        "backgroundColor": "#121212",
        "border": "1px solid #444",
        "borderRadius": "6px",
        "fontSize": "14px",
        "width": "100%",
        "direction": "rtl",
        "maxHeight": "200px",
        "overflowY": "auto",
        "zIndex": 1050,
    }
    if style:
        dropdown_style.update(style)

    return dcc.Dropdown(
        id=id,
        options=options or [],
        value=value,
        multi=multi,
        placeholder=placeholder,
        style=dropdown_style,
        clearable=True,
        searchable=True,
        disabled=disabled,
    )


def create_slider(id, min_val, max_val, step=1, value=None, marks=None, tooltip=True,
                  included=True, vertical=False):
    if min_val > max_val:
        raise ValueError("min_val يجب أن يكون أقل أو يساوي max_val.")

    if value is None:
        value = min_val

    if marks is None:
        step_marks = max(1, int((max_val - min_val) / 10))
        marks = {i: str(i) for i in range(min_val, max_val + 1, step_marks)}

    return dcc.Slider(
        id=id,
        min=min_val,
        max=max_val,
        step=step,
        value=value,
        marks=marks,
        tooltip={"placement": "bottom", "always_visible": tooltip},
        updatemode='mouseup',
        included=included,
        vertical=vertical,
    )


def create_date_picker(
    id,
    start_date=None,
    end_date=None,
    min_date=None,
    max_date=None,
    style=None,
    clearable=True,
    display_format="YYYY-MM-DD"
):
    def to_str(d):
        if d is None:
            return None
        if isinstance(d, datetime.date):
            return d.strftime('%Y-%m-%d')
        return d

    start_date = to_str(start_date)
    end_date = to_str(end_date)
    min_date = to_str(min_date)
    max_date = to_str(max_date)

    default_style = {
        "backgroundColor": "#1a1a1a",
        "border": "1px solid #444",
        "color": "#FFFFFF",
        "padding": "6px",
        "borderRadius": "6px",
        "width": "100%",
        "direction": "rtl",
    }
    final_style = default_style.copy()
    if style:
        final_style.update(style)

    return dcc.DatePickerRange(
        id=id,
        start_date=start_date,
        end_date=end_date,
        min_date_allowed=min_date,
        max_date_allowed=max_date,
        display_format=display_format,
        minimum_nights=0,
        start_date_placeholder_text="من تاريخ",
        end_date_placeholder_text="إلى تاريخ",
        clearable=clearable,
        style=final_style,
    )


def settings_panel():
    return None
