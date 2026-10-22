import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import altair as alt
from datetime import datetime, date, time, timedelta
import io
import base64
import json
import os

# ضبط إعدادات الصفحة وتفعيل الواجهة الواسعة
st.set_page_config(
    page_title="النظام المتكامل لإدارة الإجازات والموارد البشرية",
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
# 💾 دوال الحفظ والاستعادة التلقائية المعزولة للشركة
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
                        "رقم الطلب", "كود الموظف", "اسم الموظف", "الوظيفة", "الفرع", "نوع الإجازة", "من تاريخ", "إلى تاريخ", "عدد الأيام", "الحالة"
                    ])

                if "attendance" in data and len(data["attendance"]) > 0:
                    st.session_state.attendance = pd.DataFrame(data["attendance"])
                else:
                    st.session_state.attendance = pd.DataFrame(columns=[
                        "التاريخ", "كود الموظف", "اسم الموظف", "الفرع", "بداية العمل الرسمية", "وقت الحضور", "وقت الانصراف", "دقائق التأخير", "ساعات الإضافي", "الحالة"
                    ])

                if "financial_transactions" in data and len(data["financial_transactions"]) > 0:
                    st.session_state.financial_transactions = pd.DataFrame(data["financial_transactions"])
                else:
                    st.session_state.financial_transactions = pd.DataFrame(columns=[
                        "التاريخ", "كود الموظف", "اسم الموظف", "النوع", "المبلغ / القيمة", "البيان / السبب"
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
            "رقم الطلب", "كود الموظف", "اسم الموظف", "الوظيفة", "الفرع", "نوع الإجازة", "من تاريخ", "إلى تاريخ", "عدد الأيام", "الحالة"
        ])
        st.session_state.attendance = pd.DataFrame(columns=[
            "التاريخ", "كود الموظف", "اسم الموظف", "الفرع", "بداية العمل الرسمية", "وقت الحضور", "وقت الانصراف", "دقائق التأخير", "ساعات الإضافي", "الحالة"
        ])
        st.session_state.financial_transactions = pd.DataFrame(columns=[
            "التاريخ", "كود الموظف", "اسم الموظف", "النوع", "المبلغ / القيمة", "البيان / السبب"
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

# دالة لاختيار الوقت بأسلوب 12 ساعة مع نطاق الدقائق من 0 إلى 59 (حتى 60 دقيقة)
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

# دالة زر الطباعة
def render_print_button():
    components.html("""
        <div style="text-align: left; margin-bottom: 10px;">
            <button onclick="window.parent.print()" style="
                background-color: #1f4068;
                color: white;
                padding: 8px 18px;
                border: none;
                border-radius: 5px;
                font-size: 13px;
                font-weight: bold;
                cursor: pointer;
                box-shadow: 0 2px 4px rgba(0,0,0,0.15);
                font-family: 'Tahoma', sans-serif;
            ">
                🖨️ طباعة الصفحة الحالية
            </button>
        </div>
    """, height=45)

# 🎨 تصميم CSS
st.markdown("""
    <style>
    [data-testid="stSidebar"] { display: none !important; }
    header[data-testid="stHeader"] { display: none !important; }
    html, body, [class*="css"] {
        font-family: 'Tahoma', 'Segoe UI', sans-serif;
        direction: rtl;
        text-align: right;
    }
    .block-container {
        padding-top: 0.3rem !important;
        padding-bottom: 0.5rem !important;
        max-width: 100% !important;
    }
    .company-header-container {
        background: linear-gradient(135deg, #1f4068 0%, #162447 100%);
        color: white;
        padding: 8px 12px;
        border-radius: 6px;
        margin-bottom: 6px !important;
        width: 100%;
        box-shadow: 0 1px 3px rgba(0,0,0,0.15);
        box-sizing: border-box;
    }
    .header-top-system {
        text-align: center;
        width: 100%;
        margin-bottom: 4px;
        border-bottom: 1px solid rgba(255, 255, 255, 0.2);
        padding-bottom: 3px;
    }
    .header-top-system h2 {
        font-size: 16px !important;
        font-weight: bold !important;
        color: #ffffff !important;
        margin: 0 !important;
        padding: 0 !important;
    }
    .header-bottom-content {
        display: flex;
        justify-content: space-between;
        align-items: center;
        width: 100%;
    }
    .header-right-info { text-align: right; flex: 3; }
    .header-left-logo {
        flex: 1;
        text-align: left;
        display: flex;
        justify-content: flex-end;
        align-items: center;
        padding-left: 5px;
    }
    .comp-name-txt {
        font-size: 13px !important;
        font-weight: bold !important;
        margin-bottom: 1px !important;
        color: #ffffff !important;
    }
    .comp-info-txt {
        font-size: 10px !important;
        margin: 1px 0 !important;
        color: #e0e0e0 !important;
        line-height: 1.2;
    }
    .dashboard-card {
        background: #ffffff;
        border-right: 4px solid #1f4068;
        padding: 8px 10px;
        border-radius: 5px;
        box-shadow: 0 1px 2px rgba(0,0,0,0.05);
        text-align: right;
        margin-bottom: 6px;
    }
    .dashboard-card-title {
        font-size: 11px;
        color: #555555;
        font-weight: bold;
        margin-bottom: 2px;
    }
    .dashboard-card-value {
        font-size: 20px;
        color: #1f4068;
        font-weight: bold;
    }
    .section-header {
        font-size: 13px !important;
        font-weight: bold !important;
        color: #1f4068 !important;
        border-bottom: 2px solid #1f4068;
        padding-bottom: 2px;
        margin-top: 6px !important;
        margin-bottom: 4px !important;
        text-align: right !important;
        direction: rtl !important;
    }
    table.custom-table {
        width: 100%;
        border-collapse: collapse;
        margin-top: 2px !important;
        margin-bottom: 6px !important;
        background-color: #ffffff;
        color: #000000;
        direction: rtl;
        text-align: right;
    }
    table.custom-table th, table.custom-table td {
        border: 1px solid #333333;
        padding: 4px 8px;
        text-align: right;
        font-size: 11px;
        color: #000000 !important;
        background-color: #ffffff !important;
    }
    table.custom-table th {
        background-color: #f0f2f6 !important;
        font-weight: bold;
    }
    
    @media print {
        body, .stApp, .block-container {
            background-color: #ffffff !important;
            color: #000000 !important;
            direction: rtl !important;
            text-align: right !important;
            -webkit-print-color-adjust: exact !important;
            print-color-adjust: exact !important;
        }
        button, .stButton, iframe, div[data-testid="stHeader"], div[data-baseweb="select"],
        .dashboard-card, div[data-testid="stForm"], .no-print {
            display: none !important;
        }
        .company-header-container {
            background: #ffffff !important;
            color: #000000 !important;
            border: 1px solid #000;
            box-shadow: none;
            -webkit-print-color-adjust: exact !important;
            print-color-adjust: exact !important;
        }
        .header-top-system h2, .comp-name-txt, .comp-info-txt {
            color: #000000 !important;
        }
        div[data-testid="stVegaLiteChart"] {
            background-color: #ffffff !important;
            border: 1px solid #ddd;
            padding: 10px;
            border-radius: 5px;
        }
    }
    </style>
""", unsafe_allow_html=True)

if 'is_authenticated' not in st.session_state: st.session_state.is_authenticated = False
if 'current_logged_user' not in st.session_state: st.session_state.current_logged_user = ""
if 'current_user_dept' not in st.session_state: st.session_state.current_user_dept = ""
if 'current_user_branch' not in st.session_state: st.session_state.current_user_branch = ""
if 'current_user_role' not in st.session_state: st.session_state.current_user_role = ""
if 'active_tab' not in st.session_state: st.session_state.active_tab = "لوحة التحكم الرئيسية"

def render_printable_table(df):
    if df.empty:
        st.info("لا توجد بيانات متاحة للعرض.")
        return
    html = f'<div class="printable-right-align">{df.to_html(classes="custom-table", index=False, escape=False)}</div>'
    st.markdown(html, unsafe_allow_html=True)

def render_company_header():
    info = st.session_state.company_info
    logo_html = '<div style="padding: 2px 4px; border: 1px dashed white; border-radius: 3px; font-size: 8px; color: white;">🏢 الشعار</div>'
    if info.get("logo") is not None:
        try:
            logo_html = f'<img src="data:image/png;base64,{info.get("logo")}" alt="Logo" style="max-height: 38px; max-width: 75px; object-fit: contain; background: white; border-radius: 3px; padding: 1px;" />'
        except Exception:
            pass
            
    st.markdown(
        f"""
        <div class="company-header-container">
            <div class="header-top-system">
                <h2>🏢 النظام المتكامل لإدارة الموارد البشرية - شركة: {info.get("name", "")} (ترخيص: {info.get("license", "")})</h2>
            </div>
            <div class="header-bottom-content">
                <div class="header-right-info">
                    <div class="comp-name-txt">{info.get("name", "")}</div>
                    <div class="comp-info-txt">📍 {info.get("address", "")} &nbsp;|&nbsp; 📋 سجل: {info.get("cr", "")} &nbsp;|&nbsp; 🧾 ضريبي: {info.get("tax", "")} &nbsp;|&nbsp; 🔑 ترخيص: {info.get("license", "")}</div>
                    <div class="comp-info-txt">📞 {info.get("contact", "")}</div>
                </div>
                <div class="header-left-logo">
                    {logo_html}
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

if not st.session_state.is_authenticated:
    st.markdown(
        f"""
        <div style="max-width: 450px; margin: 40px auto; background: #ffffff; padding: 25px; border-radius: 10px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); text-align: center; direction: rtl;">
            <h2 style="color: #1f4068; margin-bottom: 10px;">🔐 تسجيل الدخول - {company_display_name}</h2>
            <p style="color: #666; font-size: 13px;">رخصة النظام النشطة: {company_license}</p>
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
            login_btn = st.form_submit_button("🔓 فتح قفل الدخول للنظام", use_container_width=True)
            
            if login_btn:
                user_record = st.session_state.users[st.session_state.users["اسم المستخدم"] == selected_user_login].iloc[0]
                stored_pattern = str(user_record["الرسم السري"])
                
                if pattern_input.strip() == stored_pattern.strip():
                    st.session_state.is_authenticated = True
                    st.session_state.current_logged_user = selected_user_login
                    st.session_state.current_user_dept = user_record["القسم التابع"]
                    st.session_state.current_user_branch = user_record["الفرع التابع"]
                    st.session_state.current_user_role = user_record["الصلاحية"]
                    st.session_state.active_tab = "لوحة التحكم الرئيسية"
                    st.success(f"مرحباً بك يا {user_record['الاسم الكامل']}! تم تسجيل الدخول بنجاح.")
                    st.rerun()
                else:
                    st.error("❌ الرسم السري غير صحيح!")
    st.stop()

render_company_header()

# شريط التنقل الشامل
col_nav1, col_nav2, col_nav3, col_nav4, col_nav5, col_nav6 = st.columns(6)
with col_nav1:
    if st.button("📈 لوحة التحكم", use_container_width=True): st.session_state.active_tab = "لوحة التحكم الرئيسية"
with col_nav2:
    if st.button("⏱️ الحضور والانصراف", use_container_width=True): st.session_state.active_tab = "⏱️ الحضور والانصراف"
with col_nav3:
    if st.button("💰 السلف والماليات", use_container_width=True): st.session_state.active_tab = "💰 السلف والماليات"
with col_nav4:
    if st.button("📝 طلب إجازة", use_container_width=True): st.session_state.active_tab = "تسجيل طلب إجازة"
with col_nav5:
    if st.button("👥 الموظفين", use_container_width=True): st.session_state.active_tab = "إدارة وفهرس الموظفين"
with col_nav6:
    if st.button("🔍 بحث متقدم", use_container_width=True): st.session_state.active_tab = "🔍 بحث متقدم"

col_sub1, col_sub2, col_sub3, col_sub4, col_sub5, col_sub6, col_sub7, col_sub8 = st.columns(8)
with col_sub1:
    if st.button("🔒 المستخدمين", use_container_width=True): st.session_state.active_tab = "إدارة المستخدمين والصلاحيات"
with col_sub2:
    if st.button("💰 المرتبات", use_container_width=True): st.session_state.active_tab = "💰 الرواتب وكشف المرتبات"
with col_sub3:
    if st.button("🖨️ التقارير", use_container_width=True): st.session_state.active_tab = "🖨️ طباعة البيانات والتقارير"
with col_sub4:
    if st.button("⚙️ إعدادات الشركة", use_container_width=True): st.session_state.active_tab = "⚙️ إعدادات وبيانات الشركة"
with col_sub5:
    if st.button("📥 تحميل Excel", use_container_width=True): st.session_state.active_tab = "📥 تحميل البيانات (Excel)"
with col_sub6:
    if st.button("💾 نسخة احتياطية", use_container_width=True): st.session_state.active_tab = "💾 النسخة الاحتياطية"
with col_sub7:
    if st.button("📂 استعادة النسخة", use_container_width=True): st.session_state.active_tab = "📂 استعادة النسخة الاحتياطية"
with col_sub8:
    if st.button("🗑️ مسح البيانات", use_container_width=True): st.session_state.active_tab = "🗑️ مسح وحذف البيانات"

col_info_bar, col_logout_bar = st.columns([5, 1])
with col_info_bar:
    st.markdown(f"""
        <div style="background: #eef2f7; padding: 6px 12px; border-radius: 4px; font-size: 11px; margin-bottom: 8px; color: #1f4068; font-weight: bold; display: flex; gap: 15px; direction: rtl;">
            <div>🏢 الشركة: {company_display_name}</div>
            <div>🔑 رخصة التشغيل: {company_license}</div>
            <div>👤 المستخدم: {st.session_state.current_logged_user}</div>
            <div>🛡️ الصلاحية: {st.session_state.current_user_role}</div>
        </div>
    """, unsafe_allow_html=True)
with col_logout_bar:
    if st.button("🚪 خروج آمن", use_container_width=True):
        st.session_state.is_authenticated = False
        st.session_state.current_logged_user = ""
        st.rerun()

choice = st.session_state.active_tab

# =========================================================
# 📈 لوحة التحكم الرئيسية
# =========================================================
if choice == "لوحة التحكم الرئيسية":
    st.markdown(f'<div class="section-header">📈 مؤشرات الأداء العامة لشركة: {company_display_name}</div>', unsafe_allow_html=True)
    
    branch_filter = st.session_state.current_user_branch
    dept_filter = st.session_state.current_user_dept
    
    if "Admin" in st.session_state.current_user_role or "الإدارة العليا" in dept_filter:
        view_employees = st.session_state.employees
        view_requests = st.session_state.requests
    else:
        view_employees = st.session_state.employees[st.session_state.employees["الفرع"] == branch_filter]
        view_requests = st.session_state.requests[st.session_state.requests["الفرع"] == branch_filter]
    
    total_emps = len(view_employees)
    pending_count = len(view_requests[view_requests['الحالة'] == 'قيد الانتظار']) if not view_requests.empty else 0
    accepted_count = len(view_requests[view_requests['الحالة'] == 'مقبول']) if not view_requests.empty else 0
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f'<div class="dashboard-card"><div class="dashboard-card-title">👥 إجمالي موظفي الشركة</div><div class="dashboard-card-value">{total_emps}</div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="dashboard-card" style="border-right-color: #f0ad4e;"><div class="dashboard-card-title">⏳ الطلبات المعلقة</div><div class="dashboard-card-value" style="color: #f0ad4e;">{pending_count}</div></div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div class="dashboard-card" style="border-right-color: #5cb85c;"><div class="dashboard-card-title">✅ الطلبات المقبولة</div><div class="dashboard-card-value" style="color: #5cb85c;">{accepted_count}</div></div>', unsafe_allow_html=True)
    
    st.markdown(f'<div class="section-header">📊 الرسم البياني التحليلي لإحصائيات وأرصدة الموظفين</div>', unsafe_allow_html=True)
    
    col_f_type, col_f_val, col_p_btn = st.columns([2, 2, 1])
    with col_f_type:
        chart_filter_type = st.selectbox("تصفية المخطط للطباعة حسب:", ["عرض الكل", "فرع معين", "موظف معين"])
    
    filtered_chart_emps = view_employees.copy()
    chart_subtitle = "عرض شامل لجميع الفروع والموظفين"
    
    with col_f_val:
        if chart_filter_type == "فرع معين":
            branches_list = sorted(view_employees["الفرع"].dropna().unique().tolist())
            selected_b = st.selectbox("اختر الفرع للمخطط:", branches_list) if branches_list else None
            if selected_b:
                filtered_chart_emps = filtered_chart_emps[filtered_chart_emps["الفرع"] == selected_b]
                chart_subtitle = f"المخطط الخاص بفرع: {selected_b}"
        elif chart_filter_type == "موظف معين":
            emps_list = sorted(view_employees["اسم الموظف"].dropna().unique().tolist())
            selected_e = st.selectbox("اختر الموظف للمخطط:", emps_list) if emps_list else None
            if selected_e:
                filtered_chart_emps = filtered_chart_emps[filtered_chart_emps["اسم الموظف"] == selected_e]
                chart_subtitle = f"المخطط الخاص بالموظف: {selected_e}"
        else:
            st.selectbox("النطاق الحالي:", ["جميع الفروع والموظفين"], disabled=True)

    with col_p_btn:
        st.write("")
        st.write("")
        components.html("""
            <div style="text-align: left;">
                <button onclick="window.parent.print()" style="
                    background-color: #1f4068;
                    color: white;
                    padding: 8px 14px;
                    border: none;
                    border-radius: 4px;
                    font-size: 13px;
                    font-weight: bold;
                    cursor: pointer;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.15);
                    font-family: 'Tahoma', sans-serif;
                    width: 100%;
                ">
                    🖨️ طباعة المخطط فقط
                </button>
            </div>
        """, height=45)

    if not filtered_chart_emps.empty:
        st.markdown(f'<div style="text-align: right; direction: rtl; font-weight: bold; font-size: 14px; margin-bottom: 8px; color: #1f4068;">📌 {chart_subtitle}</div>', unsafe_allow_html=True)
        
        chart_df_melted = filtered_chart_emps.melt(
            id_vars=["اسم الموظف"],
            value_vars=["رصيد سنوي (إجمالي)", "سنوي مستهلك", "سنوي متبقي"],
            var_name="نوع الرصيد",
            value_name="عدد الأيام"
        )
        
        c1 = alt.Chart(chart_df_melted).mark_bar().encode(
            x=alt.X('اسم الموظف:N', title='الموظف', axis=alt.Axis(labelAngle=0, labelColor='#333333', titleColor='#1f4068')),
            y=alt.Y('عدد الأيام:Q', title='عدد الأيام', axis=alt.Axis(labelColor='#333333', titleColor='#1f4068')),
            color=alt.Color('نوع الرصيد:N', legend=alt.Legend(
                orient='bottom', 
                direction='horizontal',
                title='نوع الرصيد:',
                titleColor='#1f4068',
                labelColor='#333333',
                titleAnchor='middle'
            )),
            tooltip=['اسم الموظف', 'نوع الرصيد', 'عدد الأيام']
        ).properties(
            height=320,
            background='white'
        ).configure_view(
            fill='white',
            stroke=None
        )
        
        st.altair_chart(c1, use_container_width=True)
    else:
        st.info("لا توجد بيانات متاحة للمخطط حسب الفلتر المختار.")

    st.markdown(f'<div class="section-header">📋 أرصدة إجازات موظفي الشركة: {company_display_name}</div>', unsafe_allow_html=True)
    render_printable_table(view_employees)

# =========================================================
# ⏱️ الحضور والانصراف
# =========================================================
elif choice == "⏱️ الحضور والانصراف":
    col_t1, col_t2 = st.columns([3, 1])
    with col_t1: st.subheader("⏱️ تسجيل الحضور والانصراف واحتساب التأخير والإضافي والإجازات")
    with col_t2: render_print_button()
    
    col_a1, col_a2 = st.columns([1, 1])
    
    with col_a1:
        st.markdown("#### 📥 تسجيل حركة حضور / انصراف / إجازة جديدة")
        emp_names = st.session_state.employees["اسم الموظف"].tolist()
        if not emp_names:
            st.warning("لا توجد موظفون متاحون.")
        else:
            selected_emp = st.selectbox("اختر الموظف", emp_names)
            emp_data = st.session_state.employees[st.session_state.employees["اسم الموظف"] == selected_emp].iloc[0]
            
            att_date = st.date_input("التاريخ", value=date.today())
            
            att_status = st.selectbox("حالة اليوم", [
                "حضور", 
                "إجازة أسبوعية", 
                "إجازة سنوية", 
                "إجازة مرضية", 
                "غياب", 
                "إجازة رسمية", 
                "مأمورية"
            ])
            
            t_official_start, t_official_start_str = select_time_12h("بداية العمل الرسمية لهذا اليوم", "att_start", default_hour=8, default_minute=0, default_period="صباحاً (AM)")
            
            t_in_str, t_out_str = "-", "-"
            delay_minutes = 0
            overtime_hours = 0.0
            
            if att_status == "حضور":
                t_in, t_in_str = select_time_12h("وقت الحضور الفعلي", "att_in", default_hour=8, default_minute=0, default_period="صباحاً (AM)")
                t_out, t_out_str = select_time_12h("وقت الانصراف الفعلي", "att_out", default_hour=4, default_minute=0, default_period="مساءً (PM)")
            else:
                st.info(f"💡 تم إعداد الحالة كـ ({att_status})، فلن يتم احتساب تأخير أو وقت إضافي لهذا اليوم.")

            if st.button("حفظ حركة اليوم", use_container_width=True):
                emp_code = emp_data["كود الموظف"]
                emp_branch = emp_data["الفرع"]
                
                if att_status == "حضور":
                    dt_in = datetime.combine(att_date, t_in)
                    dt_official_start = datetime.combine(att_date, t_official_start)
                    if dt_in > dt_official_start:
                        delay_minutes = int((dt_in - dt_official_start).total_seconds() / 60)
                        
                    dt_out = datetime.combine(att_date, t_out)
                    dt_official_end = datetime.combine(att_date, time(16, 0))
                    if dt_out > dt_official_end:
                        overtime_hours = round((dt_out - dt_official_end).total_seconds() / 3600, 2)
                
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
                    "وقت الحضور": t_in_str,
                    "وقت الانصراف": t_out_str,
                    "دقائق التأخير": delay_minutes,
                    "ساعات الإضافي": overtime_hours,
                    "الحالة": att_status
                }
                
                st.session_state.attendance = pd.concat([st.session_state.attendance, pd.DataFrame([new_att])], ignore_index=True)
                auto_save_data()
                st.success(f"تم تسجيل حركة ({att_status}) بنجاح!")
                st.rerun()

    with col_a2:
        st.markdown("#### 📋 سجل الحضور والانصراف والإجازات المسجل")
        render_printable_table(st.session_state.attendance)

# =========================================================
# 💰 السلف والماليات
# =========================================================
elif choice == "💰 السلف والماليات":
    col_t1, col_t2 = st.columns([3, 1])
    with col_t1: st.subheader("💰 إدارة السلف، الجزاءات، والمكافآت المالية")
    with col_t2: render_print_button()
    
    col_f1, col_f2 = st.columns([1, 1])
    
    with col_f1:
        with st.form("financial_form"):
            st.markdown("#### 📝 إضافة معاملة مالية جديدة")
            emp_names = st.session_state.employees["اسم الموظف"].tolist()
            if not emp_names:
                st.warning("لا توجد موظفون مسجلون.")
            else:
                selected_emp_f = st.selectbox("اختر الموظف", emp_names)
                trans_type = st.selectbox("نوع المعاملة", ["سلفة", "جزاء (خصم)", "مكافأة (إضافي)"])
                trans_date = st.date_input("تاريخ المعاملة", value=date.today())
                amount = st.number_input("المبلغ / القيمة (جنيه)", min_value=0.0, value=100.0, step=50.0)
                reason = st.text_area("البيان / السبب التفصيلي")
                
                submit_fin = st.form_submit_button("حفظ المعاملة المالية")
                
                if submit_fin:
                    emp_data = st.session_state.employees[st.session_state.employees["اسم الموظف"] == selected_emp_f].iloc[0]
                    emp_code = emp_data["كود الموظف"]
                    
                    new_trans = {
                        "التاريخ": str(trans_date),
                        "كود الموظف": emp_code,
                        "اسم الموظف": selected_emp_f,
                        "النوع": trans_type,
                        "المبلغ / القيمة": amount,
                        "البيان / السبب": reason
                    }
                    
                    st.session_state.financial_transactions = pd.concat([st.session_state.financial_transactions, pd.DataFrame([new_trans])], ignore_index=True)
                    auto_save_data()
                    st.success("تم تسجيل المعاملة المالية بنجاح!")
                    st.rerun()

    with col_f2:
        st.markdown("#### 📋 سجل المعاملات المالية المسجلة")
        render_printable_table(st.session_state.financial_transactions)

# =========================================================
# 💰 الرواتب وكشف المرتبات (Payroll Summary)
# =========================================================
elif choice == "💰 الرواتب وكشف المرتبات":
    col_t1, col_t2 = st.columns([3, 1])
    with col_t1: st.subheader("💰 كشف المرتبات وصافي المستحقات الشهري")
    with col_t2: render_print_button()
    
    st.markdown("#### 📊 حساب وتصفية رواتب الموظفين عن الشهر الحالي")
    
    employees_df = st.session_state.employees.copy()
    attendance_df = st.session_state.attendance.copy()
    financial_df = st.session_state.financial_transactions.copy()
    
    if employees_df.empty:
        st.warning("لا توجد بيانات موظفين مسجلة لحساب المرتبات.")
    else:
        payroll_data = []
        
        for index, emp in employees_df.iterrows():
            emp_code = emp["كود الموظف"]
            emp_name = emp["اسم الموظف"]
            basic_salary = float(emp.get("الراتب الأساسي", 5000.0))
            
            emp_delays = 0
            emp_overtime_hours = 0.0
            if not attendance_df.empty and "كود الموظف" in attendance_df.columns:
                emp_att = attendance_df[attendance_df["كود الموظف"] == emp_code]
                if not emp_att.empty:
                    emp_delays = emp_att["دقائق التأخير"].sum() if "دقائق التأخير" in emp_att.columns else 0
                    emp_overtime_hours = emp_att["ساعات الإضافي"].sum() if "ساعات الإضافي" in emp_att.columns else 0.0
            
            total_advances = 0.0
            total_penalties = 0.0
            total_rewards = 0.0
            
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
            
            minute_rate = (basic_salary / 30.0 / 8.0 / 60.0) if basic_salary > 0 else 0
            delay_deduction = round(emp_delays * minute_rate, 2)
            
            hour_rate = (basic_salary / 30.0 / 8.0) if basic_salary > 0 else 0
            overtime_amount = round(emp_overtime_hours * hour_rate * 1.5, 2)
            
            total_deductions = delay_deduction + total_penalties + total_advances
            total_additions = overtime_amount + total_rewards
            
            net_salary = round(basic_salary + total_additions - total_deductions, 2)
            
            payroll_data.append({
                "كود الموظف": emp_code,
                "اسم الموظف": emp_name,
                "الراتب الأساسي": basic_salary,
                "إجمالي الإضافات": total_additions,
                "إجمالي الخصومات": total_deductions,
                "صافي المستحق": net_salary
            })
            
        payroll_df = pd.DataFrame(payroll_data)
        render_printable_table(payroll_df)

# =========================================================
# 📝 تسجيل طلب إجازة
# =========================================================
elif choice == "تسجيل طلب إجازة":
    col_t1, col_t2 = st.columns([3, 1])
    with col_t1: st.subheader(f"📝 تقديم طلب إجازة جديد - {company_display_name}")
    with col_t2: render_print_button()
    
    emp_list = st.session_state.employees["اسم الموظف"].dropna().astype(str).tolist()
    
    if not emp_list:
        st.warning("لا توجد موظفون متاحون لتسجيل إجازة لهم.")
    else:
        with st.form("leave_form"):
            emp_name = st.selectbox("اسم الموظف", emp_list)
            
            leave_type = st.selectbox("نوع الإجازة", [
                "إجازة سنوية (Annual)", 
                "إجازة أسبوعية / عارضة", 
                "إجازة مرضية (Sick Leave)", 
                "إجازة رسمية", 
                "بدون أجر"
            ])
            col_d1, col_d2 = st.columns(2)
            with col_d1: start_date = st.date_input("من تاريخ")
            with col_d2: end_date = st.date_input("إلى تاريخ")
            reason = st.text_area("سبب الإجازة / ملاحظات إضافية")
            submit = st.form_submit_button("إرسال طلب الإجازة للمراجعة")
            
            if submit:
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
                        "نوع الإجازة": leave_type, "من تاريخ": str(start_date), "إلى تاريخ": str(end_date), "عدد الأيام": days, "الحالة": "قيد الانتظار"
                    }
                    st.session_state.requests = pd.concat([st.session_state.requests, pd.DataFrame([new_req])], ignore_index=True)
                    auto_save_data()
                    st.success("تم تقديم طلب الإجازة وحفظه تلقائياً في ملف الشركة!")

