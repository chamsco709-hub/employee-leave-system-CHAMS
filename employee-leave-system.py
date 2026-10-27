import streamlit as st
import pandas as pd

# 1. ضبط إعدادات الصفحة وجعلها عريضة لتناسب لوحات التحكم الإدارية
st.set_page_config(
    page_title="النظام المتكامل لإدارة الموارد البشرية والشؤون الإدارية",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. حقن واجهة التصميم المطور CSS (شريط علوي مع قوائم منسدلة سحابية أنيقة)
style_css = (
    "<style>"
    "header[data-testid='stHeader'] { visibility: hidden; height: 0px; }"
    "[data-testid='stSidebar'] { display: none !important; width: 0px !important; }"
    "html, body, [class*='css'], .stMarkdown, p, h1, h2, h3, h4, h5, h6, label {"
    "font-family: 'Segoe UI', Arial, sans-serif !important; direction: rtl !important; text-align: right !important; color: #1E293B !important;}"
    ".block-container { padding-top: 1rem !important; padding-left: 2rem !important; padding-right: 2rem !important; max-width: 100% !important; background-color: #F8FAFC !important; min-height: 100vh; }"
    "/* تصميم الشريط العلوي الفاخر */"
    ".top-navbar { background-color: #4F46E5 !important; padding: 14px 24px; margin: -1rem -2rem 24px -2rem; display: flex; align-items: center; justify-content: space-between; box-shadow: 0 4px 12px rgba(79, 70, 229, 0.15); }"
    ".navbar-title { color: #FFFFFF !important; font-size: 18px !important; font-weight: 700 !important; margin: 0; }"
    ".navbar-user { color: #EEF2F6 !important; font-size: 13px !important; font-weight: 500; }"
    "/* تصميم حاويات ونماذج العمليات */"
    ".entry-card { background: #FFFFFF; padding: 24px; border-radius: 12px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.02); border: 1px solid #E2E8F0; margin-bottom: 24px; }"
    "/* كروت المؤشرات السريعة */"
    ".kpi-box { background: #FFFFFF; border-radius: 10px; padding: 20px; border: 1px solid #E2E8F0; border-right: 5px solid #4F46E5; box-shadow: 0 2px 4px rgba(0,0,0,0.01); text-align: right; margin-bottom: 15px; }"
    ".kpi-title { font-size: 13px; color: #64748B; font-weight: 600; margin-bottom: 6px; }"
    ".kpi-value { font-size: 24px; color: #0F172A; font-weight: 700; }"
    "/* تنسيق الحقول والـ Streamlit Widgets */"
    "div[data-testid='stDateInput'] input, input, textarea, select { background-color: #FFFFFF !important; color: #0F172A !important; font-weight: 500 !important; border-radius: 8px !important; border: 1px solid #CBD5E1 !important; padding: 10px 14px !important; }"
    ".stButton button { background-color: #4F46E5 !important; color: white !important; border-radius: 8px !important; padding: 8px 16px !important; font-weight: 600 !important; border: none !important; width: 100%; }"
    ".stButton button:hover { background-color: #4338CA !important; }"
    "</style>"
)
st.markdown(style_css, unsafe_allow_html=True)

# 3. عرض شريط النظام العلوي المطور (Top Navbar)
st.markdown(
    """
    <div class="top-navbar">
        <div class="navbar-title">🏢 النظام المتكامل لإدارة الموارد البشرية والشؤون الإدارية</div>
        <div class="navbar-user">👤 مرحباً: مسؤول النظام (Admin)</div>
    </div>
    """,
    unsafe_allow_html=True
)

# 4. بناء القوائم المنسدلة التفاعلية في منطقة التحكم العلوية باستخدام Streamlit Columns
st.markdown("##### 🧭 شريط التنقل السريع وإصدار الأوامر:")
col_nav1, col_nav2, col_nav3, col_nav4 = st.columns(4)

with col_nav1:
    section_menu = st.selectbox(
        "👥 شؤون الموظفين:",
        ["لوحة التحكم الرئيسية", "دليل الموظفين والأرصدة", "إضافة موظف جديد", "إدارة العهد والأصول"]
    )
with col_nav2:
    attendance_menu = st.selectbox(
        "⏱️ الحضور والانصراف:",
        ["إجراء حركة حضور", "سجل البصمة اليومي", "شفتات العمل والمناوبات", "احتساب الساعات الإضافية"]
    )
with col_nav3:
    leaves_menu = st.selectbox(
        "📝 الإجازات والطلبات:",
        ["الطلبات قيد الانتظار", "سجل الإجازات المعتمدة", "تقديم طلب إجازة", "مأموريات العمل الخارجية"]
    )
with col_nav4:
    payroll_menu = st.selectbox(
        "💰 الرواتب والماليات:",
        ["إصدار مسير الرواتب", "السلف والقروض المالية", "المكافآت والاستقطاعات", "إعدادات الأقسام والفروع"]
    )

st.markdown("<hr style='border: 0.5px solid #E2E8F0; margin: 10px 0 24px 0;'>", unsafe_allow_html=True)

# 5. تحديد شاشة العرض بناءً على خيارات القوائم المنسدلة العلوية
if section_menu == "لوحة التحكم الرئيسية":
    st.markdown("<h4 style='font-weight:700; color:#0F172A; margin-bottom:15px;'>📊 ملخص مؤشرات الأداء الحالية للمنشأة</h4>", unsafe_allow_html=True)
    
    col_k1, col_k2, col_k3, col_k4 = st.columns(4)
    with col_k1:
        st.markdown("<div class='kpi-box'><div class='kpi-title'>👥 إجمالي الموظفين</div><div class='kpi-value'>١,٢٤٠ موظف</div></div>", unsafe_allow_html=True)
    with col_k2:
        st.markdown("<div class='kpi-box' style='border-right-color:#EA580C;'><div class='kpi-title' style='color:#EA580C;'>⏳ طلبات معلقة</div><div class='kpi-value' style='color:#EA580C;'>١٢ طلب</div></div>", unsafe_allow_html=True)
    with col_k3:
        st.markdown("<div class='kpi-box' style='border-right-color:#16A34A;'><div class='kpi-title' style='color:#16A34A;'>🟢 نسبة الحضور اليومي</div><div class='kpi-value' style='color:#16A34A;'>٩٤٪</div></div>", unsafe_allow_html=True)
    with col_k4:
        st.markdown("<div class='kpi-box' style='border-right-color:#2563EB;'><div class='kpi-title' style='color:#2563EB;'>💰 إجمالي الرواتب الأساسية</div><div class='kpi-value' style='color:#2563EB;'>٥,٢٠,٠٠٠ ج.م</div></div>", unsafe_allow_html=True)

    # جدول استعراضي سريع للبيانات الأخيرة
    st.markdown("<h5 style='font-weight:600; color:#1F2937; margin-top:15px; margin-bottom:10px;'>📋 أحدث طلبات الإجازات الواردة</h5>", unsafe_allow_html=True)
    sample_df = pd.DataFrame({
        "رقم الطلب":,
        "كود الموظف": ["EMP01", "EMP05", "EMP08"],
        "اسم الموظف": ["أحمد محمود", "سارة محمد", "كريم عبد العزيز"],
        "نوع الإجازة": ["إجازة سنوية", "إجازة مرضية", "إجازة عارضة"],
        "الفترة": ["من 2026-11-01 إلى 2026-11-05", "يوم 2026-10-28", "من 2026-11-10 إلى 2026-11-12"],
        "الحالة": ["⏳ قيد الانتظار", "⏳ قيد الانتظار", "⏳ قيد الانتظار"]
    })
    st.dataframe(sample_df, use_container_width=True, hide_index=True)

elif section_menu == "إضافة موظف جديد":
    st.markdown("<h4 style='font-weight:700; color:#0F172A; margin-bottom:15px;'>👥 إضافة سجل موظف جديد ونموذج العقود</h4>", unsafe_allow_html=True)
    with st.form("new_employee_form"):
        st.markdown("<div class='entry-card'>", unsafe_allow_html=True)
        c_emp1, c_emp2 = st.columns(2)
        with c_emp1:
            st.text_input("كود الموظف الوظيفي:")
            st.text_input("اسم الموظف بالكامل (كما في الهوية):")
        with c_emp2:
            st.selectbox("القسم التابع له الموظف:", ["الإدارة المالية", "التقنية والمعلومات", "الموارد البشرية", "الحسابات والمراجعة"])
            st.number_input("الراتب الأساسي المقابل للتعاقد:", value=5000)
        st.form_submit_button("💾 حفظ السجل وتوليد الرقم الوظيفي")
        st.markdown("</div>", unsafe_allow_html=True)

else:
    # شاشة افتراضية عامة لباقي الخيارات الفرعية المنتقاة من القوائم المنسدلة
    st.markdown("<div class='entry-card'>", unsafe_allow_html=True)
    st.info(f"📂 شاشة العرض والعمليات الحالية تتبع خيارك: **{section_menu} / {attendance_menu} / {leaves_menu} / {payroll_menu}**")
    st.markdown("</div>", unsafe_allow_html=True)