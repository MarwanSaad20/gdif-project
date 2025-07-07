import os
import requests
import json
from datetime import datetime
from typing import Optional, Dict
import logging
from dotenv import load_dotenv

# 📥 تحميل متغيرات البيئة
load_dotenv()

# 🔐 تحميل مفتاح FMP من .env
FMP_API_KEY = os.getenv("FMP_API_KEY")

# إعداد اللوجنغ
def setup_logger():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler()]
    )
    return logging.getLogger("FetchAPIData")

logger = setup_logger()

# 📁 إعداد المسارات
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # مجلد data
EXTERNAL_DATA_DIR = os.path.join(BASE_DIR, 'external', 'downloaded')
os.makedirs(EXTERNAL_DATA_DIR, exist_ok=True)

# 🌐 مصادر بيانات
DATA_SOURCES: Dict[str, Dict] = {
    "world_bank_gdp": {
        "url": "http://api.worldbank.org/v2/country/all/indicator/NY.GDP.MKTP.CD",
        "params": {"format": "json", "date": "2022"},
        "api_key": None
    },
    "open_meteo_weather": {
        "url": "https://api.open-meteo.com/v1/forecast",
        "params": {
            "latitude": 33.3,
            "longitude": 44.4,
            "hourly": "temperature_2m"
        },
        "api_key": None
    },
    "financial_markets": {
        "url": "https://financialmodelingprep.com/api/v3/stock/list",
        "params": {"apikey": FMP_API_KEY},
        "api_key": None
    }
}


def fetch_api_data(name: str, url: str, api_key: Optional[str], params: dict) -> Optional[dict]:
    headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}
    try:
        logger.info(f"🔗 الاتصال بالمصدر: {name} -> {url}")
        response = requests.get(url, headers=headers, params=params, timeout=20)
        response.raise_for_status()
        logger.info(f"✅ تم استلام البيانات من {name}")
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ خطأ عند الاتصال بـ {name}: {e}")
        return None


def save_data_to_file(data: dict, prefix: str) -> str:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{prefix}_{timestamp}.json"
    path = os.path.join(EXTERNAL_DATA_DIR, filename)
    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logger.info(f"💾 تم حفظ البيانات: {path}")
        return path
    except Exception as e:
        logger.error(f"❌ فشل حفظ الملف {filename}: {e}")
        return ""


def main():
    logger.info("🚀 بدء جلب البيانات من جميع المصادر...")
    for source_name, source_info in DATA_SOURCES.items():
        if "apikey" in source_info.get("params", {}) and not FMP_API_KEY:
            logger.warning(f"⚠️ لم يتم ضبط FMP_API_KEY في البيئة - سيتم تخطي {source_name}")
            continue

        data = fetch_api_data(
            name=source_name,
            url=source_info["url"],
            api_key=source_info.get("api_key"),
            params=source_info.get("params", {})
        )
        if data:
            save_data_to_file(data, prefix=source_name)
        else:
            logger.warning(f"⚠️ لم يتم استلام بيانات من المصدر: {source_name}")


if __name__ == "__main__":
    main()
