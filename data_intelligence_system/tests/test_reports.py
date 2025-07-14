import os
import pytest
import pandas as pd

# ✅ اجعل matplotlib يستخدم backend لا يحتاج GUI
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from tempfile import TemporaryDirectory

from data_intelligence_system.reports.generators.pdf_report_generator import PDFReportGenerator
from data_intelligence_system.reports.generators.excel_report_generator import ExcelReportGenerator
from data_intelligence_system.reports.generators.html_report_generator import HTMLReportGenerator
from data_intelligence_system.reports import report_dispatcher
from data_intelligence_system.reports.report_dispatcher import ReportDispatcher
from data_intelligence_system.reports.report_data_loader import ReportDataLoader
from data_intelligence_system.reports import report_config
from data_intelligence_system.reports.export_utils import (
    ensure_dir,
    save_dataframe_to_csv,
    save_dataframe_to_excel,
    save_plot,
    df_to_html_table,
    plot_correlation_heatmap,
    save_image_bytes
)


@pytest.fixture(scope="module")
def sample_df():
    return pd.DataFrame({
        "Name": ["Alice", "Bob", "Charlie"],
        "Score": [90, 85, 88],
        "Date": pd.to_datetime(["2025-01-01", "2025-01-02", "2025-01-03"])
    })


@pytest.fixture(scope="module")
def sample_sections():
    return [
        {"title": "Section One", "content": "Simple paragraph text."},
        {"title": "Section Two", "content": "Another paragraph."}
    ]


@pytest.fixture(scope="module")
def sample_excel_sections():
    return [
        {
            "title": "Excel Overview",
            "paragraphs": ["Excel summary paragraph."],
            "tables": [
                {"headers": ["A", "B"], "rows": [[1, 2], [3, 4]]}
            ]
        }
    ]


@pytest.fixture(scope="module")
def sample_html_sections():
    def example_plot():
        fig, ax = plt.subplots()
        ax.plot([1, 2, 3], [4, 5, 6])
        return fig
    return [
        {"title": "Intro", "content": "Sample HTML content."},
        {"title": "Table", "dataframe": pd.DataFrame({"X": [1, 2], "Y": [3, 4]})},
        {"title": "Plot", "plot_func": example_plot}
    ]


@pytest.fixture(scope="module")
def sample_corr_df():
    return pd.DataFrame({
        "A": [1.0, 0.5],
        "B": [0.5, 1.0]
    }, index=["A", "B"])


# -------- Generators tests --------
def test_pdf_report_generation(sample_sections):
    with TemporaryDirectory() as tmpdir:
        path = os.path.join(tmpdir, "report.pdf")
        gen = PDFReportGenerator(path, title="Test PDF")
        gen.build_pdf(sample_sections)
        assert os.path.exists(path) and os.path.getsize(path) > 0


def test_excel_report_generation(sample_excel_sections):
    with TemporaryDirectory() as tmpdir:
        path = os.path.join(tmpdir, "report.xlsx")
        gen = ExcelReportGenerator(path)
        gen.generate(title="Excel Test", sections=sample_excel_sections)
        assert os.path.exists(path) and os.path.getsize(path) > 0


def test_html_report_generation(sample_html_sections):
    with TemporaryDirectory() as tmpdir:
        path = os.path.join(tmpdir, "report.html")
        gen = HTMLReportGenerator(path)
        gen.build_report(title="HTML Test", sections=sample_html_sections)
        assert os.path.exists(path)
        with open(path, encoding="utf-8") as f:
            content = f.read()
            assert "<html" in content.lower() or "<!doctype html" in content.lower()


# -------- Dispatcher tests --------
def test_report_dispatcher_all_types(sample_df):
    with TemporaryDirectory() as tmpdir:
        dispatcher = ReportDispatcher(output_dir=tmpdir)

        pdf = dispatcher.dispatch("pdf", sample_df, {"filename": "test_pdf"})
        excel = dispatcher.dispatch("excel", sample_df, {"filename": "test_excel"})
        html = dispatcher.dispatch("html", sample_df, {"filename": "test_html"})
        csv = dispatcher.dispatch("csv", sample_df, {"filename": "test_csv"})

        for path in [pdf, excel, html, csv]:
            assert os.path.exists(path)


