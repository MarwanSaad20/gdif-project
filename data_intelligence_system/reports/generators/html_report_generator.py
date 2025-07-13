import os
import base64
from io import BytesIO
from typing import List, Dict, Optional, Callable

import pandas as pd
import matplotlib.pyplot as plt
from jinja2 import Environment, FileSystemLoader, select_autoescape
from data_intelligence_system.utils.logger import get_logger

logger = get_logger("HTMLReportGenerator")


class HTMLReportGenerator:
    def __init__(self, output_path: str, template_dir: Optional[str] = None):
        """
        مولد تقرير HTML باستخدام Jinja2.

        :param output_path: المسار الكامل لحفظ التقرير.
        :param template_dir: مجلد القوالب (افتراضي داخل reports/templates)
        """
        self.output_path = output_path

        if template_dir is None:
            project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
            template_dir = os.path.join(project_root, "reports", "templates")

        self.env = Environment(
            loader=FileSystemLoader(template_dir),
            autoescape=select_autoescape(['html', 'xml'])
        )

    def _plot_to_base64(self, plt_figure) -> str:
        buf = BytesIO()
        plt_figure.savefig(buf, format="png", bbox_inches='tight')
        plt.close(plt_figure)
        buf.seek(0)
        img_base64 = base64.b64encode(buf.read()).decode('utf-8')
        return f"data:image/png;base64,{img_base64}"

    def _render_table(self, df: pd.DataFrame) -> str:
        return df.to_html(classes="table table-striped table-hover", border=0, index=False)

    def _render_section(self, section: Dict) -> Dict[str, str]:
        html_parts = []

        content = section.get("content")
        if content:
            html_parts.append(f"<p>{content}</p>")

        df = section.get("dataframe")
        if isinstance(df, pd.DataFrame):
            html_parts.append(self._render_table(df))

        plot_func: Optional[Callable] = section.get("plot_func")
        if callable(plot_func):
            fig = plot_func()
            img_html = self._plot_to_base64(fig)
            html_parts.append(f'<img src="{img_html}" alt="Plot" style="max-width: 100%; height: auto;">')

        return {
            "title": section.get("title", ""),
            "html_content": "".join(html_parts)
        }

    def build_report(
        self,
        title: str,
        sections: List[Dict],
        additional_css: Optional[str] = None,
        cover_image_path: Optional[str] = None
    ):
        template_name = "base_report.html"
        try:
            template = self.env.get_template(template_name)
        except Exception as e:
            raise FileNotFoundError(
                f"قالب التقرير '{template_name}' غير موجود في: {self.env.loader.searchpath}. الخطأ: {e}"
            )

        if cover_image_path and not os.path.exists(cover_image_path):
            logger.warning(f"صورة الغلاف غير موجودة: {cover_image_path}")
            cover_image_path = None

        rendered_sections = [self._render_section(sec) for sec in sections]

        html_content = template.render(
            title=title,
            sections=rendered_sections,
            additional_css=additional_css,
            cover_image=cover_image_path
        )

        os.makedirs(os.path.dirname(self.output_path), exist_ok=True)
        try:
            with open(self.output_path, "w", encoding="utf-8") as f:
                f.write(html_content)
            logger.info(f"تم إنشاء تقرير HTML: {self.output_path}")
        except Exception as e:
            logger.error(f"فشل في حفظ تقرير HTML: {e}", exc_info=True)
            raise


if __name__ == "__main__":
    def example_plot():
        fig, ax = plt.subplots()
        x = pd.Series(range(100))
        y = x.apply(lambda v: v ** 0.5)
        ax.plot(x, y)
        ax.set_title("مثال لرسم بياني بسيط")
        return fig

    sample_sections = [
        {"title": "مقدمة", "content": "هذا تقرير HTML مولد تلقائيًا باستخدام Jinja2."},
        {"title": "جدول بيانات", "dataframe": pd.DataFrame({
            "الاسم": ["أحمد", "ليلى", "سعيد"],
            "الدرجات": [88, 92, 79]
        })},
        {"title": "رسم بياني", "plot_func": example_plot}
    ]

    generator = HTMLReportGenerator(
        output_path=os.path.join("reports", "output", "sample_report.html")
    )
    generator.build_report("تقرير بيانات اختباري", sample_sections)
