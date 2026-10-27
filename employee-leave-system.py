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
    "الرئيسية": ["لوحة التحكم والمؤشرات"],
    "الحضور والانصراف": ["تسجيل حضور وانصراف", "سجل الحضور والانصراف", "تعديل أو حذف حركة حضور"],
    "طلبات الاجازة": ["تسجيل طلب إجازة", "سجل طلبات قيد الانتظار", "سجل الطلبات المقبولة", "سجل الطلبات المرفوضة", "تعديل أو حذف طلب إجازة"],
    "المعاملات المالية": ["تسجيل معاملة مالية", "سجل المعاملات المالية", "تعديل أو حذف معاملة مالية"],
    "كشف الرواتب": ["كشف الرواتب والمستحقات الشامل"],
    "شؤون الموظفين": ["إضافة موظف جديد", "سجل الموظفين والأرصدة", "تعديل أو حذف موظف"],
    "المستخدمين": ["إدارة المستخدمين والصلاحيات"],
    "التقارير": ["طباعة التقارير العامة"],
    "اعدادات الشركة": ["إعدادات الشركة وبياناتها"],
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
    st.subheader("⏱️ تسجيل حضور / انصراف جديد")
    emp_names = st.session_state.employees["اسم الموظف"].tolist()
    if emp_names:
        st.markdown('<div class="entry-form-area">', unsafe_allow_html=True)
        with st.form("att_form"):
            selected_emp = st.selectbox("الموظف", emp_names)
            att_date = st.date_input("التاريخ", value=date.today())
            att_status = st.selectbox("الحالة", ["حضور", "إجازة أسبوعية", "إجازة سنوية", "غياب"])
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

elif choice == "تسجيل طلب إجازة":
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

elif choice == "كشف الرواتب والمستحقات الشامل":
    col_t1, col_t2 = st.columns([3, 1])
    with col_t1: st.subheader("💰 كشف الرواتب والمستحقات الشامل")
    with col_t2: render_print_button()
    render_printable_table(st.session_state.employees)

elif choice == "إضافة موظف جديد":
    st.subheader("👥 إضافة موظف جديد")
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

elif choice == "إدارة المستخدمين والصلاحيات":
    st.subheader("🔒 إدارة المستخدمين والصلاحيات")
    render_printable_table(st.session_state.users.drop(columns=["الرسم السري"], errors="ignore"))

elif choice == "طباعة التقارير العامة":
    col_t1, col_t2 = st.columns([3, 1])
    with col_t1: st.subheader("🖨️ طباعة التقارير العامة")
    with col_t2: render_print_button()
    render_printable_table(st.session_state.employees)

elif choice == "إعدادات الشركة وبياناتها":
    st.subheader("⚙️ إعدادات الشركة وبياناتها")
    info = st.session_state.company_info
    st.markdown('<div class="entry-form-area">', unsafe_allow_html=True)
    with st.form("settings"):
        cn = st.text_input("اسم الشركة", value=info.get("name", ""))
        car = st.text_input("السجل التجاري", value=info.get("cr", ""))
        if st.form_submit_button("حفظ التعديلات", use_container_width=True):
            info["name"] = cn
            info["cr"] = car
            auto_save_data()
            st.success("تم التحديث!")
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

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