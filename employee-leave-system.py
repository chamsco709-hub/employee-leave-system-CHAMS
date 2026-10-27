import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
from datetime import datetime, date
import json
import os
import io

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
            ">
                🖨️ طباعة السجل الحالي بشكل نظيف
            </button>
        </div>
    """, height=50)

# 🎨 تصميم CSS السينمائي الداكن وتثبيت القائمة العلوية تماماً (Sticky / Fixed Menu)
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
        padding-left: 2rem !important;
        padding-right: 2rem !important;
        max-width: 100% !important;
        background: linear-gradient(135deg, #121212 0%, #1A1A1A 50%, #0B0B0B 100%) !important;
        min-height: 100vh;
    }
    
    /* 📌 القائمة المثبتة علوياً وتتحرك مع التمرير */
    .sticky-top-wrapper {
        position: sticky;
        top: 0rem;
        z-index: 99999;
        background: rgba(18, 18, 18, 0.96);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        padding-top: 10px;
        padding-bottom: 10px;
        margin-bottom: 20px;
        border-bottom: 2.5px solid #E50914;
        box-shadow: 0 15px 35px rgba(0,0,0,0.7);
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
        border: 1px solid rgba(255, 255, 255, 0.08);
        color: #FFFFFF !important;
        padding: 12px 18px;
        border-radius: 14px;
        width: 100%;
        margin-bottom: 6px;
    }
    .header-top-system h2 {
        font-size: 14px !important;
        font-weight: bold !important;
        color: #F87171 !important;
        margin: 0 !important;
        text-align: center;
    }
    .comp-name-txt {
        font-size: 15px !important;
        font-weight: bold !important;
        color: #FFFFFF !important;
    }
    .comp-info-txt {
        font-size: 11px !important;
        color: #94A3B8 !important;
    }
    
    .user-badge-box {
        background: rgba(229, 9, 20, 0.15);
        border: 1px solid rgba(229, 9, 20, 0.4);
        padding: 5px 10px;
        border-radius: 8px;
        font-size: 11.5px;
        color: #FCA5A5;
        font-weight: bold;
        text-align: center;
        margin-bottom: 6px;
    }
    
    .glass-card {
        background: rgba(30, 30, 30, 0.75);
        backdrop-filter: blur(15px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-right: 6px solid #E50914;
        padding: 18px 20px;
        border-radius: 16px;
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.4);
        text-align: right !important;
        margin-bottom: 15px;
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
    }
    
    table.custom-table {
        width: 100%;
        border-collapse: separate;
        border-spacing: 0;
        margin-top: 10px !important;
        margin-bottom: 20px !important;
        background-color: rgba(24, 24, 24, 0.9);
        color: #FFFFFF;
        border-radius: 14px;
        overflow: hidden;
        border: 1px solid rgba(255, 255, 255, 0.08);
    }
    table.custom-table th, table.custom-table td {
        border-bottom: 1px solid #333333;
        padding: 12px 16px;
        text-align: right !important;
        font-size: 13px;
        color: #E2E8F0 !important;
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
    
    /* 🖨️ إعدادات الطباعة النظيفة */
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
        button, .stButton, iframe, div[data-testid="stHeader"], .no-print, .entry-form-area, hr, .cinema-top-bar { 
            display: none !important; 
        }
        .sticky-top-wrapper {
            position: relative !important;
            background: #FFFFFF !important;
            box-shadow: none !important;
            border-bottom: 2px solid #000000 !important;
        }
        .glass-header, .user-badge-box { 
            background: #FFFFFF !important; 
            border: 1px solid #000000 !important; 
            color: #000000 !important;
            box-shadow: none !important;
        }
        .header-top-system h2, .comp-name-txt, .comp-info-txt, .user-badge-box {
            color: #000000 !important;
        }
        table.custom-table { 
            width: 100% !important; 
            border: 1px solid #000000 !important; 
            background-color: #FFFFFF !important;
            color: #000000 !important;
        }
        table.custom-table th { 
            background-color: #E2E8F0 !important; 
            color: #000000 !important; 
            border-bottom: 2px solid #000000 !important;
        }
        table.custom-table td {
            color: #000000 !important;
            border-bottom: 1px solid #CBD5E1 !important;
        }
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
    st.markdown(
        f"""
        <div class="glass-header">
            <div class="header-top-system">
                <h2>🍿 منصة عرض شؤون الموظفين والإدارة &nbsp;|&nbsp; شركة: {info.get("name", "")}</h2>
            </div>
            <div>
                <div class="comp-name-txt">{info.get("name", "")}</div>
                <div class="comp-info-txt">📍 {info.get("address", "")} &nbsp;|&nbsp; 📋 سجل تجاري: {info.get("cr", "")} &nbsp;|&nbsp; 🔑 ترخيص: {info.get("license", "")}</div>
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
            if st.form_submit_button("▶️ تشغيل النظام", use_container_width=True):
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
# 📌 الحاوية المثبتة العلوية (Sticky Top Menu)
# ---------------------------------------------------------
st.markdown('<div class="sticky-top-wrapper">', unsafe_allow_html=True)

# 1. هيدر الشركة
render_company_header()

# 2. بيانات المستخدم الحالي
logged_username = st.session_state.current_logged_user
user_role = st.session_state.current_user_role
user_branch = st.session_state.current_user_branch
user_dept = st.session_state.current_user_dept

st.markdown(
    f"""
    <div class="user-badge-box">
        👤 المستخدم الحالي: <b>{logged_username}</b> &nbsp;|&nbsp; 🛡️ الصلاحية: <b>{user_role}</b> &nbsp;|&nbsp; 📍 الفرع: <b>{user_branch}</b> &nbsp;|&nbsp; 🏢 القسم: <b>{user_dept}</b>
    </div>
    """,
    unsafe_allow_html=True
)

# 3. الأزرار والخانات المنسدلة للتحكم والتنقل
st.markdown('<div class="cinema-top-bar" style="margin: 0; box-shadow: none;">', unsafe_allow_html=True)
col_nav1, col_nav2, col_nav3 = st.columns([1.5, 2.5, 1])

with col_nav1:
    selected_main_cat = st.selectbox("📂 القسم الرئيسي:", [
        "الرئيسية", 
        "الحضور والانصراف", 
        "طلبات الاجازة", 
        "المعاملات المالية", 
        "كشف الرواتب", 
        "شؤون الموظفين", 
        "المستخدمين", 
        "التقارير", 
        "اعدادات الشركة", 
        "أدوات النظام"
    ], label_visibility="collapsed")

