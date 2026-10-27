import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import altair as alt
from datetime import datetime, date, time, timedelta
import io
import base64
import json
import os

# ضبط إعدادات الصفحة وتفعيل الواجهة الواسعة مع إخفاء القائمة الجانبية تماماً
st.set_page_config(
    page_title="النظام المتكامل لإدارة الموارد البشرية",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 🔑 ملف الترخيص الخاص بهذه النسخة
LICENSE_FILE = "client_license.json"

def get_client_license():
    """قراءة بيانات الترخيص والشركة"""
    if os.path.exists(LICENSE_FILE):
        try:
            with open(LICENSE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {
        "id": "company_default",
        "license": "LIC-1001",
        "name": "شركة الشمس لإدارة المنشآت السياحية"
    }

client_data = get_client_license()
company_id = client_data["id"]
company_license = client_data["license"]
company_display_name = client_data["name"]

COMPANIES_DIR = "client_companies_data"
if not os.path.exists(COMPANIES_DIR):
    os.makedirs(COMPANIES_DIR)

COMPANY_FILE = os.path.join(COMPANIES_DIR, f"{company_id}_data.json")

# ---------------------------------------------------------
# 💾 دوال الحفظ والاستعادة التلقائية للبيانات
# ---------------------------------------------------------
def load_company_data():
    """تحميل بيانات الشركة الحالية"""
    if os.path.exists(COMPANY_FILE):
        try:
            with open(COMPANY_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                
                if "employees" in data and len(data["employees"]) > 0:
                    st.session_state.employees = pd.DataFrame(data["employees"])
                else:
                    st.session_state.employees = pd.DataFrame(columns=[
                        "كود الموظف", "اسم الموظف", "الوظيفة", "القسم", "الفرع", "صلاحية الموظف",
                        "الراتب الأساسي",
                        "رصيد سنوي (إجمالي)", "سنوي مستهلك", "سنوي متبقي",
                        "رصيد أسبوعي (إجمالي)", "أسبوعي مستهلك", "أسبوعي متبقي",
                        "رصيد رسمي (إجمالي)", "رسمي مستهلك", "رسمي متبقي",
                        "إجازات مرضية (أيام)"
                    ])

                if "requests" in data and len(data["requests"]) > 0:
                    st.session_state.requests = pd.DataFrame(data["requests"])
                else:
                    st.session_state.requests = pd.DataFrame(columns=[
                        "رقم الطلب", "كود الموظف", "اسم الموظف", "الوظيفة", "الفرع", "نوع الإجازة", "من تاريخ", "إلى تاريخ", "عدد الأيام", "السبب", "الحالة"
                    ])

                if "attendance" in data and len(data["attendance"]) > 0:
                    st.session_state.attendance = pd.DataFrame(data["attendance"])
                else:
                    st.session_state.attendance = pd.DataFrame(columns=[
                        "التاريخ", "كود الموظف", "اسم الموظف", "الفرع", "بداية العمل الرسمية", "نهاية العمل الرسمية", 
                        "وقت الحضور الفعلي", "وقت الانصراف الفعلي", "الحالة", 
                        "التأخير الصباحي (دقيقة)", "انصراف مبكر (دقيقة)", "إضافي بعد العمل (دقيقة)", 
                        "حضور مبكر (دقيقة)", "خروج متأخر (دقيقة)", "دقائق التأخير"
                    ])

                if "financial_transactions" in data and len(data["financial_transactions"]) > 0:
                    st.session_state.financial_transactions = pd.DataFrame(data["financial_transactions"])
                else:
                    st.session_state.financial_transactions = pd.DataFrame(columns=[
                        "التاريخ", "كود الموظف", "اسم الموظف", "الفرع", "النوع", "المبلغ / القيمة", "البيان / السبب"
                    ])

                if "users" in data and len(data["users"]) > 0:
                    st.session_state.users = pd.DataFrame(data["users"])
                else:
                    st.session_state.users = pd.DataFrame([
                        {"اسم المستخدم": "admin", "الاسم الكامل": "المدير العام", "الفرع التابع": "المركز الرئيسي", "القسم التابع": "الإدارة العليا", "الصلاحية": "مشرف عام (Admin)", "البريد الإلكتروني": "admin@company.com", "الحالة": "نشط", "الرسم السري": "1-2-3"}
                    ])

                if "company_info" in data:
                    st.session_state.company_info = data["company_info"]
        except Exception as e:
            st.error(f"خطأ في تحميل ملف الشركة: {e}")
    else:
        st.session_state.employees = pd.DataFrame([
            {
                "كود الموظف": "EMP001", "اسم الموظف": "أحمد محمود", "الوظيفة": "محاسب أول", "القسم": "الإدارة المالية", "الفرع": "المركز الرئيسي",
                "صلاحية الموظف": "اعتماد الطلبات", "الراتب الأساسي": 5000,
                "رصيد سنوي (إجمالي)": 21, "سنوي مستهلك": 3, "سنوي متبقي": 18,
                "رصيد أسبوعي (إجمالي)": 4, "أسبوعي مستهلك": 1, "أسبوعي متبقي": 3,
                "رصيد رسمي (إجمالي)": 10, "رسمي مستهلك": 2, "رسمي متبقي": 8,
                "إجازات مرضية (أيام)": 0
            }
        ])
        st.session_state.requests = pd.DataFrame(columns=[
            "رقم الطلب", "كود الموظف", "اسم الموظف", "الوظيفة", "الفرع", "نوع الإجازة", "من تاريخ", "إلى تاريخ", "عدد الأيام", "السبب", "الحالة"
        ])
        st.session_state.attendance = pd.DataFrame(columns=[
            "التاريخ", "كود الموظف", "اسم الموظف", "الفرع", "بداية العمل الرسمية", "نهاية العمل الرسمية", 
            "وقت الحضور الفعلي", "وقت الانصراف الفعلي", "الحالة", 
            "التأخير الصباحي (دقيقة)", "انصراف مبكر (دقيقة)", "إضافي بعد العمل (دقيقة)", 
            "حضور مبكر (دقيقة)", "خروج متأخر (دقيقة)", "دقائق التأخير"
        ])
        st.session_state.financial_transactions = pd.DataFrame(columns=[
            "التاريخ", "كود الموظف", "اسم الموظف", "الفرع", "النوع", "المبلغ / القيمة", "البيان / السبب"
        ])
        st.session_state.users = pd.DataFrame([
            {"اسم المستخدم": "admin", "الاسم الكامل": "المدير العام", "الفرع التابع": "المركز الرئيسي", "القسم التابع": "الإدارة العليا", "الصلاحية": "مشرف عام (Admin)", "البريد الإلكتروني": "admin@company.com", "الحالة": "نشط", "الرسم السري": "1-2-3"}
        ])
        st.session_state.company_info = {
            "name": company_display_name,
            "address": "القاهرة، جمهورية مصر العربية",
            "cr": "123456",
            "tax": "987-654-321",
            "contact": "هاتف: 01000000000 | بريد: info@company.com",
            "license": company_license,
            "logo": None
        }

def auto_save_data():
    """حفظ التغييرات في ملف هذه الشركة"""
    try:
        data_to_save = {
            "employees": st.session_state.employees.to_dict(orient='records'),
            "requests": st.session_state.requests.to_dict(orient='records'),
            "attendance": st.session_state.attendance.to_dict(orient='records'),
            "financial_transactions": st.session_state.financial_transactions.to_dict(orient='records'),
            "users": st.session_state.users.to_dict(orient='records'),
            "company_info": st.session_state.company_info
        }
        with open(COMPANY_FILE, "w", encoding="utf-8") as f:
            json.dump(data_to_save, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"خطأ في الحفظ التلقائي: {e}")

load_company_data()
st.session_state.company_info["name"] = company_display_name
st.session_state.company_info["license"] = company_license

def select_time_12h(label_prefix, key_prefix, default_hour=8, default_minute=0, default_period="صباحاً (AM)"):
    st.markdown(f"**{label_prefix}**")
    c1, c2, c3 = st.columns([1, 1, 1.2])
    with c1:
        hour = st.selectbox("ساعة", list(range(1, 13)), index=default_hour-1 if 1 <= default_hour <= 12 else 7, key=f"{key_prefix}_h")
    with c2:
        minute = st.selectbox("دقيقة (0-59)", list(range(0, 60)), index=default_minute, key=f"{key_prefix}_m")
    with c3:
        period = st.radio("الفترة", ["صباحاً (AM)", "مساءً (PM)"], index=0 if "صباحاً" in default_period else 1, key=f"{key_prefix}_p", horizontal=True)
    
    h_24 = hour
    if period == "مساءً (PM)" and hour != 12:
        h_24 += 12
    elif period == "صباحاً (AM)" and hour == 12:
        h_24 = 0
        
    formatted_str = f"{hour:02d}:{minute:02d} {'AM' if period == 'صباحاً (AM)' else 'PM'}"
    return time(h_24, minute), formatted_str

def render_print_button():
    components.html("""
        <div style="text-align: left; margin-bottom: 15px;" class="no-print">
            <button onclick="
                window.parent.print();
            " style="
                background: linear-gradient(135deg, #E50914 0%, #B20710 100%);
                color: white;
                padding: 10px 22px;
                border: none;
                border-radius: 12px;
                font-size: 13px;
                font-weight: bold;
                cursor: pointer;
                box-shadow: 0 4px 15px rgba(229, 9, 20, 0.4);
                font-family: 'Tahoma', sans-serif;
                transition: all 0.3s ease;
            ">
                🖨️ طباعة السجل الحالي بشكل نظيف
            </button>
        </div>
    """, height=50)

# 🎨 تصميم CSS السينمائي اللامع وإلغاء القائمة الجانبية تماماً
st.markdown("""
    <style>
    header[data-testid="stHeader"] { visibility: hidden; height: 0px; }
    [data-testid="stSidebar"] { display: none !important; width: 0px !important; }
    
    html, body, [class*="css"], .stMarkdown, div, span, p, h1, h2, h3, h4, h5, h6, label {
        font-family: 'Tahoma', 'Segoe UI', sans-serif !important;
        direction: rtl !important;
        text-align: right !important;
        color: #F1F5F9 !important;
    }
    
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 4rem !important;
        padding-left: 2.5rem !important;
        padding-right: 2.5rem !important;
        max-width: 100% !important;
        background: linear-gradient(135deg, #121212 0%, #1A1A1A 50%, #0B0B0B 100%) !important;
        min-height: 100vh;
    }
    
    /* 📌 بار القوائم العلوي السينمائي الثابت */
    .cinema-top-bar {
        position: sticky;
        top: 0rem;
        z-index: 9999;
        background: rgba(18, 18, 18, 0.95);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        padding: 12px 20px;
        border-radius: 16px;
        margin-bottom: 20px;
        border-bottom: 2.5px solid #E50914;
        box-shadow: 0 15px 35px rgba(0,0,0,0.7);
    }
    
    div[data-testid="stDateInput"],
    div[data-testid="stDateInput"] > div,
    div[data-testid="stDateInput"] input,
    div[data-testid="stDateInput"] div {
        background-color: rgba(30, 41, 59, 0.9) !important;
        color: #FFFFFF !important;
        font-weight: bold !important;
        border-radius: 12px !important;
        border-color: #334155 !important;
    }
    
    label p, .stRadio label, .stSelectbox label, .stTextInput label, .stNumberInput label, .stDateInput label {
        color: #CBD5E1 !important;
        font-weight: bold !important;
        font-size: 13.5px !important;
    }
    
    input, textarea, select {
        background-color: rgba(30, 41, 59, 0.9) !important;
        color: #FFFFFF !important;
        font-size: 13.5px !important;
        font-weight: bold !important;
        border-radius: 12px !important;
        border: 1.5px solid #475569 !important;
        padding: 10px !important;
    }
    
    .glass-header {
        background: rgba(30, 30, 30, 0.85);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        color: #FFFFFF !important;
        padding: 16px 22px;
        border-radius: 18px;
        width: 100%;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
        box-sizing: border-box;
        margin-bottom: 12px;
    }
    .header-top-system {
        text-align: center !important;
        width: 100%;
        margin-bottom: 6px;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        padding-bottom: 6px;
    }
    .header-top-system h2 {
        font-size: 15px !important;
        font-weight: bold !important;
        color: #F87171 !important;
        margin: 0 !important;
    }
    .comp-name-txt {
        font-size: 17px !important;
        font-weight: bold !important;
        margin-bottom: 3px !important;
        color: #FFFFFF !important;
    }
    .comp-info-txt {
        font-size: 12px !important;
        margin: 2px 0 !important;
        color: #94A3B8 !important;
        line-height: 1.4;
    }
    
    .glass-card {
        background: rgba(30, 30, 30, 0.75);
        backdrop-filter: blur(15px);
        -webkit-backdrop-filter: blur(15px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-right: 6px solid #E50914;
        padding: 18px 20px;
        border-radius: 16px;
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.4);
        text-align: right !important;
        margin-bottom: 15px;
        transition: all 0.3s ease;
    }
    .glass-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 12px 30px rgba(229, 9, 20, 0.2);
    }
    .glass-card-title {
        font-size: 12.5px;
        color: #94A3B8;
        font-weight: bold;
        margin-bottom: 6px;
    }
    .glass-card-value {
        font-size: 24px;
        color: #FFFFFF;
        font-weight: bold;
    }
    
    .section-header {
        font-size: 17px !important;
        font-weight: bold !important;
        color: #F87171 !important;
        border-bottom: 2.5px solid #E50914;
        padding-bottom: 10px;
        margin-top: 22px !important;
        margin-bottom: 16px !important;
        text-align: right !important;
        direction: rtl !important;
    }
    
    table.custom-table {
        width: 100%;
        border-collapse: separate;
        border-spacing: 0;
        margin-top: 10px !important;
        margin-bottom: 20px !important;
        background-color: rgba(24, 24, 24, 0.9);
        backdrop-filter: blur(10px);
        color: #FFFFFF;
        direction: rtl !important;
        text-align: right !important;
        border-radius: 14px;
        overflow: hidden;
        box-shadow: 0 8px 25px rgba(0,0,0,0.4);
        border: 1px solid rgba(255, 255, 255, 0.08);
    }
    table.custom-table th, table.custom-table td {
        border-bottom: 1px solid #333333;
        border-left: 1px solid #222222;
        padding: 12px 16px;
        text-align: right !important;
        font-size: 13px;
        color: #E2E8F0 !important;
        background-color: transparent !important;
    }
    table.custom-table th {
        background-color: rgba(229, 9, 20, 0.2) !important;
        font-weight: bold;
        color: #FCA5A5 !important;
        border-bottom: 2.5px solid #E50914;
    }
    
    .entry-form-area {
        background: rgba(30, 30, 30, 0.85);
        backdrop-filter: blur(15px);
        padding: 26px;
        border-radius: 18px;
        box-shadow: 0 8px 25px rgba(0,0,0,0.4);
        border: 1px solid rgba(255, 255, 255, 0.08);
        margin-bottom: 20px;
    }
    
    @media print {
        @page { size: A4 landscape; margin: 10mm; }
        body, .stApp, .block-container {
            background-color: #FFFFFF !important;
            color: #000000 !important;
            direction: rtl !important;
            text-align: right !important;
            width: 100% !important;
            margin: 0 !important;
            padding: 0 !important;
        }
        button, .stButton, iframe, div[data-testid="stHeader"], .no-print, .entry-form-area, hr, .cinema-top-bar { display: none !important; }
        .glass-header { background: #FFFFFF !important; border: 1.5px solid #E50914; box-shadow: none; }
        table.custom-table { width: 100% !important; border: 1.5px solid #E50914 !important; }
        table.custom-table th { background-color: #E50914 !important; color: #FFFFFF !important; }
    }
    </style>
""", unsafe_allow_html=True)

if 'is_authenticated' not in st.session_state: st.session_state.is_authenticated = False
if 'current_logged_user' not in st.session_state: st.session_state.current_logged_user = ""
if 'current_user_dept' not in st.session_state: st.session_state.current_user_dept = ""
if 'current_user_branch' not in st.session_state: st.session_state.current_user_branch = ""
if 'current_user_role' not in st.session_state: st.session_state.current_user_role = ""

def render_printable_table(df):
    if df.empty:
        st.info("لا توجد بيانات متاحة للعرض.")
        return
    html = f'<div class="printable-right-align">{df.to_html(classes="custom-table", index=False, escape=False)}</div>'
    st.markdown(html, unsafe_allow_html=True)

def render_company_header():
    info = st.session_state.company_info
    logo_html = '<div style="padding: 8px 12px; border: 1.5px dashed rgba(229,9,20,0.4); border-radius: 10px; font-size: 11px; color: #F87171; background: rgba(0,0,0,0.3); font-weight: bold;">🎬 شعار المنصة</div>'
    if info.get("logo") is not None:
        try:
            logo_html = f'<img src="data:image/png;base64,{info.get("logo")}" alt="Logo" style="max-height: 65px; max-width: 140px; object-fit: contain; background: white; border-radius: 8px; padding: 4px;" />'
        except Exception:
            pass
            
    st.markdown(
        f"""
        <div class="glass-header">
            <div class="header-top-system">
                <h2>🍿 منصة عرض شؤون الموظفين والإدارة &nbsp;|&nbsp; شركة: {info.get("name", "")}</h2>
            </div>
            <div style="display: flex; justify-content: space-between; align-items: center; width: 100%;">
                <div>
                    <div class="comp-name-txt">{info.get("name", "")}</div>
                    <div class="comp-info-txt">📍 {info.get("address", "")} &nbsp;|&nbsp; 📋 سجل تجاري: {info.get("cr", "")} &nbsp;|&nbsp; 🧾 ضريبي: {info.get("tax", "")} &nbsp;|&nbsp; 🔑 ترخيص: {info.get("license", "")}</div>
                    <div class="comp-info-txt">📞 {info.get("contact", "")}</div>
                </div>
                <div>{logo_html}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

if not st.session_state.is_authenticated:
    st.markdown(
        f"""
        <div style="max-width: 480px; margin: 80px auto; background: rgba(30, 30, 30, 0.9); backdrop-filter: blur(20px); padding: 40px; border-radius: 20px; box-shadow: 0 20px 40px rgba(0,0,0,0.7); text-align: center; border: 1px solid rgba(255,255,255,0.08);">
            <h2 style="color: #F87171; margin-bottom: 15px; font-size: 22px;">🎬 تسجيل الدخول للمنصة</h2>
            <p style="color: #94A3B8; font-size: 13.5px; margin-bottom: 25px;">{company_display_name} | رخصة التشغيل: {company_license}</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    col_l1, col_l2, col_l3 = st.columns([1, 2, 1])
    with col_l2:
        with st.form("login_pattern_form"):
            usernames = st.session_state.users["اسم المستخدم"].tolist()
            selected_user_login = st.selectbox("اختر المستخدم", usernames)
            pattern_input = st.text_input("أدخل تسلسل الرسم السري", type="password", placeholder="مثل: 1-2-3")
            login_btn = st.form_submit_button("▶️ تشغيل النظام", use_container_width=True)
            
            if login_btn:
                user_record = st.session_state.users[st.session_state.users["اسم المستخدم"] == selected_user_login].iloc[0]
                if pattern_input.strip() == str(user_record["الرسم السري"]).strip():
                    st.session_state.is_authenticated = True
                    st.session_state.current_logged_user = selected_user_login
                    st.session_state.current_user_dept = user_record["القسم التابع"]
                    st.session_state.current_user_branch = user_record["الفرع التابع"]
                    st.session_state.current_user_role = user_record["الصلاحية"]
                    st.success("تم تسجيل الدخول بنجاح!")
                    st.rerun()
                else:
                    st.error("❌ الرسم السري غير صحيح!")
    st.stop()

# ---------------------------------------------------------
# 🎬 بار القوائم السينمائي العلوي المنسدل (أعلى الشاشة مثل مواقع الأفلام)
# ---------------------------------------------------------
render_company_header()

st.markdown('<div class="cinema-top-bar">', unsafe_allow_html=True)

cinema_menu_categories = {
    "🏠 الرئيسية": ["لوحة التحكم والمؤشرات"],
    "🔍 البحث المتقدم": ["بحث شامل في قواعد البيانات"],
    "⏱️ الحضور والانصراف": ["تسجيل حضور وانصراف", "سجل الحضور والانصراف", "تعديل أو حذف حركة حضور"],
    "💰 المعاملات المالية": ["تسجيل معاملة مالية", "سجل المعاملات المالية", "تعديل أو حذف معاملة مالية"],
    "📝 طلبات الإجازات": ["تسجيل طلب إجازة جديد", "سجل طلبات قيد الانتظار", "سجل الطلبات المقبولة", "سجل الطلبات المرفوضة", "تعديل أو حذف طلب إجازة"],
    "👥 شؤون الموظفين": ["إضافة موظف جديد", "سجل الموظفين والأرصدة", "تعديل أو حذف موظف"],
    "⚙️ الأدوات والنظام": ["إدارة المستخدمين والصلاحيات", "كشف الرواتب والمستحقات", "طباعة التقارير", "إعدادات الشركة", "تصدير وتحميل Excel", "نسخة احتياطية واستعادة", "مسح البيانات"]
}

col_nav1, col_nav2, col_nav3 = st.columns([1.5, 2.5, 1])
with col_nav1:
    selected_main_cat = st.selectbox("🎬 القسم الرئيسي:", list(cinema_menu_categories.keys()), label_visibility="collapsed")
with col_nav2:
    sub_options_list = cinema_menu_categories[selected_main_cat]
    choice = st.selectbox(f"🍿 العمليات والعروض:", sub_options_list, label_visibility="collapsed")
with col_nav3:
    if st.button("⏹️ خروج", use_container_width=True):
        st.session_state.is_authenticated = False
        st.session_state.current_logged_user = ""
        st.rerun()

st.markdown('</div>', unsafe_allow_html=True)

# ---------------------------------------------------------
# 🎯 بطاقات المؤشرات الأربعة السينمائية
# ---------------------------------------------------------
branch_filter = st.session_state.current_user_branch
dept_filter = st.session_state.current_user_dept

if "Admin" in st.session_state.current_user_role or "الإدارة العليا" in dept_filter:
    view_employees = st.session_state.employees
    view_requests = st.session_state.requests
else:
    view_employees = st.session_state.employees[st.session_state.employees["الفرع"] == branch_filter]
    view_requests = st.session_state.requests[st.session_state.requests["الفرع"] == branch_filter]

total_emps = len(view_employees)
pending_requests = view_requests[view_requests['الحالة'] == 'قيد الانتظار'] if not view_requests.empty else pd.DataFrame()
pending_count = len(pending_requests)
accepted_count = len(view_requests[view_requests['الحالة'] == 'مقبول']) if not view_requests.empty else 0

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown(f'<div class="glass-card"><div class="glass-card-title">👥 إجمالي نجوم الشركة</div><div class="glass-card-value">{total_emps}</div></div>', unsafe_allow_html=True)
with col2:
    st.markdown(f'<div class="glass-card" style="border-right-color: #F59E0B;"><div class="glass-card-title">⏳ عروض قيد الانتظار</div><div class="glass-card-value" style="color: #F59E0B;">{pending_count}</div></div>', unsafe_allow_html=True)
with col3:
    st.markdown(f'<div class="glass-card" style="border-right-color: #10B981;"><div class="glass-card-title">✅ العروض المقبولة</div><div class="glass-card-value" style="color: #10B981;">{accepted_count}</div></div>', unsafe_allow_html=True)
with col4:
    total_payroll_est = float(view_employees["الراتب الأساسي"].sum()) if not view_employees.empty and "الراتب الأساسي" in view_employees.columns else 0.0
    st.markdown(f'<div class="glass-card" style="border-right-color: #3B82F6;"><div class="glass-card-title">💰 إجمالي ميزانية الرواتب</div><div class="glass-card-value" style="font-size: 20px; color: #3B82F6;">{total_payroll_est:,.0f} ج.م</div></div>', unsafe_allow_html=True)

st.markdown("<hr style='border: 0.5px solid rgba(255,255,255,0.08); margin: 15px 0 25px 0;'>", unsafe_allow_html=True)

# =========================================================
# 🔍 صندوق البحث السينمائي
# =========================================================
if selected_main_cat == "🔍 البحث المتقدم" or choice == "بحث شامل في قواعد البيانات":
    st.markdown(f'<div class="section-header">🔍 محرك البحث السينمائي الشامل</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="entry-form-area">', unsafe_allow_html=True)
    with st.form("advanced_search_form"):
        col_s1, col_s2, col_s3 = st.columns(3)
        with col_s1:
            search_keyword = st.text_input("بحث نصي (الاسم، الوظيفة، أو الكود):")
        with col_s2:
            branches_avail = ["الكل"] + sorted(st.session_state.employees["الفرع"].dropna().unique().tolist()) if not st.session_state.employees.empty else ["الكل"]
            selected_search_branch = st.selectbox("تصفية حسب الفرع:", branches_avail)
        with col_s3:
            search_target_section = st.selectbox("نطاق البحث:", ["جميع السجلات (شامل)", "سجل الموظفين", "سجل الحضور", "سجل الإجازات", "سجل المعاملات المالية"])
            
        submit_adv_search = st.form_submit_button("🔍 ابدأ البحث", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
        
    keyword = search_keyword.strip().lower()
    if search_target_section in ["جميع السجلات (شامل)", "سجل الموظفين"]:
        st.markdown("##### 👥 نتائج البحث في (الموظفين):")
        emp_df = st.session_state.employees.copy()
        if selected_search_branch != "الكل": emp_df = emp_df[emp_df["الفرع"] == selected_search_branch]
        if keyword: emp_df = emp_df[emp_df.astype(str).apply(lambda x: x.str.lower().str.contains(keyword)).any(axis=1)]
        render_printable_table(emp_df)
        
    if search_target_section in ["جميع السجلات (شامل)", "سجل الحضور"]:
        st.markdown("##### ⏱️ نتائج البحث في (الحضور):")
        att_df = st.session_state.attendance.copy()
        if not att_df.empty:
            if selected_search_branch != "الكل": att_df = att_df[att_df["الفرع"] == selected_search_branch]
            if keyword: att_df = att_df[att_df.astype(str).apply(lambda x: x.str.lower().str.contains(keyword)).any(axis=1)]
        render_printable_table(att_df)

    if search_target_section in ["جميع السجلات (شامل)", "سجل الإجازات"]:
        st.markdown("##### 📝 نتائج البحث في (الإجازات):")
        req_df = st.session_state.requests.copy()
        if not req_df.empty:
            if selected_search_branch != "الكل": req_df = req_df[req_df["الفرع"] == selected_search_branch]
            if keyword: req_df = req_df[req_df.astype(str).apply(lambda x: x.str.lower().str.contains(keyword)).any(axis=1)]
        render_printable_table(req_df)

    if search_target_section in ["جميع السجلات (شامل)", "سجل المعاملات المالية"]:
        st.markdown("##### 💰 نتائج البحث في (الماليات):")
        fin_df = st.session_state.financial_transactions.copy()
        if not fin_df.empty:
            if selected_search_branch != "الكل": fin_df = fin_df[fin_df["الفرع"] == selected_search_branch]
            if keyword: fin_df = fin_df[fin_df.astype(str).apply(lambda x: x.str.lower().str.contains(keyword)).any(axis=1)]
        render_printable_table(fin_df)

# =========================================================
# 🏠 الشاشة الرئيسية
# =========================================================
elif choice == "لوحة التحكم والمؤشرات" or choice == "🏠 الرئيسية":
    if not pending_requests.empty:
        st.markdown(f'<div class="section-header">⏳ العروض المعلقة بانتظار الاعتماد ({pending_count})</div>', unsafe_allow_html=True)
        render_printable_table(pending_requests)
        
        st.markdown('<div class="entry-form-area">', unsafe_allow_html=True)
        col_dec1, col_dec2, col_dec3 = st.columns([2, 2, 2])
        with col_dec1:
            req_ids = pending_requests["رقم الطلب"].tolist()
            selected_req_id = st.selectbox("اختر رقم الطلب:", req_ids)
            
        selected_req = pending_requests[pending_requests["رقم الطلب"] == selected_req_id].iloc[0]
        emp_code_req = selected_req["كود الموظف"]
        days_req = selected_req["عدد الأيام"]
        type_req = selected_req["نوع الإجازة"]
        
        with col_dec2:
            st.write("")
            st.write("")
            if st.button("✅ قبول العرض وتأكيده", use_container_width=True):
                st.session_state.requests.loc[st.session_state.requests["رقم الطلب"] == selected_req_id, "الحالة"] = "مقبول"
                if "سنوية" in type_req:
                    st.session_state.employees.loc[st.session_state.employees["كود الموظف"] == emp_code_req, "سنوي مستهلك"] += days_req
                    st.session_state.employees.loc[st.session_state.employees["كود الموظف"] == emp_code_req, "سنوي متبقي"] -= days_req
                auto_save_data()
                st.success("تم قبول الطلب بنجاح!")
                st.rerun()

        with col_dec3:
            st.write("")
            st.write("")
            if st.button("❌ رفض الطلب", use_container_width=True):
                st.session_state.requests.loc[st.session_state.requests["رقم الطلب"] == selected_req_id, "الحالة"] = "مرفوض"
                auto_save_data()
                st.error("تم رفض الطلب.")
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown(f'<div class="section-header">📊 لوحة إحصائيات وأرصدة النجوم</div>', unsafe_allow_html=True)
    render_printable_table(view_employees)

# =========================================================
# الحضور والانصراف
# =========================================================
elif choice == "تسجيل حضور وانصراف":
    st.subheader("⏱️ تسجيل حضور / انصراف جديد")
    emp_names = st.session_state.employees["اسم الموظف"].tolist()
    if not emp_names:
        st.warning("لا توجد موظفون متاحون.")
    else:
        st.markdown('<div class="entry-form-area">', unsafe_allow_html=True)
        with st.form("att_form"):
            selected_emp = st.selectbox("الموظف", emp_names)
            att_date = st.date_input("التاريخ", value=date.today())
            att_status = st.selectbox("الحالة", ["حضور", "إجازة أسبوعية", "إجازة سنوية", "غياب", "مأمورية"])
            if st.form_submit_button("حفظ حركة الحضور", use_container_width=True):
                emp_data = st.session_state.employees[st.session_state.employees["اسم الموظف"] == selected_emp].iloc[0]
                new_att = {"التاريخ": str(att_date), "كود الموظف": emp_data["كود الموظف"], "اسم الموظف": selected_emp, "الفرع": emp_data["الفرع"], "بداية العمل الرسمية": "08:00 AM", "نهاية العمل الرسمية": "04:00 PM", "وقت الحضور الفعلي": "08:00 AM", "وقت الانصراف الفعلي": "04:00 PM", "الحالة": att_status, "التأخير الصباحي (دقيقة)": 0, "انصراف مبكر (دقيقة)": 0, "إضافي بعد العمل (دقيقة)": 0, "حضور مبكر (دقيقة)": 0, "خروج متأخر (دقيقة)": 0, "دقائق التأخير": 0}
                st.session_state.attendance = pd.concat([st.session_state.attendance, pd.DataFrame([new_att])], ignore_index=True)
                auto_save_data()
                st.success("تم الحفظ بنجاح!")
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

elif choice == "سجل الحضور والانصراف":
    col_t1, col_t2 = st.columns([3, 1])
    with col_t1: st.subheader("⏱️ سجل الحضور والانصراف العام")
    with col_t2: render_print_button()
    render_printable_table(st.session_state.attendance)

elif choice == "تعديل أو حذف حركة حضور":
    st.subheader("⏱️ تعديل أو حذف حركة حضور")
    if st.session_state.attendance.empty:
        st.info("لا توجد حركات مسجلة.")
    else:
        att_recs = [f"الموظف: {r['اسم الموظف']} | التاريخ: {r['التاريخ']}" for _, r in st.session_state.attendance.iterrows()]
        sel_att = st.selectbox("اختر الحركة:", att_recs)
        idx = att_recs.index(sel_att)
        if st.button("🗑️ حذف هذه الحركة نهائياً"):
            st.session_state.attendance = st.session_state.attendance.drop(index=idx).reset_index(drop=True)
            auto_save_data()
            st.success("تم الحذف بنجاح!")
            st.rerun()

# =========================================================
# المعاملات المالية
# =========================================================
elif choice == "تسجيل معاملة مالية":
    st.subheader("💰 تسجيل معاملة مالية جديدة")
    emp_names = st.session_state.employees["اسم الموظف"].tolist()
    if emp_names:
        st.markdown('<div class="entry-form-area">', unsafe_allow_html=True)
        with st.form("fin_form"):
            emp_f = st.selectbox("الموظف", emp_names)
            t_type = st.selectbox("نوع المعاملة", ["سلفة", "جزاء (خصم)", "مكافأة (إضافي)", "بدلات"])
            t_amt = st.number_input("المبلغ", min_value=0.0, value=100.0)
            t_reas = st.text_input("البيان / السبب")
            if st.form_submit_button("حفظ المعاملة المالية", use_container_width=True):
                emp_data = st.session_state.employees[st.session_state.employees["اسم الموظف"] == emp_f].iloc[0]
                new_f = {"التاريخ": str(date.today()), "كود الموظف": emp_data["كود الموظف"], "اسم الموظف": emp_f, "الفرع": emp_data["الفرع"], "النوع": t_type, "المبلغ / القيمة": t_amt, "البيان / السبب": t_reas}
                st.session_state.financial_transactions = pd.concat([st.session_state.financial_transactions, pd.DataFrame([new_f])], ignore_index=True)
                auto_save_data()
                st.success("تم الحفظ بنجاح!")
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

elif choice == "سجل المعاملات المالية":
    col_t1, col_t2 = st.columns([3, 1])
    with col_t1: st.subheader("💰 سجل المعاملات المالية")
    with col_t2: render_print_button()
    render_printable_table(st.session_state.financial_transactions)

elif choice == "تعديل أو حذف معاملة مالية":
    st.subheader("💰 تعديل أو حذف معاملة مالية")
    if st.session_state.financial_transactions.empty:
        st.info("لا توجد معاملات مسجلة.")
    else:
        fin_recs = [f"الموظف: {r['اسم الموظف']} | النوع: {r['النوع']} | المبلغ: {r['المبلغ / القيمة']}" for _, r in st.session_state.financial_transactions.iterrows()]
        sel_fin = st.selectbox("اختر المعاملة:", fin_recs)
        f_idx = fin_recs.index(sel_fin)
        if st.button("🗑️ حذف هذه المعاملة نهائياً"):
            st.session_state.financial_transactions = st.session_state.financial_transactions.drop(index=f_idx).reset_index(drop=True)
            auto_save_data()
            st.success("تم الحذف بنجاح!")
            st.rerun()

# =========================================================
# طلبات الإجازات
# =========================================================
elif choice == "تسجيل طلب إجازة جديد":
    st.subheader("📝 تقديم طلب إجازة جديد")
    emp_names = st.session_state.employees["اسم الموظف"].tolist()
    if emp_names:
        st.markdown('<div class="entry-form-area">', unsafe_allow_html=True)
        with st.form("req_form"):
            emp_r = st.selectbox("الموظف", emp_names)
            r_type = st.selectbox("نوع الإجازة", ["إجازة سنوية", "إجازة أسبوعية / عارضة", "إجازة مرضية"])
            col_d1, col_d2 = st.columns(2)
            with col_d1: d_from = st.date_input("من تاريخ")
            with col_d2: d_to = st.date_input("إلى تاريخ")
            r_reas = st.text_area("السبب")
            if st.form_submit_button("إرسال الطلب", use_container_width=True):
                days = (d_to - d_from).days + 1
                emp_data = st.session_state.employees[st.session_state.employees["اسم الموظف"] == emp_r].iloc[0]
                new_req = {"رقم الطلب": int(st.session_state.requests["رقم الطلب"].max() + 1) if not st.session_state.requests.empty else 101, "كود الموظف": emp_data["كود الموظف"], "اسم الموظف": emp_r, "الوظيفة": emp_data["الوظيفة"], "الفرع": emp_data["الفرع"], "نوع الإجازة": r_type, "من تاريخ": str(d_from), "إلى تاريخ": str(d_to), "عدد الأيام": days, "السبب": r_reas, "الحالة": "قيد الانتظار"}
                st.session_state.requests = pd.concat([st.session_state.requests, pd.DataFrame([new_req])], ignore_index=True)
                auto_save_data()
                st.success("تم إرسال الطلب بنجاح!")
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

elif choice == "سجل طلبات قيد الانتظار":
    col_t1, col_t2 = st.columns([3, 1])
    with col_t1: st.subheader("⏳ سجل الطلبات قيد الانتظار")
    with col_t2: render_print_button()
    render_printable_table(st.session_state.requests[st.session_state.requests["الحالة"] == "قيد الانتظار"] if not st.session_state.requests.empty else pd.DataFrame())

elif choice == "سجل الطلبات المقبولة":
    col_t1, col_t2 = st.columns([3, 1])
    with col_t1: st.subheader("✅ سجل الطلبات المقبولة")
    with col_t2: render_print_button()
    render_printable_table(st.session_state.requests[st.session_state.requests["الحالة"] == "مقبول"] if not st.session_state.requests.empty else pd.DataFrame())

elif choice == "سجل الطلبات المرفوضة":
    col_t1, col_t2 = st.columns([3, 1])
    with col_t1: st.subheader("❌ سجل الطلبات المرفوضة")
    with col_t2: render_print_button()
    render_printable_table(st.session_state.requests[st.session_state.requests["الحالة"] == "مرفوض"] if not st.session_state.requests.empty else pd.DataFrame())

elif choice == "تعديل أو حذف طلب إجازة":
    st.subheader("📝 تعديل أو حذف طلب إجازة")
    if st.session_state.requests.empty:
        st.info("لا توجد طلبات مسجلة.")
    else:
        req_recs = [f"طلب رقم #{r['رقم الطلب']} - {r['اسم الموظف']}" for _, r in st.session_state.requests.iterrows()]
        sel_req = st.selectbox("اختر الطلب:", req_recs)
        r_idx = req_recs.index(sel_req)
        if st.button("🗑️ حذف هذا الطلب نهائياً"):
            st.session_state.requests = st.session_state.requests.drop(index=r_idx).reset_index(drop=True)
            auto_save_data()
            st.success("تم الحذف بنجاح!")
            st.rerun()

# =========================================================
# شؤون الموظفين
# =========================================================
elif choice == "إضافة موظف جديد":
    st.subheader("👥 إضافة موظف جديد للمنصة")
    st.markdown('<div class="entry-form-area">', unsafe_allow_html=True)
    with st.form("new_emp"):
        c_code = st.text_input("كود الموظف")
        c_name = st.text_input("اسم الموظف")
        c_job = st.text_input("الوظيفة")
        c_dept = st.text_input("القسم")
        c_branch = st.text_input("الفرع")
        c_sal = st.number_input("الراتب الأساسي", min_value=0.0, value=5000.0)
        if st.form_submit_button("إضافة الموظف", use_container_width=True):
            new_e = {"كود الموظف": c_code, "اسم الموظف": c_name, "الوظيفة": c_job, "القسم": c_dept, "الفرع": c_branch, "صلاحية الموظف": "إدخال", "الراتب الأساسي": c_sal, "رصيد سنوي (إجمالي)": 21, "سنوي مستهلك": 0, "سنوي متبقي": 21, "رصيد أسبوعي (إجمالي)": 4, "أسبوعي مستهلك": 0, "أسبوعي متبقي": 4, "رصيد رسمي (إجمالي)": 10, "رسمي مستهلك": 0, "رسمي متبقي": 10, "إجازات مرضية (أيام)": 0}
            st.session_state.employees = pd.concat([st.session_state.employees, pd.DataFrame([new_e])], ignore_index=True)
            auto_save_data()
            st.success("تمت الإضافة بنجاح!")
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

elif choice == "سجل الموظفين والأرصدة":
    col_t1, col_t2 = st.columns([3, 1])
    with col_t1: st.subheader("👥 سجل الموظفين والأرصدة الشامل")
    with col_t2: render_print_button()
    render_printable_table(st.session_state.employees)

elif choice == "تعديل أو حذف موظف":
    st.subheader("👥 تعديل أو حذف موظف")
    if st.session_state.employees.empty:
        st.info("لا توجد موظفين مسجلين.")
    else:
        emp_recs = [f"{r['كود الموظف']} - {r['اسم الموظف']}" for _, r in st.session_state.employees.iterrows()]
        sel_e = st.selectbox("اختر الموظف:", emp_recs)
        e_idx = emp_recs.index(sel_e)
        if st.button("🗑️ حذف هذا الموظف نهائياً"):
            st.session_state.employees = st.session_state.employees.drop(index=e_idx).reset_index(drop=True)
            auto_save_data()
            st.success("تم الحذف بنجاح!")
            st.rerun()

# =========================================================
# الأدوات والنظام
# =========================================================
elif choice == "إدارة المستخدمين والصلاحيات":
    st.subheader("🔒 إدارة المستخدمين والصلاحيات")
    render_printable_table(st.session_state.users.drop(columns=["الرسم السري"], errors="ignore"))

elif choice == "كشف الرواتب والمستحقات":
    col_t1, col_t2 = st.columns([3, 1])
    with col_t1: st.subheader("💰 كشف الرواتب والمستحقات الشامل")
    with col_t2: render_print_button()
    render_printable_table(st.session_state.employees)

elif choice == "طباعة التقارير":
    col_t1, col_t2 = st.columns([3, 1])
    with col_t1: st.subheader("🖨️ طباعة التقارير العامة")
    with col_t2: render_print_button()
    render_printable_table(st.session_state.employees)

elif choice == "إعدادات الشركة":
    st.subheader("⚙️ إعدادات المنصة والشركة")
    info = st.session_state.company_info
    st.markdown('<div class="entry-form-area">', unsafe_allow_html=True)
    with st.form("settings"):
        cn = st.text_input("اسم الشركة", value=info.get("name", ""))
        car = st.text_input("السجل التجاري", value=info.get("cr", ""))
        ctax = st.text_input("الرقم الضريبي", value=info.get("tax", ""))
        ccontact = st.text_input("معلومات الاتصال", value=info.get("contact", ""))
        clic = st.text_input("رقم الترخيص", value=info.get("license", ""))
        if st.form_submit_button("حفظ التعديلات", use_container_width=True):
            info["name"] = cn
            info["cr"] = car
            info["tax"] = ctax
            info["contact"] = ccontact
            info["license"] = clic
            auto_save_data()
            st.success("تم التحديث بنجاح!")
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

elif choice == "تصدير وتحميل Excel":
    st.markdown('<div class="entry-form-area">', unsafe_allow_html=True)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        st.session_state.employees.to_excel(writer, sheet_name='الموظفين', index=False)
        st.session_state.requests.to_excel(writer, sheet_name='الإجازات', index=False)
        st.session_state.attendance.to_excel(writer, sheet_name='الحضور', index=False)
        st.session_state.financial_transactions.to_excel(writer, sheet_name='الماليات', index=False)
    output.seek(0)
    st.download_button("📥 تحميل ملف الإكسيل الآن", data=output, file_name="cinema_system_data.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    st.markdown('</div>', unsafe_allow_html=True)

elif choice == "نسخة احتياطية واستعادة":
    st.subheader("💾 النسخ الاحتياطي والاستعادة")
    st.markdown('<div class="entry-form-area">', unsafe_allow_html=True)
    backup_dict = {
        "employees": st.session_state.employees.to_dict(orient='records'),
        "requests": st.session_state.requests.to_dict(orient='records'),
        "attendance": st.session_state.attendance.to_dict(orient='records'),
        "financial_transactions": st.session_state.financial_transactions.to_dict(orient='records'),
        "users": st.session_state.users.to_dict(orient='records'),
        "company_info": st.session_state.company_info
    }
    st.download_button("💾 تحميل النسخة الاحتياطية (JSON)", data=json.dumps(backup_dict, ensure_ascii=False, indent=4), file_name="backup_cinema.json", mime="application/json")
    st.markdown('</div>', unsafe_allow_html=True)

elif choice == "مسح البيانات":
    st.subheader("🗑️ مسح وحذف كافة البيانات")
    st.markdown('<div class="entry-form-area">', unsafe_allow_html=True)
    conf = st.text_input("اكتب 'تأكيد الحذف' للتأكيد:")
    if conf == "تأكيد الحذف" and st.button("حذف كافة البيانات نهائياً", type="primary"):
        st.session_state.employees = pd.DataFrame(columns=["كود الموظف", "اسم الموظف", "الوظيفة", "القسم", "الفرع", "صلاحية الموظف", "الراتب الأساسي", "رصيد سنوي (إجمالي)", "سنوي مستهلك", "سنوي متبقي", "رصيد أسبوعي (إجمالي)", "أسبوعي مستهلك", "أسبوعي متبقي", "رصيد رسمي (إجمالي)", "رسمي مستهلك", "رسمي متبقي", "إجازات مرضية (أيام)"])
        st.session_state.requests = pd.DataFrame(columns=["رقم الطلب", "كود الموظف", "اسم الموظف", "الوظيفة", "الفرع", "نوع الإجازة", "من تاريخ", "إلى تاريخ", "عدد الأيام", "السبب", "الحالة"])
        st.session_state.attendance = pd.DataFrame(columns=["التاريخ", "كود الموظف", "اسم الموظف", "الفرع", "بداية العمل الرسمية", "نهاية العمل الرسمية", "وقت الحضور الفعلي", "وقت الانصراف الفعلي", "الحالة", "التأخير الصباحي (دقيقة)", "انصراف مبكر (دقيقة)", "إضافي بعد العمل (دقيقة)", "حضور مبكر (دقيقة)", "خروج متأخر (دقيقة)", "دقائق التأخير"])
        st.session_state.financial_transactions = pd.DataFrame(columns=["التاريخ", "كود الموظف", "اسم الموظف", "الفرع", "النوع", "المبلغ / القيمة", "البيان / السبب"])
        auto_save_data()
        st.success("تم مسح كافة البيانات بنجاح!")
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)