import os
import pandas as pd
import matplotlib.pyplot as plt
import base64
from io import BytesIO
from jinja2 import Environment, FileSystemLoader, select_autoescape


class HTMLReportGenerator:
    def __init__(self, output_path: str, template_dir: str = None):
        """
        مولد تقرير HTML باستخدام Jinja2.

        :param output_path: المسار الكامل لحفظ التقرير (مثلاً reports/output/report.html)
        :param template_dir: مجلد القوالب (افتراضي داخل reports/templates)
        """
        self.output_path = output_path

        if template_dir is None:
            # تحديد المسار الجذري للمشروع بناءً على موقع الملف الحالي
            project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
            template_dir = os.path.join(project_root, "reports", "templates")

        self.env = Environment(
            loader=FileSystemLoader(template_dir),
            autoescape=select_autoescape(['html', 'xml'])
        )

    def _plot_to_base64(self, plt_figure) -> str:
        """
        تحويل رسم matplotlib إلى صورة base64 لتضمينها في HTML.
        """
        buf = BytesIO()
        plt_figure.savefig(buf, format="png", bbox_inches='tight')
        plt.close(plt_figure)
        buf.seek(0)
        img_base64 = base64.b64encode(buf.read()).decode('utf-8')
        return f"data:image/png;base64,{img_base64}"

    def _render_table(self, df: pd.DataFrame) -> str:
        """
        تحويل DataFrame إلى جدول HTML منسق باستخدام pandas.
        """
        return df.to_html(classes="table table-striped table-hover", border=0, index=False)

    def build_report(self, title: str, sections: list, additional_css: str = None, cover_image_path: str = None):
        """
        توليد تقرير HTML من الأقسام.

        :param title: عنوان التقرير
        :param sections: قائمة أقسام التقرير، كل قسم dict يحتوي على:
                         - title (str): عنوان القسم
                         - content (str, optional): نص أو HTML
                         - dataframe (pd.DataFrame, optional): جدول بيانات
                         - plot_func (callable, optional): دالة رسم matplotlib
        :param additional_css: نص CSS إضافي (اختياري)
        :param cover_image_path: مسار صورة الغلاف (اختياري)
        """
        # التحقق من وجود قالب التقرير
        template_name = "base_report.html"
        try:
            template = self.env.get_template(template_name)
        except Exception as e:
            raise FileNotFoundError(
                f"قالب التقرير '{template_name}' غير موجود في المسار: {self.env.loader.searchpath}. الخطأ: {e}"
            )

        # التحقق من وجود صورة الغلاف إذا تم تحديدها
        if cover_image_path and not os.path.exists(cover_image_path):
            print(f"[WARNING] صورة الغلاف غير موجودة: {cover_image_path}")
            cover_image_path = None

        rendered_sections = []

        for sec in sections:
            section_html = ""

            content = sec.get("content", "")
            if content:
                section_html += f"<p>{content}</p>"

            df = sec.get("dataframe")
            if isinstance(df, pd.DataFrame):
                section_html += self._render_table(df)

            plot_func = sec.get("plot_func")
            if callable(plot_func):
                fig = plot_func()
                img_html = self._plot_to_base64(fig)
                section_html += f'<img src="{img_html}" alt="Plot" style="max-width: 100%; height: auto;">'

            rendered_sections.append({
                "title": sec.get("title", ""),
                "html_content": section_html
            })

        html_content = template.render(
            title=title,
            sections=rendered_sections,
            additional_css=additional_css,
            cover_image=cover_image_path
        )

        os.makedirs(os.path.dirname(self.output_path), exist_ok=True)
        with open(self.output_path, "w", encoding="utf-8") as f:
            f.write(html_content)

        print(f"[INFO] تم إنشاء تقرير HTML: {self.output_path}")


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
