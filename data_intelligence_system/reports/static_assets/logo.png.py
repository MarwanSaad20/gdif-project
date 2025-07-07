from PIL import Image, ImageDraw, ImageFont

def create_logo(
    width=400,
    height=400,
    bg_color=None,              # لون الخلفية (خارج الشعار)، None تعني خلفية شفافة
    circle_color="#ffffff",     # لون الدائرة الداخلية
    text="GDIF",                # نص الشعار
    text_color="#0d6efd",       # لون النص (يتناقض مع الأبيض)
    font_path=None,             # مسار الخط إذا كان مخصص
    font_size=100,
    output_path="logo.png"
):
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

    # إنشاء صورة جديدة مع خلفية شفافة أو بلون معين
    if bg_color:
        img = Image.new("RGBA", (width, height), bg_color)
    else:
        img = Image.new("RGBA", (width, height), (0, 0, 0, 0))  # شفافة

    draw = ImageDraw.Draw(img)

    # رسم الدائرة في المنتصف
    center = (width // 2, height // 2)
    radius = min(width, height) // 2 - 20
    draw.ellipse(
        (center[0] - radius, center[1] - radius, center[0] + radius, center[1] + radius),
        fill=circle_color
    )

    # تحميل الخط
    if font_path:
        try:
            font = ImageFont.truetype(font_path, font_size)
        except Exception as e:
            print(f"[تحذير] فشل تحميل الخط: {e}. سيتم استخدام الخط الافتراضي.")
            font = ImageFont.load_default()
    else:
        # محاولة استخدام خط Arial الشائع، وإلا الخط الافتراضي
        try:
            font = ImageFont.truetype("arial.ttf", font_size)
        except Exception:
            font = ImageFont.load_default()

    # قياس أبعاد النص بدقة
    try:
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
    except Exception as e:
        print(f"[خطأ] أثناء حساب أبعاد النص: {e}")
        text_width, text_height = font_size * len(text) // 2, font_size  # تقدير تقريبي

    # تموضع النص في مركز الدائرة
    text_x = (width - text_width) // 2
    text_y = (height - text_height) // 2

    # رسم النص
    draw.text((text_x, text_y), text, font=font, fill=text_color)

    # حفظ الصورة النهائية
    img.save(output_path)
    print(f"[✓] تم إنشاء الشعار وحفظه في: {output_path}")

if __name__ == "__main__":
    # يمكنك تخصيص مسار الخط هنا إذا أردت، أو ترك None لاستخدام الخط الافتراضي
    font_path = None
    create_logo(font_path=font_path)