# =========================================================
# 👥 إدارة وفهرس الموظفين
# =========================================================
elif choice == "إدارة وفهرس الموظفين":
    col_t1, col_t2 = st.columns([3, 1])
    with col_t1: st.subheader(f"👥 دليل الموظفين والأرصدة - {company_display_name}")
    with col_t2: render_print_button()
    
    with st.expander("➕ إضافة موظف جديد"):
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
        
        if st.button("إضافة الموظف", use_container_width=True):
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
                st.success("تم إضافة الموظف وحفظ البيانات تلقائياً!")
                st.rerun()
                
    render_printable_table(st.session_state.employees)

# =========================================================
# 🔒 إدارة المستخدمين والصلاحيات
# =========================================================
elif choice == "إدارة المستخدمين والصلاحيات":
    col_t1, col_t2 = st.columns([3, 1])
    with col_t1: st.subheader("🔒 إدارة مستخدمي النظام والصلاحيات")
    with col_t2: render_print_button()
    
    render_printable_table(st.session_state.users.drop(columns=["الرسم السري"], errors="ignore"))

# =========================================================
# 🔍 بحث متقدم
# =========================================================
elif choice == "🔍 بحث متقدم":
    col_f1, col_f2, col_f3 = st.columns([2, 2, 1])
    
    with col_f1:
        search_category = st.selectbox("اختر مجال البحث:", [
            "عرض الكل", "اسم الموظف", "الفرع", "الوظيفة", "كود الموظف", "اسم المستخدم", "بحث بالفترة (طلبات الإجازات)"
        ])
        
    with col_f2:
        selected_value = "الكل"
        date_from, date_to = None, None
        
        if search_category == "اسم الموظف":
            options = ["الكل"] + sorted(st.session_state.employees["اسم الموظف"].dropna().astype(str).unique().tolist())
            selected_value = st.selectbox("اختر اسم الموظف:", options)
        elif search_category == "الفرع":
            options = ["الكل"] + sorted(st.session_state.employees["الفرع"].dropna().astype(str).unique().tolist())
            selected_value = st.selectbox("اختر الفرع:", options)
        elif search_category == "الوظيفة":
            options = ["الكل"] + sorted(st.session_state.employees["الوظيفة"].dropna().astype(str).unique().tolist())
            selected_value = st.selectbox("اختر الوظيفة:", options)
        elif search_category == "كود الموظف":
            options = ["الكل"] + sorted(st.session_state.employees["كود الموظف"].dropna().astype(str).unique().tolist())
            selected_value = st.selectbox("اختر كود الموظف:", options)
        elif search_category == "اسم المستخدم":
            options = ["الكل"] + sorted(st.session_state.users["اسم المستخدم"].dropna().astype(str).unique().tolist())
            selected_value = st.selectbox("اختر اسم المستخدم:", options)
        elif search_category == "بحث بالفترة (طلبات الإجازات)":
            col_date1, col_date2 = st.columns(2)
            with col_date1: date_from = st.date_input("من تاريخ", value=date.today())
            with col_date2: date_to = st.date_input("إلى تاريخ", value=date.today())
        else:
            st.selectbox("القيمة:", ["الكل"])

    with col_f3:
        render_print_button()

    if search_category == "بحث بالفترة (طلبات الإجازات)":
        req_df = st.session_state.requests.copy()
        if not req_df.empty and "من تاريخ" in req_df.columns:
            req_df["من_تاريخ_dt"] = pd.to_datetime(req_df["من تاريخ"]).dt.date
            req_df["إلى_تاريخ_dt"] = pd.to_datetime(req_df["إلى تاريخ"]).dt.date
            req_df = req_df[(req_df["من_تاريخ_dt"] >= date_from) & (req_df["إلى_تاريخ_dt"] <= date_to)]
            req_df = req_df.drop(columns=["من_تاريخ_dt", "إلى_تاريخ_dt"])
        render_printable_table(req_df)
    
    # 5. إدارة المستخدمين
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