def test_generate_report_function(sample_df):
    with TemporaryDirectory() as tmpdir:
        dispatcher = ReportDispatcher(output_dir=tmpdir)
        path = dispatcher.dispatch("pdf", sample_df, {"filename": "gen_report"})
        assert os.path.exists(path)


# -------- Data loader tests --------
def test_report_data_loader(sample_df):
    with TemporaryDirectory() as tmpdir:
        csv_file = os.path.join(tmpdir, "data.csv")
        sample_df.to_csv(csv_file, index=False)
        loader = ReportDataLoader(processed_data_path=tmpdir)

        datasets = loader.load_all_csvs()
        assert "data.csv" in datasets
        df_loaded = loader.get_dataset("data.csv")
        assert df_loaded.equals(datasets["data.csv"])

        summary = loader.load_summary_for_report("data.csv")
        assert summary["n_rows"] == 3 and summary["n_cols"] == 3

        kpis = loader.get_kpi_summary("data.csv")
        assert kpis["total_records"] == 3


# -------- Config tests --------
def test_report_config_values():
    assert isinstance(report_config.REPORT_CONFIG, dict)
    assert "title" in report_config.REPORT_CONFIG  # تم تعديل المفتاح هنا
    assert isinstance(report_config.REPORT_OPTIONS, dict)


# -------- Export utils tests --------
def test_ensure_dir_creates_directory():
    with TemporaryDirectory() as tmpdir:
        test_dir = os.path.join(tmpdir, "new_folder")
        assert not os.path.exists(test_dir)
        ensure_dir(test_dir)
        assert os.path.isdir(test_dir)


def test_save_dataframe_to_csv_and_read(sample_df):
    with TemporaryDirectory() as tmpdir:
        save_dataframe_to_csv(sample_df, "test", output_dir=tmpdir)
        path = os.path.join(tmpdir, "test.csv")
        assert os.path.exists(path)
        loaded = pd.read_csv(path, parse_dates=["Date"])  # ✅ إضافة parse_dates للحفاظ على نوع التاريخ
        pd.testing.assert_frame_equal(loaded, sample_df)


def test_save_dataframe_to_excel_and_read(sample_df):
    with TemporaryDirectory() as tmpdir:
        save_dataframe_to_excel(sample_df, "test", output_dir=tmpdir)
        path = os.path.join(tmpdir, "test.xlsx")
        assert os.path.exists(path)
        loaded = pd.read_excel(path)
        pd.testing.assert_frame_equal(loaded, sample_df)


def test_save_plot_creates_png():
    fig, ax = plt.subplots()
    ax.plot([1, 2], [3, 4])
    with TemporaryDirectory() as tmpdir:
        save_plot(fig, "plot", output_dir=tmpdir)
        path = os.path.join(tmpdir, "plot.png")
        assert os.path.exists(path) and os.path.getsize(path) > 0


def test_df_to_html_table_output(sample_df):
    html = df_to_html_table(sample_df, classes="table")
    assert "<table" in html and "Name" in html


def test_plot_correlation_heatmap_creates_png(sample_corr_df):
    with TemporaryDirectory() as tmpdir:
        plot_correlation_heatmap(sample_corr_df, "heatmap", output_dir=tmpdir)
        path = os.path.join(tmpdir, "heatmap.png")
        assert os.path.exists(path) and os.path.getsize(path) > 0


def test_save_image_bytes_returns_bytes():
    fig, ax = plt.subplots()
    ax.plot([1, 2], [3, 4])
    img_bytes = save_image_bytes(fig)
    assert isinstance(img_bytes, bytes) and len(img_bytes) > 100


def test_save_dataframe_to_csv_raises_on_empty():
    with pytest.raises(ValueError):
        save_dataframe_to_csv(pd.DataFrame(), "empty")


def test_save_dataframe_to_excel_raises_on_empty():
    with pytest.raises(ValueError):
        save_dataframe_to_excel(pd.DataFrame(), "empty")


def test_plot_correlation_heatmap_raises_on_empty():
    with pytest.raises(ValueError):
        plot_correlation_heatmap(pd.DataFrame(), "fail")
