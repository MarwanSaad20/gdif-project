import logging
from typing import Optional
from PIL import Image, ImageDraw, ImageFont


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def create_footer_banner(
    width: int = 1200,
    height: int = 100,
    bg_color: str = "#0d6efd",  # أزرق Bootstrap
    text: str = "© 2025 نظام تحليل البيانات الذكي",
    text_color: str = "white",
    font_path: Optional[str] = None,
    font_size: int = 28,
    output_path: str = "footer_banner.png",
    return_image: bool = False,
) -> Optional[Image.Image]:
    """
    إنشاء بانر للفوتر بخلفية ملونة ونص في المنتصف.

    Args:
        width (int): عرض الصورة بالبكسل.
        height (int): ارتفاع الصورة بالبكسل.
        bg_color (str): لون الخلفية (رمز HEX أو اسم لون).
        text (str): نص الفوتر.
        text_color (str): لون النص.
        font_path (Optional[str]): مسار الخط (اختياري).
        font_size (int): حجم الخط.
        output_path (str): مسار حفظ الصورة.
        return_image (bool): إذا كان True تعيد كائن PIL Image بدلاً من الحفظ.

    Returns:
        Optional[Image.Image]: كائن الصورة إذا تم التحديد، وإلا None.
    """

    # إنشاء صورة جديدة بخلفية اللون المحدد
    img = Image.new("RGBA", (width, height), bg_color)
    draw = ImageDraw.Draw(img)

    # تحميل الخط أو استخدام الافتراضي
    font = None
    if font_path:
        try:
            font = ImageFont.truetype(font_path, font_size)
        except Exception as e:
            logger.warning(f"تعذر تحميل الخط '{font_path}': {e} — سيتم استخدام الخط الافتراضي.")
    if not font:
        try:
            font = ImageFont.truetype("arial.ttf", font_size)
        except Exception:
            font = ImageFont.load_default()

    # قياس أبعاد النص بدقة باستخدام textbbox
    try:
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
    except Exception as e:
        logger.error(f"تعذر حساب أبعاد النص: {e}")
        text_width, text_height = font_size * len(text) // 2, font_size  # تقدير تقريبي

    # تموضع النص في مركز البانر
    x = (width - text_width) // 2
    y = (height - text_height) // 2

    # رسم النص
    draw.text((x, y), text, font=font, fill=text_color)

    if return_image:
        return img

    # حفظ الصورة النهائية مع التعامل مع الأخطاء
    try:
        img.save(output_path)
        logger.info(f"تم إنشاء بانر الفوتر وحفظه في: {output_path}")
    except Exception as e:
        logger.error(f"فشل حفظ الصورة: {e}")

    return None


if __name__ == "__main__":
    # ضع هنا مسار خط عربي إن أردت تخصيصه، مثال:
    # arabic_font_path = "C:/Windows/Fonts/arial.ttf"
    arabic_font_path = None
    create_footer_banner(font_path=arabic_font_path)