# 6. التقارير والطباعة
elif choice == "🖨️ طباعة البيانات والتقارير":
    report_type = st.selectbox("اختر نوع التقرير المُراد طباعته:", [
        "تقرير شامل لجميع الموظفين",
        "تقرير مخصص حسب (اسم الموظف)",
        "تقرير مخصص حسب (الفرع)",
        "تقرير مخصص حسب (القسم)",
        "تقرير مخصص حسب (كود الموظف)"
    ])
    
    st.components.v1.html(
        '<div style="text-align: right; margin: 2px 0;">'
        '<button onclick="parent.window.print();" style="background-color: #1f4068; color: white; padding: 6px 12px; border: none; border-radius: 5px; font-weight: bold; cursor: pointer; font-size: 12px; width: 100%;">'
        '🖨️ طباعة التقرير الحالي / حفظ PDF (اضغط هنا للطباعة)'
        '</button>'
        '</div>',
        height=38
    )
    
    branch_filter = st.session_state.current_user_branch
    dept_filter = st.session_state.current_user_dept
    is_admin_or_top = "Admin" in st.session_state.current_user_role or "الإدارة العليا" in dept_filter
    base_emps = st.session_state.employees if is_admin_or_top else st.session_state.employees[st.session_state.employees["الفرع"] == branch_filter]