sub_options_map = {
    "الرئيسية": ,
    "الحضور والانصراف": ["تسجيل حضور وانصراف", "سجل الحضور والانصراف", "تعديل أو حذف حركة حضور"],
    "طلبات الاجازة": ["تسجيل طلب إجازة", "سجل طلبات قيد الانتظار", "سجل الطلبات المقبولة", "سجل الطلبات المرفوضة", "تعديل أو حذف طلب إجازة"],
    "المعاملات المالية": ["تسجيل معاملة مالية", "سجل المعاملات المالية", "تعديل أو حذف معاملة مالية"],
    "كشف الرواتب": ["كشف الرواتب والمستحقات الشامل"],
    "شؤون الموظفين": ["إضافة موظف جديد", "سجل الموظفين والأرصدة", "تعديل أو حذف موظف"],
    "المستخدمين": ["إدارة المستخدمين والصلاحيات"],
    "التقارير": ["طباعة التقارير العامة"],
    "اعدادات الشركة": ,
    "أدوات النظام": ["تصدير وتحميل Excel", "نسخة احتياطية واستعادة", "مسح البيانات"]
}

with col_nav2:
    sub_options_list = sub_options_map.get(selected_main_cat, ["لوحة التحكم والمؤشرات"])
    choice = st.selectbox("📑 العمليات الفرعية (بوتون منسدل):", sub_options_list, label_visibility="collapsed")

with col_nav3:
    if st.button("⏹️ خروج", use_container_width=True):
        st.session_state.is_authenticated = False
        st.session_state.current_logged_user = ""
        st.rerun()

