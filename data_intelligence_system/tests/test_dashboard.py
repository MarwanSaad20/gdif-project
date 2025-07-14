import os
import time
import pytest
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from socket import socket, AF_INET, SOCK_STREAM

# استيراد كل مكونات الواجهة من جذر المشروع
from data_intelligence_system.dashboard import app
from data_intelligence_system.dashboard.callbacks import (
    kpi_callbacks,
    layout_callbacks,
    filters_callbacks,
    charts_callbacks,
    export_callbacks
)
from data_intelligence_system.dashboard.layouts import (
    main_layout,
    kpi_cards,
    charts_placeholders,
    stats_summary,
    theme
)
from data_intelligence_system.dashboard.components import (
    upload_component,
    charts,
    tables,
    filters,
    indicators
)

CHROMEDRIVER_PATH = os.getenv(
    "CHROMEDRIVER_PATH",
    r"C:\Users\PC\.wdm\drivers\chromedriver\win64\138.0.7204.49\chromedriver-win32\chromedriver.exe"
)

@pytest.fixture(scope="session")
def browser_options():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--window-size=1920,1080")
    return options

def wait_for_port(host: str, port: int, timeout=15):
    """انتظار حتى يصبح السيرفر جاهز (البورت مفتوح للاستماع)."""
    start_time = time.time()
    while True:
        try:
            with socket(AF_INET, SOCK_STREAM) as sock:
                result = sock.connect_ex((host, port))
                if result == 0:
                    return True
        except Exception:
            pass
        if time.time() - start_time > timeout:
            raise TimeoutError(f"لم يفتح المنفذ {port} على {host} خلال {timeout} ثانية.")
        time.sleep(0.5)

@pytest.fixture(scope="session")
def dash_app():
    # ارجاع app Dash
    return app.app

@pytest.fixture(scope="session")
def dash_driver(browser_options, dash_app):
    from threading import Thread

    service = ChromeService(executable_path=CHROMEDRIVER_PATH)
    driver = webdriver.Chrome(service=service, options=browser_options)

    # تشغيل سيرفر Dash داخل Thread كـ daemon
    def run_dash():
        dash_app.run(debug=False, use_reloader=False, port=8050, threaded=True)

    thread = Thread(target=run_dash, daemon=True)
    thread.start()

    # انتظر حتى يفتح السيرفر المنفذ 8050 (جاهزية)
    wait_for_port("127.0.0.1", 8050, timeout=20)

    yield driver

    driver.quit()

class TestDashboardApp:
    BASE_URL = "http://localhost:8050"

    def wait_for_element(self, driver, by, identifier, timeout=10):
        return WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((by, identifier))
        )

    def test_app_renders(self, dash_driver):
        dash_driver.get(self.BASE_URL)
        WebDriverWait(dash_driver, 10).until(EC.title_contains("نظام تحليل البيانات العام"))
        assert "نظام تحليل البيانات العام" in dash_driver.title

        expected_ids = [
            "app-title",
            "refresh-button",
            "data-selector",
            "output-area",
            "status-message",
        ]

        for eid in expected_ids:
            elem = self.wait_for_element(dash_driver, By.ID, eid)
            assert elem is not None, f"❌ العنصر {eid} غير موجود في الصفحة"

    def test_callbacks_execution(self, dash_driver):
        dash_driver.get(self.BASE_URL)

        button = self.wait_for_element(dash_driver, By.ID, "refresh-button")
        assert button is not None
        button.click()

        status = self.wait_for_element(dash_driver, By.ID, "status-message")
        assert "تم التحديث بنجاح" in status.text.strip()

    def test_main_graph_rendered(self, dash_driver):
        dash_driver.get(self.BASE_URL)

        graph = self.wait_for_element(dash_driver, By.ID, "main-graph")
        assert graph is not None
        inner_html = graph.get_attribute("innerHTML").lower()
        assert "plotly" in inner_html or "svg" in inner_html
