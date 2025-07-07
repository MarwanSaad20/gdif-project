import time

import pytest
from dash.testing.application_runners import import_app
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By

# ✅ المسار الكامل لـ chromedriver.exe
CHROMEDRIVER_PATH = r"C:\Users\PC\.wdm\drivers\chromedriver\win64\138.0.7204.49\chromedriver-win32\chromedriver.exe"

@pytest.fixture(scope="session")
def browser_options():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    return options

@pytest.fixture
def dash_duo(browser_options):
    service = ChromeService(executable_path=CHROMEDRIVER_PATH)
    driver = webdriver.Chrome(service=service, options=browser_options)
    yield driver
    driver.quit()

@pytest.fixture
def dash_app():
    app = import_app("data_intelligence_system.dashboard.app")
    return app

def test_app_renders(dash_duo, dash_app):
    dash_app.run(debug=False, use_reloader=False, port=8050)
    time.sleep(2)  # ⏳ انتظر قليلاً حتى يبدأ السيرفر
    dash_duo.get("http://localhost:8050")

    assert "نظام تحليل البيانات العام" in dash_duo.title

    expected_ids = [
        "app-title",
        "refresh-button",
        "data-selector",
        "output-area",
        "status-message",
    ]
    for eid in expected_ids:
        element = dash_duo.find_element(By.ID, eid)
        assert element is not None, f"❌ العنصر {eid} غير موجود في الصفحة"

def test_callbacks_execution(dash_duo, dash_app):
    dash_app.run(debug=False, use_reloader=False, port=8050)
    time.sleep(2)
    dash_duo.get("http://localhost:8050")

    button = dash_duo.find_element(By.ID, "refresh-button")
    assert button is not None
    button.click()
    time.sleep(1)
    status = dash_duo.find_element(By.ID, "status-message")
    assert "تم التحديث بنجاح" in status.text.strip()

def test_main_graph_rendered(dash_duo, dash_app):
    dash_app.run(debug=False, use_reloader=False, port=8050)
    time.sleep(2)
    dash_duo.get("http://localhost:8050")

    graph = dash_duo.find_element(By.ID, "main-graph")
    assert graph is not None
    inner_html = graph.get_attribute("innerHTML").lower()
    assert "plotly" in inner_html or "svg" in inner_html