st.markdown('</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# ---------------------------------------------------------
# 🎯 بطاقات المؤشرات الأربعة المتجاورة
# ---------------------------------------------------------
if "Admin" in user_role or "الإدارة العليا" in user_dept:
    view_employees = st.session_state.employees
    view_requests = st.session_state.requests
else:
    view_employees = st.session_state.employees[st.session_state.employees["الفرع"] == user_branch]
    view_requests = st.session_state.requests[st.session_state.requests["الفرع"] == user_branch]

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
# منطق عرض الشاشات والأقسام حسب الاختيار المنسدل
# =========================================================
if selected_main_cat == "الرئيسية" or choice == "لوحة التحكم والمؤشرات":
    st.markdown(f'<div class="section-header">📊 لوحة إحصائيات وأرصدة الموظفين</div>', unsafe_allow_html=True)
    render_printable_table(view_employees)

elif choice == "تسجيل حضور وانصراف":
    st.subheader("⏱️ 1. تسجيل حركة حضور / انصراف جديدة")
    
    emp_names = st.session_state.employees["اسم الموظف"].tolist()
    if not emp_names:
        st.warning("لا توجد موظفون متاحون.")
    else:
        with st.form("attendance_record_form"):
            col_f1, col_f2, col_f3 = st.columns([2, 2, 2])
            with col_f1:
                selected_emp = st.selectbox("اختر الموظف", emp_names)
                emp_data = st.session_state.employees[st.session_state.employees["اسم الموظف"] == selected_emp].iloc[0]
            with col_f2:
                att_date = st.date_input("تاريخ اليوم", value=date.today())
            with col_f3:
                att_status = st.selectbox("حالة اليوم", [
                    "حضور", "إجازة أسبوعية", "إجازة سنوية", "إجازة مرضية", "غياب", "إجازة رسمية", "مأمورية"
                ])
                
            st.markdown("##### ⏰ مواعيد العمل الرسمية والفعلية:")
            col_w1, col_w2 = st.columns(2)
            with col_w1:
                t_official_start, t_official_start_str = select_time_12h("بداية العمل الرسمية", "att_start_r", default_hour=8, default_minute=0, default_period="صباحاً (AM)")
            with col_w2:
                t_official_end, t_official_end_str = select_time_12h("نهاية العمل الرسمية", "att_end_r", default_hour=4, default_minute=0, default_period="مساءً (PM)")

            t_in_str, t_out_str = "-", "-"
            if att_status == "حضور":
                col_act1, col_act2 = st.columns(2)
                with col_act1:
                    t_in, t_in_str = select_time_12h("وقت الحضور الفعلي", "att_in_f", default_hour=8, default_minute=0, default_period="صباحاً (AM)")
                with col_act2:
                    t_out, t_out_str = select_time_12h("وقت الانصراف الفعلي", "att_out_f", default_hour=4, default_minute=0, default_period="مساءً (PM)")
            else:
                st.info(f"💡 الحالة الحالية: ({att_status})")

            grace_period = st.number_input("فترة السماح (بالدقائق)", min_value=0, value=15, step=1)
            
            submit_att = st.form_submit_button("💾 حفظ الحركة واحتساب الحسابات بدقة", use_container_width=True)
            
            if submit_att:
                emp_code = emp_data["كود الموظف"]
                emp_branch = emp_data["الفرع"]
                
                morning_delay = 0
                early_leave = 0
                overtime_after = 0
                early_arrival = 0
                late_departure = 0
                
                if att_status == "حضور":
                    dt_in = datetime.combine(att_date, t_in)
                    dt_official_start = datetime.combine(att_date, t_official_start)
                    dt_official_start_with_grace = dt_official_start + timedelta(minutes=grace_period)
                    
                    if dt_in > dt_official_start_with_grace:
                        morning_delay = int((dt_in - dt_official_start).total_seconds() / 60)
                    elif dt_in < dt_official_start:
                        early_arrival = int((dt_official_start - dt_in).total_seconds() / 60)
                        
                    dt_out = datetime.combine(att_date, t_out)
                    dt_official_end = datetime.combine(att_date, t_official_end)
                    
                    if dt_out < dt_official_end:
                        early_leave = int((dt_official_end - dt_out).total_seconds() / 60)
                    elif dt_out > dt_official_end:
                        late_departure = int((dt_out - dt_official_end).total_seconds() / 60)
                        overtime_after = late_departure
                
                if att_status == "إجازة سنوية":
                    st.session_state.employees.loc[st.session_state.employees["كود الموظف"] == emp_code, "سنوي مستهلك"] += 1
                    st.session_state.employees.loc[st.session_state.employees["كود الموظف"] == emp_code, "سنوي متبقي"] -= 1
                elif att_status == "إجازة أسبوعية":
                    st.session_state.employees.loc[st.session_state.employees["كود الموظف"] == emp_code, "أسبوعي مستهلك"] += 1
                    st.session_state.employees.loc[st.session_state.employees["كود الموظف"] == emp_code, "أسبوعي متبقي"] -= 1
                elif att_status == "إجازة مرضية":
                    if "إجازات مرضية (أيام)" in st.session_state.employees.columns:
                        st.session_state.employees.loc[st.session_state.employees["كود الموظف"] == emp_code, "إجازات مرضية (أيام)"] += 1
                
                new_att = {
                    "التاريخ": str(att_date),
                    "كود الموظف": emp_code,
                    "اسم الموظف": selected_emp,
                    "الفرع": emp_branch,
                    "بداية العمل الرسمية": t_official_start_str,
                    "نهاية العمل الرسمية": t_official_end_str,
                    "وقت الحضور الفعلي": t_in_str,
                    "وقت الانصراف الفعلي": t_out_str,
                    "الحالة": att_status,
                    "التأخير الصباحي (دقيقة)": morning_delay,
                    "انصراف مبكر (دقيقة)": early_leave,
                    "إضافي بعد العمل (دقيقة)": overtime_after,
                    "حضور مبكر (دقيقة)": early_arrival,
                    "خروج متأخر (دقيقة)": late_departure,
                    "دقائق التأخير": morning_delay
                }
                
                st.session_state.attendance = pd.concat([st.session_state.attendance, pd.DataFrame([new_att])], ignore_index=True)
                auto_save_data()
                st.success("تم تسجيل حركة الحضور والانصراف وحساب كافة الأوقات بالدقيقة بنجاح!")
                st.rerun()

# =========================================================
# ⏱️ 2. سجل الحضور والانصراف
# =========================================================
elif choice == "سجل الحضور والانصراف":
    col_t1, col_t2 = st.columns([3, 1])
    with col_t1: st.subheader("⏱️ 2. سجل الحضور والانصراف العام")
    with col_t2: render_print_button()
    
    st.markdown('<div class="entry-form-area">', unsafe_allow_html=True)
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        search_emp_att = st.selectbox("بحث سريع حسب الموظف:", ["الكل"] + sorted(st.session_state.attendance["اسم الموظف"].dropna().unique().tolist()) if not st.session_state.attendance.empty else ["الكل"])
    with col_s2:
        search_branch_att = st.selectbox("بحث سريع حسب الفرع:", ["الكل"] + sorted(st.session_state.attendance["الفرع"].dropna().unique().tolist()) if not st.session_state.attendance.empty else ["الكل"])
    st.markdown('</div>', unsafe_allow_html=True)
    
    filtered_att = st.session_state.attendance.copy()
    if not filtered_att.empty:
        if search_emp_att != "الكل":
            filtered_att = filtered_att[filtered_att["اسم الموظف"] == search_emp_att]
        if search_branch_att != "الكل":
            filtered_att = filtered_att[filtered_att["الفرع"] == search_branch_att]
            
    render_printable_table(filtered_att)

# =========================================================
# ⏱️ 3. تعديل أو حذف حركة حضور
# =========================================================
elif choice == "تعديل أو حذف حركة حضور":
    st.subheader("⏱️ 3. تعديل أو حذف حركة تسجيل حضور وانصراف")
    
    if st.session_state.attendance.empty:
        st.info("لا توجد حركات حضور مسجلة حالياً.")
    else:
        att_records = [f"الموظف: {row['اسم الموظف']} | التاريخ: {row['التاريخ']} | الحالة: {row['الحالة']}" for _, row in st.session_state.attendance.iterrows()]
        selected_att_label = st.selectbox("اختر الحركة المراد تعديلها أو حذفها:", att_records)
        selected_att_idx = att_records.index(selected_att_label)
        
        row_to_edit = st.session_state.attendance.loc[selected_att_idx]
        
        with st.form("edit_attendance_full_form"):
            st.markdown(f"**تعديل تفاصيل حركة الحضور للموظف: {row_to_edit['اسم الموظف']} (بتاريخ {row_to_edit['التاريخ']})**")
            
            ed_emp = st.text_input("اسم الموظف", value=str(row_to_edit["اسم الموظف"]))
            ed_date = st.text_input("التاريخ", value=str(row_to_edit["التاريخ"]))
            
            status_options = ["حضور", "إجازة أسبوعية", "إجازة سنوية", "إجازة مرضية", "غياب", "إجازة رسمية", "مأمورية"]
            current_st_idx = status_options.index(row_to_edit["الحالة"]) if row_to_edit["الحالة"] in status_options else 0
            ed_status = st.selectbox("حالة اليوم", status_options, index=current_st_idx)
            
            col_e1, col_e2 = st.columns(2)
            with col_e1:
                ed_start_r = st.text_input("بداية العمل الرسمية", value=str(row_to_edit["بداية العمل الرسمية"]))
                ed_in_f = st.text_input("وقت الحضور الفعلي", value=str(row_to_edit["وقت الحضور الفعلي"]))
            with col_e2:
                ed_end_r = st.text_input("نهاية العمل الرسمية", value=str(row_to_edit["نهاية العمل الرسمية"]))
                ed_out_f = st.text_input("وقت الانصراف الفعلي", value=str(row_to_edit["وقت الانصراف الفعلي"]))
            
            ed_morning_delay = st.number_input("التأخير الصباحي (دقيقة)", min_value=0, value=int(row_to_edit.get("التأخير الصباحي (دقيقة)", 0)))
            ed_early_leave = st.number_input("انصراف مبكر (دقيقة)", min_value=0, value=int(row_to_edit.get("انصراف مبكر (دقيقة)", 0)))
            ed_overtime = st.number_input("إضافي بعد العمل (دقيقة)", min_value=0, value=int(row_to_edit.get("إضافي بعد العمل (دقيقة)", 0)))
            
            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                submit_edit_att = st.form_submit_button("💾 حفظ التعديلات", use_container_width=True)
            with col_btn2:
                submit_del_att = st.form_submit_button("🗑️ حذف الحركة نهائياً", use_container_width=True)
                
            if submit_edit_att:
                st.session_state.attendance.loc[selected_att_idx, "اسم الموظف"] = ed_emp
                st.session_state.attendance.loc[selected_att_idx, "التاريخ"] = ed_date
                st.session_state.attendance.loc[selected_att_idx, "الحالة"] = ed_status
                st.session_state.attendance.loc[selected_att_idx, "بداية العمل الرسمية"] = ed_start_r
                st.session_state.attendance.loc[selected_att_idx, "نهاية العمل الرسمية"] = ed_end_r
                st.session_state.attendance.loc[selected_att_idx, "وقت الحضور الفعلي"] = ed_in_f
                st.session_state.attendance.loc[selected_att_idx, "وقت الانصراف الفعلي"] = ed_out_f
                st.session_state.attendance.loc[selected_att_idx, "التأخير الصباحي (دقيقة)"] = ed_morning_delay
                st.session_state.attendance.loc[selected_att_idx, "انصراف مبكر (دقيقة)"] = ed_early_leave
                st.session_state.attendance.loc[selected_att_idx, "إضافي بعد العمل (دقيقة)"] = ed_overtime
                auto_save_data()
                st.success("تم تعديل تفاصيل حركة الحضور بنجاح!")
                st.rerun()
            elif submit_del_att:
                st.session_state.attendance = st.session_state.attendance.drop(index=selected_att_idx).reset_index(drop=True)
                auto_save_data()
                st.error("تم حذف الحركة بنجاح!")
                st.rerun()

elif choice == "تسجيل طلب إجازة جديد":
    st.subheader(f"📝 1. تقديم طلب إجازة جديد - {company_display_name}")
    
    emp_list = st.session_state.employees["اسم الموظف"].dropna().astype(str).tolist()
    
    if not emp_list:
        st.warning("لا توجد موظفون متاحون لتسجيل إجازة لهم.")
    else:
        with st.form("leave_form"):
            emp_name = st.selectbox("اسم الموظف", emp_list)
            leave_type = st.selectbox("نوع الإجازة", [
                "إجازة سنوية (Annual)", "إجازة أسبوعية / عارضة", "إجازة مرضية (Sick Leave)", "إجازة رسمية", "بدون أجر"
            ])
            col_d1, col_d2 = st.columns(2)
            with col_d1: start_date = st.date_input("من تاريخ")
            with col_d2: end_date = st.date_input("إلى تاريخ")
            reason = st.text_area("سبب الإجازة / ملاحظات إضافية")
            submit_leave = st.form_submit_button("إرسال طلب الإجازة للمراجعة")
            
            if submit_leave:
                days = (end_date - start_date).days + 1
                if days <= 0:
                    st.error("خطأ: تاريخ النهاية يجب أن يكون بعد تاريخ البداية!")
                else:
                    emp_row = st.session_state.employees[st.session_state.employees["اسم الموظف"] == emp_name].iloc[0]
                    emp_code = emp_row["كود الموظف"]
                    emp_job = emp_row["الوظيفة"]
                    emp_branch = emp_row["الفرع"]
                    
                    new_req = {
                        "رقم الطلب": int(st.session_state.requests["رقم الطلب"].max() + 1) if not st.session_state.requests.empty else 101,
                        "كود الموظف": emp_code, "اسم الموظف": emp_name, "الوظيفة": emp_job, "الفرع": emp_branch,
                        "نوع الإجازة": leave_type, "من تاريخ": str(start_date), "إلى تاريخ": str(end_date), "عدد الأيام": days, "السبب": reason, "الحالة": "قيد الانتظار"
                    }
                    st.session_state.requests = pd.concat([st.session_state.requests, pd.DataFrame([new_req])], ignore_index=True)
                    auto_save_data()
                    st.success("تم تقديم طلب الإجازة وحفظه تلقائياً في ملف الشركة!")

# =========================================================
# 📝 2. سجل طلبات قيد الانتظار
# =========================================================
elif choice == "سجل طلبات قيد الانتظار":
    col_t1, col_t2 = st.columns([3, 1])
    with col_t1: st.subheader("⏳ 2. سجل طلبات الإجازات قيد الانتظار")
    with col_t2: render_print_button()
    
    pending_df = st.session_state.requests[st.session_state.requests["الحالة"] == "قيد الانتظار"] if not st.session_state.requests.empty else pd.DataFrame()
    render_printable_table(pending_df)

# =========================================================
# 📝 3. سجل الطلبات المقبولة
# =========================================================
elif choice == "سجل الطلبات المقبولة":
    col_t1, col_t2 = st.columns([3, 1])
    with col_t1: st.subheader("✅ 3. سجل طلبات الإجازات المقبولة")
    with col_t2: render_print_button()
    
    accepted_df = st.session_state.requests[st.session_state.requests["الحالة"] == "مقبول"] if not st.session_state.requests.empty else pd.DataFrame()
    render_printable_table(accepted_df)

# =========================================================
# 📝 4. سجل الطلبات المرفوضة
# =========================================================
elif choice == "سجل الطلبات المرفوضة":
    col_t1, col_t2 = st.columns([3, 1])
    with col_t1: st.subheader("❌ 4. سجل طلبات الإجازات المرفوضة")
    with col_t2: render_print_button()
    
    rejected_df = st.session_state.requests[st.session_state.requests["الحالة"] == "مرفوض"] if not st.session_state.requests.empty else pd.DataFrame()
    render_printable_table(rejected_df)

# =========================================================
# 📝 5. تعديل أو حذف طلب إجازة
# =========================================================
elif choice == "تعديل أو حذف طلب إجازة":
    st.subheader("📝 5. تعديل أو حذف طلب إجازة")
    
    if st.session_state.requests.empty:
        st.info("لا توجد طلبات إجازات مسجلة.")
    else:
        req_records = [f"طلب رقم #{row['رقم الطلب']} - الموظف: {row['اسم الموظف']} ({row['نوع الإجازة']}) - الحالة: {row['الحالة']}" for _, row in st.session_state.requests.iterrows()]
        selected_req_label = st.selectbox("اختر الطلب المراد تعديله أو حذفه:", req_records)
        selected_req_idx = req_records.index(selected_req_label)
        
        req_to_edit = st.session_state.requests.loc[selected_req_idx]
        
        with st.form("edit_req_form"):
            st.markdown(f"**تعديل طلب الإجازة رقم #{req_to_edit['رقم الطلب']} للموظف: {req_to_edit['اسم الموظف']}**")
            
            ed_req_emp = st.text_input("اسم الموظف", value=str(req_to_edit["اسم الموظف"]))
            ed_req_branch = st.text_input("الفرع", value=str(req_to_edit["الفرع"]))
            ed_req_type = st.text_input("نوع الإجازة", value=str(req_to_edit["نوع الإجازة"]))
            
            status_list = ["قيد الانتظار", "مقبول", "مرفوض"]
            current_st_idx = status_list.index(req_to_edit["الحالة"]) if req_to_edit["الحالة"] in status_list else 0
            ed_req_status = st.selectbox("حالة الطلب", status_list, index=current_st_idx)
            
            ed_req_from = st.text_input("من تاريخ", value=str(req_to_edit["من تاريخ"]))
            ed_req_to = st.text_input("إلى تاريخ", value=str(req_to_edit["إلى تاريخ"]))
            ed_req_days = st.number_input("عدد الأيام", min_value=1, value=int(req_to_edit["عدد الأيام"]))
            ed_req_reason = st.text_area("سبب الإجازة", value=str(req_to_edit.get("السبب", "")))
            
            col_r1, col_r2 = st.columns(2)
            with col_r1:
                submit_edit_req = st.form_submit_button("💾 حفظ تعديل الطلب", use_container_width=True)
            with col_r2:
                submit_del_req = st.form_submit_button("🗑️ حذف طلب الإجازة", use_container_width=True)
                
            if submit_edit_req:
                st.session_state.requests.loc[selected_req_idx, "اسم الموظف"] = ed_req_emp
                st.session_state.requests.loc[selected_req_idx, "الفرع"] = ed_req_branch
                st.session_state.requests.loc[selected_req_idx, "نوع الإجازة"] = ed_req_type
                st.session_state.requests.loc[selected_req_idx, "الحالة"] = ed_req_status
                st.session_state.requests.loc[selected_req_idx, "من تاريخ"] = ed_req_from
                st.session_state.requests.loc[selected_req_idx, "إلى تاريخ"] = ed_req_to
                st.session_state.requests.loc[selected_req_idx, "عدد الأيام"] = ed_req_days
                st.session_state.requests.loc[selected_req_idx, "سبب الإجازة"] = ed_req_reason
                auto_save_data()
                st.success("تم تعديل طلب الإجازة بنجاح!")
                st.rerun()
            elif submit_del_req:
                st.session_state.requests = st.session_state.requests.drop(index=selected_req_idx).reset_index(drop=True)
                auto_save_data()
                st.error("تم حذف طلب الإجازة بنجاح!")
                st.rerun()

elif choice == "تسجيل معاملة مالية":
    st.subheader("💰 1. إضافة معاملة مالية جديدة (سلفة / جزاء / مكافأة / بدلات / إضافي)")
    
    emp_names = st.session_state.employees["اسم الموظف"].tolist()
    if not emp_names:
        st.warning("لا توجد موظفون مسجلون.")
    else:
        with st.form("financial_transaction_form"):
            col_m1, col_m2, col_m3 = st.columns([2, 2, 2])
            with col_m1:
                selected_emp_f = st.selectbox("اختر الموظف للمعاملة", emp_names)
            with col_m2:
                trans_type = st.selectbox("نوع المعاملة", [
                    "سلفة", 
                    "جزاء (خصم)", 
                    "مكافأة (إضافي)", 
                    "بدلات (إضافي مستحق)", 
                    "إضافي (ساعات عمل إضافية)"
                ])
            with col_m3:
                trans_date = st.date_input("تاريخ المعاملة المالية", value=date.today())
                
            col_m4, col_m5 = st.columns([2, 4])
            with col_m4:
                amount = st.number_input("المبلغ / القيمة (جنيه)", min_value=0.0, value=100.0, step=50.0)
            with col_m5:
                reason = st.text_input("البيان / السبب التفصيلي للمعاملة")
                
            submit_fin = st.form_submit_button("💾 حفظ المعاملة المالية وتحديث الحسابات", use_container_width=True)
            
            if submit_fin:
                emp_data = st.session_state.employees[st.session_state.employees["اسم الموظف"] == selected_emp_f].iloc[0]
                emp_code = emp_data["كود الموظف"]
                emp_branch = emp_data["الفرع"]
                
                new_trans = {
                    "التاريخ": str(trans_date),
                    "كود الموظف": emp_code,
                    "اسم الموظف": selected_emp_f,
                    "الفرع": emp_branch,
                    "النوع": trans_type,
                    "المبلغ / القيمة": amount,
                    "البيان / السبب": reason
                }
                
                st.session_state.financial_transactions = pd.concat([st.session_state.financial_transactions, pd.DataFrame([new_trans])], ignore_index=True)
                auto_save_data()
                st.success("تم تسجيل المعاملة المالية بنجاح!")
                st.rerun()

# =========================================================
# 💰 2. سجل المعاملات المالية
# =========================================================
elif choice == "سجل المعاملات المالية":
    col_t1, col_t2 = st.columns([3, 1])
    with col_t1: st.subheader("💰 2. سجل المعاملات المالية والسلف العام")
    with col_t2: render_print_button()
    
    render_printable_table(st.session_state.financial_transactions)

# =========================================================
# 💰 3. تعديل أو حذف معاملة مالية
# =========================================================
elif choice == "تعديل أو حذف معاملة مالية":
    st.subheader("💰 3. تعديل أو حذف معاملة مالية (سلفة / جزاء / مكافأة / بدلات / إضافي)")
    
    if st.session_state.financial_transactions.empty:
        st.info("لا توجد معاملات مالية مسجلة.")
    else:
        fin_records = [f"الموظف: {row['اسم الموظف']} | النوع: {row['النوع']} | المبلغ: {row['المبلغ / القيمة']} | التاريخ: {row['التاريخ']}" for _, row in st.session_state.financial_transactions.iterrows()]
        selected_fin_label = st.selectbox("اختر المعاملة المراد تعديلها أو حذفها:", fin_records)
        selected_fin_idx = fin_records.index(selected_fin_label)
        
        fin_to_edit = st.session_state.financial_transactions.loc[selected_fin_idx]
        
        with st.form("edit_fin_form"):
            st.markdown(f"**تعديل المعاملة المالية للموظف: {fin_to_edit['اسم الموظف']}**")
            ed_f_emp = st.text_input("اسم الموظف", value=str(fin_to_edit["اسم الموظف"]))
            
            fin_types = ["سلفة", "جزاء (خصم)", "مكافأة (إضافي)", "بدلات (إضافي مستحق)", "إضافي (ساعات عمل إضافية)"]
            current_f_idx = fin_types.index(fin_to_edit["النوع"]) if fin_to_edit["النوع"] in fin_types else 0
            ed_f_type = st.selectbox("نوع المعاملة", fin_types, index=current_f_idx)
            
            ed_f_amt = st.number_input("المبلغ / القيمة", min_value=0.0, value=float(fin_to_edit["المبلغ / القيمة"]))
            ed_f_reason = st.text_input("البيان / السبب", value=str(fin_to_edit["البيان / السبب"]))
            
            col_f1, col_f2 = st.columns(2)
            with col_f1:
                submit_edit_fin = st.form_submit_button("💾 حفظ تعديل المعاملة المالية", use_container_width=True)
            with col_f2:
                submit_del_fin = st.form_submit_button("🗑️ حذف المعاملة نهائياً", use_container_width=True)
                
            if submit_edit_fin:
                st.session_state.financial_transactions.loc[selected_fin_idx, "اسم الموظف"] = ed_f_emp
                st.session_state.financial_transactions.loc[selected_fin_idx, "النوع"] = ed_f_type
                st.session_state.financial_transactions.loc[selected_fin_idx, "المبلغ / القيمة"] = ed_f_amt
                st.session_state.financial_transactions.loc[selected_fin_idx, "البيان / السبب"] = ed_f_reason
                auto_save_data()
                st.success("تم تعديل المعاملة المالية بنجاح!")
                st.rerun()
            elif submit_del_fin:
                st.session_state.financial_transactions = st.session_state.financial_transactions.drop(index=selected_fin_idx).reset_index(drop=True)
                auto_save_data()
                st.error("تم حذف المعاملة المالية بنجاح!")
                st.rerun()
elif choice == "كشف الرواتب والمستحقات":
    col_t1, col_t2 = st.columns([3, 1])
    with col_t1: st.subheader("💰 2. كشف الرواتب وتفاصيل الاستحقاقات والاستقطاعات الشامل")
    with col_t2: render_print_button()
    
    employees_df = st.session_state.employees.copy()
    attendance_df = st.session_state.attendance.copy()
    financial_df = st.session_state.financial_transactions.copy()
    
    if employees_df.empty:
        st.warning("لا توجد بيانات موظفين مسجلة لحساب المرتبات.")
    else:
        payroll_data = []
        
        for _, emp in employees_df.iterrows():
            emp_code = emp["كود الموظف"]
            emp_name = emp["اسم الموظف"]
            emp_branch = emp["الفرع"]
            basic_salary = float(emp.get("الراتب الأساسي", 5000.0))
            
            emp_delays_mins = 0
            emp_overtime_mins = 0
            if not attendance_df.empty and "كود الموظف" in attendance_df.columns:
                emp_att = attendance_df[attendance_df["كود الموظف"] == emp_code]
                if not emp_att.empty:
                    emp_delays_mins = emp_att["التأخير الصباحي (دقيقة)"].sum() if "التأخير الصباحي (دقيقة)" in emp_att.columns else 0
                    emp_overtime_mins = emp_att["إضافي بعد العمل (دقيقة)"].sum() if "إضافي بعد العمل (دقيقة)" in emp_att.columns else 0
            
            total_advances = 0.0
            total_penalties = 0.0
            total_rewards = 0.0
            total_allowances = 0.0
            total_extra_manual = 0.0
            
            if not financial_df.empty and "كود الموظف" in financial_df.columns:
                emp_fin = financial_df[financial_df["كود الموظف"] == emp_code]
                if not emp_fin.empty:
                    for _, f_row in emp_fin.iterrows():
                        f_type = f_row["النوع"]
                        f_amount = float(f_row["المبلغ / القيمة"])
                        if f_type == "سلفة":
                            total_advances += f_amount
                        elif "جزاء" in f_type:
                            total_penalties += f_amount
                        elif "مكافأة" in f_type:
                            total_rewards += f_amount
                        elif "بدلات" in f_type:
                            total_allowances += f_amount
                        elif "إضافي" in f_type:
                            total_extra_manual += f_amount
            
            minute_rate = (basic_salary / 30.0 / 8.0 / 60.0) if basic_salary > 0 else 0
            delay_deduction_val = round(emp_delays_mins * minute_rate, 2)
            
            hour_rate = (basic_salary / 30.0 / 8.0) if basic_salary > 0 else 0
            overtime_amount_val = round((emp_overtime_mins / 60.0) * hour_rate * 1.5, 2)
            
            total_additions = round(overtime_amount_val + total_rewards + total_allowances + total_extra_manual, 2)
            total_deductions = round(delay_deduction_val + total_penalties + total_advances, 2)
            
            net_salary = round(basic_salary + total_additions - total_deductions, 2)
            
            payroll_data.append({
                "كود الموظف": emp_code,
                "اسم الموظف": emp_name,
                "الفرع": emp_branch,
                "الراتب الأساسي": basic_salary,
                "البدلات (جنيه)": total_allowances,
                "الإضافي / المكافآت (جنيه)": round(overtime_amount_val + total_rewards + total_extra_manual, 2),
                "إجمالي الاستحقاقات": round(basic_salary + total_additions, 2),
                "خصم التأخيرات (جنيه)": delay_deduction_val,
                "الجزاءات والخصومات (جنيه)": total_penalties,
                "السلف المالية (جنيه)": total_advances,
                "إجمالي الاستقطاعات": total_deductions,
                "صافي المستحق": net_salary
            })
            
        payroll_df = pd.DataFrame(payroll_data)
        render_printable_table(payroll_df)

elif choice == "إضافة موظف جديد":
    st.subheader(f"👥 1. إضافة موظف جديد - {company_display_name}")
    
    with st.form("new_employee_form_full"):
        c_code = st.text_input("كود الموظف")
        c_name = st.text_input("اسم الموظف الكامل")
        c_job = st.text_input("الوظيفة")
        c_dept = st.text_input("القسم")
        c_branch = st.text_input("الفرع")
        c_salary = st.number_input("الراتب الأساسي (جنيه)", min_value=0.0, value=5000.0)
        c_emp_permission = st.selectbox("صلاحية الموظف المخصصة", ["إدخال طلبات فقط", "اعتماد الطلبات", "مدير شؤون إدارية", "صلاحيات كاملة للقسم"])
        
        col_b1, col_b2, col_b3 = st.columns(3)
        with col_b1: c_annual = st.number_input("الرصيد السنوي", min_value=0, value=21)
        with col_b2: c_weekly = st.number_input("الرصيد الأسبوعي", min_value=0, value=4)
        with col_b3: c_official = st.number_input("رصيد الإجازات الرسمية", min_value=0, value=10)
        
        submit_new_emp = st.form_submit_button("إضافة الموظف الجديد وحفظ البيانات", use_container_width=True)
        if submit_new_emp:
            if c_code and c_name:
                new_emp = {
                    "كود الموظف": c_code, "اسم الموظف": c_name, "الوظيفة": c_job, "القسم": c_dept, "الفرع": c_branch,
                    "الراتب الأساسي": c_salary,
                    "صلاحية الموظف": c_emp_permission,
                    "رصيد سنوي (إجمالي)": c_annual, "سنوي مستهلك": 0, "سنوي متبقي": c_annual,
                    "رصيد أسبوعي (إجمالي)": c_weekly, "أسبوعي مستهلك": 0, "أسبوعي متبقي": c_weekly,
                    "رصيد رسمي (إجمالي)": c_official, "رسمي مستهلك": 0, "رسمي متبقي": c_official,
                    "إجازات مرضية (أيام)": 0
                }
                st.session_state.employees = pd.concat([st.session_state.employees, pd.DataFrame([new_emp])], ignore_index=True)
                auto_save_data()
                st.success("تم إضافة الموظف بنجاح!")
                st.rerun()

# =========================================================
# 👥 2. سجل الموظفين والأرصدة
# =========================================================
elif choice == "سجل الموظفين والأرصدة":
    col_t1, col_t2 = st.columns([3, 1])
    with col_t1: st.subheader(f"👥 2. سجل الموظفين والأرصدة - {company_display_name}")
    with col_t2: render_print_button()
    
    render_printable_table(st.session_state.employees)

# =========================================================
# 👥 3. تعديل أو حذف موظف
# =========================================================
elif choice == "تعديل أو حذف موظف":
    st.subheader("👥 3. تعديل أو حذف بيانات موظف")
    
    if st.session_state.employees.empty:
        st.info("لا توجد موظفين مسجلين.")
    else:
        emp_records = [f"الكود: {row['كود الموظف']} - الاسم: {row['اسم الموظف']} ({row['الوظيفة']})" for _, row in st.session_state.employees.iterrows()]
        selected_emp_label = st.selectbox("اختر الموظف المراد تعديله أو حذفه:", emp_records)
        selected_emp_idx = emp_records.index(selected_emp_label)
        
        emp_to_edit = st.session_state.employees.loc[selected_emp_idx]
        
        with st.form("edit_emp_form"):
            st.markdown(f"**تعديل بيانات الموظف: {emp_to_edit['اسم الموظف']} (كود: {emp_to_edit['كود الموظف']})**")
            
            ed_emp_code = st.text_input("كود الموظف", value=str(emp_to_edit["كود الموظف"]))
            ed_emp_name = st.text_input("اسم الموظف", value=str(emp_to_edit["اسم الموظف"]))
            ed_emp_job = st.text_input("الوظيفة", value=str(emp_to_edit["الوظيفة"]))
            ed_emp_dept = st.text_input("القسم", value=str(emp_to_edit["القسم"]))
            ed_emp_branch = st.text_input("الفرع", value=str(emp_to_edit["الفرع"]))
            ed_emp_sal = st.number_input("الراتب الأساسي", min_value=0.0, value=float(emp_to_edit["الراتب الأساسي"]))
            ed_emp_annual = st.number_input("رصيد سنوي (إجمالي)", min_value=0, value=int(emp_to_edit["رصيد سنوي (إجمالي)"]))
            ed_emp_annual_rem = st.number_input("سنوي متبقي", min_value=0, value=int(emp_to_edit["سنوي متبقي"]))
            
            col_em1, col_em2 = st.columns(2)
            with col_em1:
                submit_edit_emp = st.form_submit_button("💾 حفظ تعديلات الموظف", use_container_width=True)
            with col_em2:
                submit_del_emp = st.form_submit_button("🗑️ حذف الموظف نهائياً", use_container_width=True)
                
            if submit_edit_emp:
                st.session_state.employees.loc[selected_emp_idx, "كود الموظف"] = ed_emp_code
                st.session_state.employees.loc[selected_emp_idx, "اسم الموظف"] = ed_emp_name
                st.session_state.employees.loc[selected_emp_idx, "الوظيفة"] = ed_emp_job
                st.session_state.employees.loc[selected_emp_idx, "القسم"] = ed_emp_dept
                st.session_state.employees.loc[selected_emp_idx, "الفرع"] = ed_emp_branch
                st.session_state.employees.loc[selected_emp_idx, "الراتب الأساسي"] = ed_emp_sal
                st.session_state.employees.loc[selected_emp_idx, "رصيد سنوي (إجمالي)"] = ed_emp_annual
                st.session_state.employees.loc[selected_emp_idx, "سنوي متبقي"] = ed_emp_annual_rem
                auto_save_data()
                st.success("تم تعديل بيانات الموظف بنجاح!")
                st.rerun()
            elif submit_del_emp:
                st.session_state.employees = st.session_state.employees.drop(index=selected_emp_idx).reset_index(drop=True)
                auto_save_data()
                st.error("تم حذف الموظف بنجاح!")
                st.rerun()

elif choice == "إدارة المستخدمين والصلاحيات":
    st.subheader("🔒 إدارة مستخدمي النظام وفروعهم وأقسامهم والصلاحيات والرسوم السرية")
    
    with st.expander("➕ إضافة مستخدم جديد"):
        with st.form("add_user_form"):
            u_username = st.text_input("اسم المستخدم (Username)")
            u_fullname = st.text_input("الاسم الكامل للمستخدم")
            u_email = st.text_input("البريد الإلكتروني")
            u_branch_target = st.text_input("الفرع التابع له")
            u_dept_target = st.text_input("القسم التابع له")
            u_role = st.selectbox("صلاحية المستخدم", ["مشرف عام (Admin)", "مفوض الموارد البشرية (HR Manager)", "مدير فرع / قسم", "مستخدم عادي (Viewer)"])
            u_status = st.selectbox("حالة الحساب", ["نشط", "موقوف"])
            u_pattern = st.text_input("الرسم السري (Pattern)", placeholder="مثل: 1-2-3")
            
            add_user_btn = st.form_submit_button("إضافة المستخدم")
            if add_user_btn:
                if u_username and u_fullname and u_pattern and u_branch_target:
                    if u_username in st.session_state.users["اسم المستخدم"].values:
                        st.error("اسم المستخدم موجوة مسبقاً!")
                    else:
                        new_user = {
                            "اسم المستخدم": u_username, "الاسم الكامل": u_fullname, "الفرع التابع": u_branch_target,
                            "القسم التابع": u_dept_target, "الصلاحية": u_role, "البريد الإلكتروني": u_email,
                            "الحالة": u_status, "الرسم السري": u_pattern
                        }
                        st.session_state.users = pd.concat([st.session_state.users, pd.DataFrame([new_user])], ignore_index=True)
                        auto_save_data()  # 💾 حفظ تلقائي
                        st.success("تم إضافة المستخدم وحفظه تلقائياً!")
                        st.rerun()

    st.markdown("---")
    user_list = st.session_state.users["اسم المستخدم"].dropna().astype(str).tolist()
    if user_list:
        selected_username = st.selectbox("اختر اسم المستخدم للتعديل أو الحذف", user_list)
        user_row = st.session_state.users[st.session_state.users["اسم المستخدم"] == selected_username].iloc[0]
        
        with st.form("edit_delete_user_form"):
            e_uname = st.text_input("اسم المستخدم", value=str(user_row["اسم المستخدم"]), disabled=True)
            e_fullname = st.text_input("الاسم الكامل", value=str(user_row["الاسم الكامل"]))
            e_branch_target = st.text_input("الفرع التابع", value=str(user_row["الفرع التابع"]))
            e_dept_target = st.text_input("القسم التابع", value=str(user_row["القسم التابع"]))
            e_email = st.text_input("البريد الإلكتروني", value=str(user_row["البريد الإلكتروني"]))
            
            roles_list = ["مشرف عام (Admin)", "مفوض الموارد البشرية (HR Manager)", "مدير فرع / قسم", "مستخدم عادي (Viewer)"]
            e_role = st.selectbox("صلاحية المستخدم", roles_list, index=roles_list.index(user_row["الصلاحية"]) if user_row["الصلاحية"] in roles_list else 0)
            
            status_list = ["نشط", "موقوف"]
            e_status = st.selectbox("حالة الحساب", status_list, index=status_list.index(user_row["الحالة"]) if user_row["الحالة"] in status_list else 0)
            e_pattern = st.text_input("الرسم السري الجديد", value=str(user_row["الرسم السري"]))
            
            col_u1, col_u2 = st.columns(2)
            with col_u1: update_user_btn = st.form_submit_button("💾 حفظ تعديلات المستخدم", use_container_width=True)
            with col_u2: delete_user_btn = st.form_submit_button("🗑️ حذف المستخدم نهائياً", use_container_width=True)
                
            if update_user_btn:
                st.session_state.users.loc[st.session_state.users["اسم المستخدم"] == selected_username, [
                    "الاسم الكامل", "الفرع التابع", "القسم التابع", "البريد الإلكتروني", "الصلاحية", "الحالة", "الرسم السري"
                ]] = [e_fullname, e_branch_target, e_dept_target, e_email, e_role, e_status, e_pattern]
                auto_save_data()  # 💾 حفظ تلقائي
                st.success("تم تحديث بيانات المستخدم وحفظها تلقائياً!")
                st.rerun()
                
            if delete_user_btn:
                if len(st.session_state.users) <= 1:
                    st.error("لا يمكن حذف آخر مستخدم في النظام!")
                else:
                    st.session_state.users = st.session_state.users[st.session_state.users["اسم المستخدم"] != selected_username].reset_index(drop=True)
                    auto_save_data()  # 💾 حفظ تلقائي
                    st.warning("تم حذف المستخدم بنجاح!")
                    st.rerun()

    display_users_df = st.session_state.users.drop(columns=["الرسم السري"], errors="ignore")
    render_printable_table(display_users_df)

elif choice == "طباعة التقارير العامة":
    col_t1, col_t2 = st.columns([3, 1])
    with col_t1: st.subheader("🖨️ طباعة التقارير العامة")
    with col_t2: render_print_button()
    render_printable_table(st.session_state.employees)

elif choice == "إعدادات الشركة":
    st.subheader("⚙️ 4. إعدادات وبيانات الشركة")
    
    if "company_info" not in st.session_state:
        st.session_state.company_info = {
            "name": company_display_name,
            "address": "القاهرة، جمهورية مصر العربية",
            "cr": "123456",
            "tax": "987-654-321",
            "contact": "هاتف: 01000000000 | بريد: info@company.com",
            "license": company_license,
            "logo": None
        }
        
    info = st.session_state.company_info
    
    with st.form("company_settings_direct_form"):
        c_name = st.text_input("اسم الشركة", value=info.get("name", ""))
        c_address = st.text_input("عنوان الشركة", value=info.get("address", ""))
        c_cr = st.text_input("السجل التجاري", value=info.get("cr", ""))
        c_tax = st.text_input("الرقم الضريبي", value=info.get("tax", ""))
        c_contact = st.text_input("معلومات الاتصال", value=info.get("contact", ""))
        c_license = st.text_input("رقم الترخيص", value=info.get("license", ""))
        
        uploaded_logo = st.file_uploader("رفع شعار الشركة (Logo)", type=["png", "jpg", "jpeg"])
        
        submit_settings = st.form_submit_button("💾 حفظ وتحديث إعدادات الشركة", use_container_width=True)
        
        if submit_settings:
            info["name"] = c_name
            info["address"] = c_address
            info["cr"] = c_cr
            info["tax"] = c_tax
            info["contact"] = c_contact
            info["license"] = c_license
            
            if uploaded_logo is not None:
                bytes_data = uploaded_logo.getvalue()
                encoded_logo = base64.b64encode(bytes_data).decode('utf-8')
                info["logo"] = encoded_logo
                
            auto_save_data()
            st.success("تم تحديث إعدادات وحفظ بيانات الشركة بنجاح!")
            st.rerun()

elif choice == "تصدير وتحميل Excel":
    st.markdown('<div class="entry-form-area">', unsafe_allow_html=True)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        st.session_state.employees.to_excel(writer, sheet_name='الموظفين', index=False)
    output.seek(0)
    st.download_button("📥 تحميل ملف الإكسيل", data=output, file_name="system_data.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    st.markdown('</div>', unsafe_allow_html=True)

else:
    st.info(f"عنصر القائمة ({choice}) جاهز للعمل بكامل ميزاته.")
   
  نسخة احتياطية واستعادة
elif choice == "نسخة احتياطية واستعادة":
    st.subheader("💾 6. النسخ الاحتياطي والاستعادة")
    backup_dict = {
        "employees": st.session_state.employees.to_dict(orient='records'),
        "requests": st.session_state.requests.to_dict(orient='records'),
        "attendance": st.session_state.attendance.to_dict(orient='records'),
        "financial_transactions": st.session_state.financial_transactions.to_dict(orient='records'),
        "users": st.session_state.users.to_dict(orient='records'),
        "company_info": st.session_state.company_info
    }
    st.download_button("تحميل النسخة الاحتياطية (JSON)", data=json.dumps(backup_dict, ensure_ascii=False, indent=4), file_name=f"backup_{company_id}.json", mime="application/json")
 مسح البيانات
elif choice == "مسح البيانات":
    st.subheader("🗑️ 7. مسح وحذف كافة بيانات الشركة")
    confirm_text = st.text_input("اكتب 'تأكيد الحذف' للتأكيد:")
    if confirm_text == "تأكيد الحذف" and st.button("حذف كافة البيانات نهائياً", type="primary"):
        st.session_state.employees = pd.DataFrame(columns=["كود الموظف", "اسم الموظف", "الوظيفة", "القسم", "الفرع", "صلاحية الموظف", "الراتب الأساسي", "رصيد سنوي (إجمالي)", "سنوي مستهلك", "سنوي متبقي", "رصيد أسبوعي (إجمالي)", "أسبوعي مستهلك", "أسبوعي متبقي", "رصيد رسمي (إجمالي)", "رسمي مستهلك", "رسمي متبقي", "إجازات مرضية (أيام)"])
        st.session_state.requests = pd.DataFrame(columns=["رقم الطلب", "كود الموظف", "اسم الموظف", "الوظيفة", "الفرع", "نوع الإجازة", "من تاريخ", "إلى تاريخ", "عدد الأيام", "السبب", "الحالة"])
        st.session_state.attendance = pd.DataFrame(columns=["التاريخ", "كود الموظف", "اسم الموظف", "الفرع", "بداية العمل الرسمية", "نهاية العمل الرسمية", "وقت الحضور الفعلي", "وقت الانصراف الفعلي", "الحالة", "التأخير الصباحي (دقيقة)", "انصراف مبكر (دقيقة)", "إضافي بعد العمل (دقيقة)", "حضور مبكر (دقيقة)", "خروج متأخر (دقيقة)", "دقائق التأخير"])
        st.session_state.financial_transactions = pd.DataFrame(columns=["التاريخ", "كود الموظف", "اسم الموظف", "الفرع", "النوع", "المبلغ / القيمة", "البيان / السبب"])
        auto_save_data()
        st.success("تم مسح كافة البيانات بنجاح!")
        st.rerun()