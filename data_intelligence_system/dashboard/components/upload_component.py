import io
import base64
from datetime import datetime
from pathlib import Path

import pandas as pd
from dash import dcc, html
from werkzeug.utils import secure_filename

from data_intelligence_system.config.paths_config import RAW_DATA_DIR
from data_intelligence_system.utils.logger import get_logger  # ✅ استيراد موحّد للّوجر

logger = get_logger("UploadComponent")  # ✅ لوجر مخصص لهذا الملف

if not isinstance(RAW_DATA_DIR, Path):
    raise TypeError(f"❌ RAW_DATA_DIR يجب أن يكون كائن Path، لكنه من النوع: {type(RAW_DATA_DIR)}")

logger.info(f"📂 RAW_DATA_DIR مضبوط بنجاح: {RAW_DATA_DIR}")


def upload_csv_component(component_id="upload-data", max_file_size_mb=5):
    return html.Div([
        html.H4("📁 تحميل ملف البيانات (CSV)", style={
            "marginBottom": "10px",
            "fontWeight": "600",
            "fontSize": "1.25rem",
            "color": "#60aaff"
        }),
        dcc.Upload(
            id=component_id,
            children=html.Div([
                html.Span("📤 اسحب الملف هنا أو "),
                html.A("اختر ملف من جهازك", style={
                    "color": "#1E90FF",
                    "textDecoration": "underline",
                    "cursor": "pointer"
                })
            ]),
            style={
                'width': '100%',
                'height': '120px',
                'lineHeight': '120px',
                'borderWidth': '2px',
                'borderStyle': 'dashed',
                'borderRadius': '15px',
                'textAlign': 'center',
                'marginBottom': '10px',
                'backgroundColor': '#121212',
                'color': '#e0e0e0',
                'borderColor': '#1E90FF',
                'cursor': 'pointer',
                'transition': 'border-color 0.3s ease',
            },
            multiple=False,
            accept='.csv,text/csv'
        ),
        html.Div(
            f"✅ الصيغة المدعومة: CSV فقط — الحد الأقصى للحجم: {max_file_size_mb}MB",
            style={
                "fontSize": "0.9rem",
                "color": "#ffaa00",
                "marginTop": "8px"
            }
        )
    ])


def is_csv_content_valid(decoded_bytes):
    try:
        sample = io.StringIO(decoded_bytes.decode('utf-8', errors='ignore'))
        pd.read_csv(sample, nrows=5)
        return True
    except Exception:
        return False


def save_uploaded_file(contents, filename, max_file_size_mb=5):
    if not filename.lower().endswith(".csv"):
        raise ValueError("❌ الملف ليس من نوع CSV.")

    try:
        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)
    except Exception:
        logger.exception("❌ فشل في فك ترميز Base64")
        raise ValueError("❌ تعذر قراءة الملف.")

    if content_type not in (
        "data:text/csv;base64",
        "data:application/vnd.ms-excel;base64",
        "data:application/csv;base64"
    ):
        raise ValueError(f"❌ نوع الملف غير مدعوم: {content_type}")

    file_size_mb = len(decoded) / (1024 * 1024)
    if file_size_mb > max_file_size_mb:
        raise ValueError(f"❌ حجم الملف يتجاوز {max_file_size_mb}MB.")

    if not is_csv_content_valid(decoded):
        raise ValueError("❌ محتوى الملف لا يتوافق مع صيغة CSV.")

    secure_name = secure_filename(filename)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    final_name = f"{timestamp}_{secure_name}"

    try:
        RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        logger.exception(f"❌ فشل في إنشاء المجلد: {RAW_DATA_DIR}")
        raise ValueError("❌ تعذر إنشاء مجلد الحفظ.")

    save_path = RAW_DATA_DIR / final_name

    with open(save_path, 'wb') as f:
        f.write(decoded)

    logger.info(f"✅ تم حفظ الملف في: {save_path}")
    return str(save_path)


def upload_section():
    return upload_csv_component(component_id="upload-data")
