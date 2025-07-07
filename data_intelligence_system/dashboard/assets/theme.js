// theme.js
// إعدادات ثيم الألوان والأنماط الخاصة بمشروع Dash
// يستخدم هذا الملف في Dash DAQ أو مكتبات Dash التي تدعم الثيمات,
// كما يمكن تضمينه في مجلد assets لتطبيق الأنماط يدوياً في الواجهة.

const theme = {
    colors: {
        background: "#121212",      // خلفية عامة داكنة جداً
        surface: "#1a1a1a",         // خلفيات البطاقات والحاويات
        primary: "#4fc3f7",         // اللون الأساسي للأزرار والعناوين
        primaryLight: "#81d4fa",    // لون فاتح من الأساسي (للتمرير وعند التفاعل)
        primaryDark: "#1f78b4",     // لون داكن للظل والخطوط الحدودية
        secondary: "#80deea",       // لون ثانوي للعناصر الثانوية والمساعدة
        error: "#f44336",           // لون أخطاء / تحذيرات
        success: "#00cc96",         // لون نجاح (مناسب لـ KPI أو التنبيهات الإيجابية)
        warning: "#ffae42",         // لون تحذير (اختياري)
        textPrimary: "#e0e0e0",     // لون النص الأساسي
        textSecondary: "#aaa",      // لون النص الثانوي أو التوضيحي
        border: "#333",             // لون الحدود والفواصل
        link: "#4fc3f7",            // لون الروابط
        linkHover: "#81d4fa"        // لون الروابط عند المرور (hover)
    },
    font: {
        family: "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif",
        size: 16,                   // رقم بدون px لتسهيل الاستخدام برمجياً
        weight: "400",
        weightBold: "700"
    },
    spacing: {
        paddingSmall: "0.5rem",
        paddingMedium: "1rem",
        paddingLarge: "1.5rem",
        marginSmall: "0.5rem",
        marginMedium: "1rem",
        marginLarge: "1.5rem"
    },
    borderRadius: "8px",
    boxShadow: "0 0 12px rgba(79, 195, 247, 0.3)",

    breakpoints: {
        mobile: "480px",
        tablet: "768px",
        desktop: "1024px"
    },

    // ألوان تفاعلية للـ hover و active
    interactive: {
        hoverBg: "#1f78b4",
        activeBg: "#1665a2"
    },

    // دوال مساعدة لاستدعاء الألوان بشكل برمجي
    getPrimaryColor() {
        return this.colors.primary;
    },
    getSecondaryColor() {
        return this.colors.secondary;
    },
    getErrorColor() {
        return this.colors.error;
    },
    getSuccessColor() {
        return this.colors.success;
    },
    getWarningColor() {
        return this.colors.warning;
    },
    getLinkColor() {
        return this.colors.link;
    },
    getLinkHoverColor() {
        return this.colors.linkHover;
    }
};

// إذا تستخدم إطار عمل يدعم ES6 modules يمكن استيراده هكذا:
// import theme from './theme.js';

// وإذا تستخدم Dash فقط، ضعه داخل مجلد assets وتطبق الأنماط عبر callbacks أو في ملفات CSS/JS مباشرة.

// لحذف التصدير إذا بيئة Dash لا تدعم modules:
// export default theme;
