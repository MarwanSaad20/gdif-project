from PIL import Image, ImageDraw, ImageFont

def create_footer_banner(
    width=1200,
    height=100,
    bg_color="#0d6efd",  # أزرق Bootstrap
    text="© 2025 نظام تحليل البيانات الذكي",
    text_color="white",
    font_path=None,
    font_size=28,
    output_path="footer_banner.png"
):
    """
    إنشاء بانر للفوتر بخلفية ملونة ونص في المنتصف.
    - width, height: أبعاد الصورة.
    - bg_color: لون الخلفية.
    - text: نص الفوتر.
    - text_color: لون النص.
    - font_path: مسار الخط (اختياري).
    - font_size: حجم الخط.
    - output_path: مسار حفظ الصورة.
    """

    # إنشاء صورة جديدة بخلفية اللون المحدد
    img = Image.new("RGBA", (width, height), bg_color)
    draw = ImageDraw.Draw(img)

    # تحميل الخط أو استخدام الافتراضي
    if font_path:
        try:
            font = ImageFont.truetype(font_path, font_size)
        except Exception as e:
            print(f"[تحذير] تعذر تحميل الخط: {e} — سيتم استخدام الخط الافتراضي.")
            font = ImageFont.load_default()
    else:
        # محاولة استخدام Arial أو الخط الافتراضي
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
        print(f"[خطأ] تعذر حساب أبعاد النص: {e}")
        text_width, text_height = font_size * len(text) // 2, font_size  # تقدير تقريبي

    # تموضع النص في مركز البانر
    x = (width - text_width) // 2
    y = (height - text_height) // 2

    # رسم النص
    draw.text((x, y), text, font=font, fill=text_color)

    # حفظ الصورة النهائية
    img.save(output_path)
    print(f"[✓] تم إنشاء بانر الفوتر وحفظه في: {output_path}")

if __name__ == "__main__":
    # ضع هنا مسار خط عربي إن أردت تخصيصه، مثال:
    # arabic_font_path = "C:/Windows/Fonts/arial.ttf"
    arabic_font_path = None
    create_footer_banner(font_path=arabic_font_path)
