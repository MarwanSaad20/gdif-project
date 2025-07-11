import logging
from typing import Optional, Tuple
from PIL import Image, ImageDraw, ImageFont

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def create_logo(
    width: int = 400,
    height: int = 400,
    bg_color: Optional[str] = None,              # لون الخلفية (خارج الشعار)، None تعني خلفية شفافة
    circle_color: str = "#ffffff",               # لون الدائرة الداخلية
    text: str = "GDIF",                          # نص الشعار
    text_color: str = "#0d6efd",                 # لون النص (يتناقض مع الأبيض)
    font_path: Optional[str] = None,             # مسار الخط إذا كان مخصص
    font_size: int = 100,
    output_path: str = "logo.png"
) -> None:
    """
    إنشاء شعار بسيط مكوّن من دائرة ونص في الوسط.
    - bg_color: لون الخلفية الكلية (خارج الدائرة). إذا None تكون شفافة.
    - circle_color: لون الدائرة الداخلية.
    - text: نص الشعار.
    - text_color: لون النص.
    - font_path: مسار الخط (اختياري).
    - font_size: حجم الخط.
    - output_path: مسار حفظ الصورة.
    """

    def is_valid_color(c: Optional[str]) -> bool:
        if c is None:
            return True
        if not isinstance(c, str):
            return False
        if c.startswith("#") and (len(c) == 7 or len(c) == 4):
            return True
        return False

    if not is_valid_color(bg_color):
        logger.warning(f"لون الخلفية غير صالح: {bg_color}. سيتم تعيينه إلى شفاف.")
        bg_color = None

    if not is_valid_color(circle_color):
        logger.warning(f"لون الدائرة غير صالح: {circle_color}. سيتم تعيينه إلى الأبيض.")
        circle_color = "#ffffff"

    if not is_valid_color(text_color):
        logger.warning(f"لون النص غير صالح: {text_color}. سيتم تعيينه إلى أزرق Bootstrap.")
        text_color = "#0d6efd"

    # إنشاء صورة جديدة مع خلفية شفافة أو بلون معين
    img = Image.new("RGBA", (width, height), bg_color if bg_color else (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # رسم الدائرة في المنتصف
    center = (width // 2, height // 2)
    radius = min(width, height) // 2 - 20
    draw.ellipse(
        (center[0] - radius, center[1] - radius, center[0] + radius, center[1] + radius),
        fill=circle_color
    )

    # تحميل الخط
    font = None
    if font_path:
        try:
            font = ImageFont.truetype(font_path, font_size)
        except Exception as e:
            logger.warning(f"فشل تحميل الخط من {font_path}: {e}. سيتم استخدام الخط الافتراضي.")
    if font is None:
        for fallback_font in ["arial.ttf", "DejaVuSans.ttf"]:
            try:
                font = ImageFont.truetype(fallback_font, font_size)
                break
            except Exception:
                continue
        if font is None:
            font = ImageFont.load_default()

    # قياس أبعاد النص بدقة
    try:
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
    except Exception as e:
        logger.warning(f"فشل في حساب أبعاد النص: {e}")
        text_width = font_size * len(text) // 2
        text_height = font_size

    # تموضع النص في مركز الدائرة
    text_x = (width - text_width) // 2
    text_y = (height - text_height) // 2

    # رسم النص
    draw.text((text_x, text_y), text, font=font, fill=text_color)

    # حفظ الصورة النهائية مع حماية
    try:
        img.save(output_path)
        logger.info(f"تم إنشاء الشعار وحفظه في: {output_path}")
    except Exception as e:
        logger.error(f"فشل في حفظ الصورة: {e}")

if __name__ == "__main__":
    # يمكنك تخصيص مسار الخط هنا إذا أردت، أو ترك None لاستخدام الخط الافتراضي
    create_logo(font_path=None)