elif choice == "⚙️ إعدادات وبيانات الشركة":
    st.subheader("⚙️ إعدادات وتعديل بيانات الشركة")
    with st.form("company_settings_form"):
        c_name = st.text_input("اسم الشركة", value=st.session_state.company_info.get("name", ""))
        c_address = st.text_input("عنوان الشركة", value=st.session_state.company_info.get("address", ""))
        save_settings = st.form_submit_button("حفظ التغييرات")
        if save_settings:
            st.session_state.company_info["name"] = c_name
            st.session_state.company_info["address"] = c_address
            auto_save_data()
            st.success("تم التحديث!")
            st.rerun()

elif choice == "📥 تحميل البيانات (Excel)":
    st.subheader("📥 تصدير وتحميل بيانات النظام بصيغة Excel")
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        st.session_state.employees.to_excel(writer, sheet_name='الموظفين', index=False)
        st.session_state.requests.to_excel(writer, sheet_name='سجل الإجازات', index=False)
        st.session_state.attendance.to_excel(writer, sheet_name='الحضور والانصراف', index=False)
        st.session_state.financial_transactions.to_excel(writer, sheet_name='السلف والماليات', index=False)
    output.seek(0)
    st.download_button(label="تحميل ملف الإكسيل الآن", data=output, file_name=f"Leave_System_{company_id}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

elif choice == "💾 النسخة الاحتياطية":
    st.subheader("💾 تحميل النسخة الاحتياطية")
    backup_dict = {
        "employees": st.session_state.employees.to_dict(orient='records'),
        "requests": st.session_state.requests.to_dict(orient='records'),
        "attendance": st.session_state.attendance.to_dict(orient='records'),
        "financial_transactions": st.session_state.financial_transactions.to_dict(orient='records'),
        "users": st.session_state.users.to_dict(orient='records'),
        "company_info": st.session_state.company_info
    }
    st.download_button("تحميل النسخة الاحتياطية (JSON)", data=json.dumps(backup_dict, ensure_ascii=False, indent=4), file_name=f"backup_{company_id}.json", mime="application/json")

elif choice == "📂 استعادة النسخة الاحتياطية":
    st.subheader("📂 استعادة نسخة احتياطية")
    uploaded_backup = st.file_uploader("اختر ملف JSON", type=["json"])
    if uploaded_backup is not None and st.button("تأكيد الاستعادة"):
        backup_data = json.load(uploaded_backup)
        if "employees" in backup_data: st.session_state.employees = pd.DataFrame(backup_data["employees"])
        if "requests" in backup_data: st.session_state.requests = pd.DataFrame(backup_data["requests"])
        if "attendance" in backup_data: st.session_state.attendance = pd.DataFrame(backup_data["attendance"])
        if "financial_transactions" in backup_data: st.session_state.financial_transactions = pd.DataFrame(backup_data["financial_transactions"])
        if "users" in backup_data: st.session_state.users = pd.DataFrame(backup_data["users"])
        auto_save_data()
        st.success("تمت الاستعادة بنجاح!")
        st.rerun()

elif choice == "🗑️ مسح وحذف البيانات":
    st.subheader("🗑️ مسح بيانات الشركة")
    confirm_text = st.text_input("اكتب 'تأكيد الحذف' للتأكيد:")
    if confirm_text == "تأكيد الحذف" and st.button("حذف كافة البيانات", type="primary"):
        st.session_state.employees = pd.DataFrame(columns=["كود الموظف", "اسم الموظف", "الوظيفة", "القسم", "الفرع", "صلاحية الموظف", "الراتب الأساسي", "رصيد سنوي (إجمالي)", "سنوي مستهلك", "سنوي متبقي", "رصيد أسبوعي (إجمالي)", "أسبوعي مستهلك", "أسبوعي متبقي", "رصيد رسمي (إجمالي)", "رسمي مستهلك", "رسمي متبقي", "إجازات مرضية (أيام)"])
        st.session_state.requests = pd.DataFrame(columns=["رقم الطلب", "كود الموظف", "اسم الموظف", "الوظيفة", "الفرع", "نوع الإجازة", "من تاريخ", "إلى تاريخ", "عدد الأيام", "الحالة"])
        st.session_state.attendance = pd.DataFrame(columns=["التاريخ", "كود الموظف", "اسم الموظف", "الفرع", "بداية العمل الرسمية", "وقت الحضور", "وقت الانصراف", "دقائق التأخير", "ساعات الإضافي", "الحالة"])
        st.session_state.financial_transactions = pd.DataFrame(columns=["التاريخ", "كود الموظف", "اسم الموظف", "النوع", "المبلغ / القيمة", "البيان / السبب"])
        auto_save_data()
        st.success("تم المسح بنجاح!")
        st.rerun()