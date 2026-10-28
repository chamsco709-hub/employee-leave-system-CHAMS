import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
from datetime import datetime, date, time, timedelta
import json
import os
import io
import base64

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

DOCS_DIR = "client_employees_docs"
if not os.path.exists(DOCS_DIR):
    os.makedirs(DOCS_DIR)

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
                    df_emp = pd.DataFrame(data["employees"])
                    if "مسوغات التعيين" not in df_emp.columns:
                        df_emp["مسوغات التعيين"] = ""
                    st.session_state.employees = df_emp
                else:
                    st.session_state.employees = pd.DataFrame(columns=[
                        "كود الموظف", "اسم الموظف", "الوظيفة", "القسم", "الفرع", "صلاحية الموظف",
                        "الراتب الأساسي", "مسوغات التعيين",
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
                    df_att = pd.DataFrame(data["attendance"])
                    expected_att_cols = [
                        "التاريخ", "كود الموظف", "اسم الموظف", "الوظيفة", "الفرع", 
                        "بداية العمل الرسمية", "نهاية العمل الرسمية", "وقت الحضور الفعلي", "وقت الانصراف الفعلي", 
                        "فترة السماح (دقيقة)", "الحالة", "التأخير (دقيقة)", "إضافي (دقيقة)"
                    ]
                    for col in expected_att_cols:
                        if col not in df_att.columns:
                            df_att[col] = 0 if "(دقيقة)" in col else ""
                    st.session_state.attendance = df_att[expected_att_cols]
                else:
                    st.session_state.attendance = pd.DataFrame(columns=[
                        "التاريخ", "كود الموظف", "اسم الموظف", "الوظيفة", "الفرع", 
                        "بداية العمل الرسمية", "نهاية العمل الرسمية", "وقت الحضور الفعلي", "وقت الانصراف الفعلي", 
                        "فترة السماح (دقيقة)", "الحالة", "التأخير (دقيقة)", "إضافي (دقيقة)"
                    ])

                if "financial_transactions" in data and len(data["financial_transactions"]) > 0:
                    st.session_state.financial_transactions = pd.DataFrame(data["financial_transactions"])
                else:
                    st.session_state.financial_transactions = pd.DataFrame(columns=[
                        "التاريخ", "كود الموظف", "اسم الموظف", "الفرع", "النوع", "المبلغ / القيمة", "البيان / السبب"
                    ])

                if "users" in data and len(data["users"]) > 0:
                    df_users = pd.DataFrame(data["users"])
                    if "الحالة" not in df_users.columns:
                        df_users["الحالة"] = "نشط"
                    st.session_state.users = df_users
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
                "صلاحية الموظف": "اعتماد الطلبات", "الراتب الأساسي": 5000, "مسوغات التعيين": "",
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
            "التاريخ", "كود الموظف", "اسم الموظف", "الوظيفة", "الفرع", 
            "بداية العمل الرسمية", "نهاية العمل الرسمية", "وقت الحضور الفعلي", "وقت الانصراف الفعلي", 
            "فترة السماح (دقيقة)", "الحالة", "التأخير (دقيقة)", "إضافي (دقيقة)"
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
            "contact": "01000000000",
            "email": "info@company.com",
            "license": company_license,
            "logo": ""
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
        <div style="text-align: left; margin-bottom: 12px; margin-top: 5px;" class="no-print">
            <button onclick="
                window.parent.print();
            " style="
                background: linear-gradient(135deg, #E50914 0%, #B20710 100%);
                color: white;
                padding: 8px 18px;
                border: none;
                border-radius: 10px;
                font-size: 12.5px;
                font-weight: bold;
                cursor: pointer;
                box-shadow: 0 4px 12px rgba(229, 9, 20, 0.4);
                font-family: 'Tahoma', sans-serif;
            ">
                🖨️ طباعة الجدول الحالي فقط
            </button>
        </div>
    """, height=45)

# 🎨 تصميم CSS مع تنسيق احترافي للمسافات والهوامش
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
        padding-top: 0.5rem !important;
        padding-bottom: 3rem !important;
        padding-left: 1.5rem !important;
        padding-right: 1.5rem !important;
        max-width: 100% !important;
        background: linear-gradient(135deg, #121212 0%, #1A1A1A 50%, #0B0B0B 100%) !important;
        min-height: 100vh;
    }
    
    /* 📌 تنسيق وتثبيت الهيدر والأقسام العلوية بمسافات مدمجة ومنظمة */
    .sticky-top-wrapper {
        position: fixed !important;
        top: 0 !important;
        left: 0 !important;
        right: 0 !important;
        z-index: 999999 !important;
        background: #121212 !important;
        padding: 8px 15px 4px 15px !important;
        border-bottom: 2px solid #E50914;
        box-shadow: 0 8px 25px rgba(0,0,0,0.8);
    }
    
    /* 🚀 مسافة علوية مثالية للمحتوى أسفل الشريط المثبت */
    .main-content-spacer {
        margin-top: 165px !important;
    }
    
    label p, .stRadio label, .stSelectbox label, .stTextInput label, .stNumberInput label, .stDateInput label {
        color: #CBD5E1 !important;
        font-weight: bold !important;
        font-size: 13px !important;
        margin-bottom: 4px !important;
    }
    
    input, textarea, select {
        background-color: rgba(30, 41, 59, 0.9) !important;
        color: #FFFFFF !important;
        font-size: 13px !important;
        font-weight: bold !important;
        border-radius: 10px !important;
        border: 1.5px solid #475569 !important;
        padding: 8px 12px !important;
    }
    
    .glass-header {
        background: rgba(30, 30, 30, 0.85);
        border: 1px solid rgba(255, 255, 255, 0.08);
        color: #FFFFFF !important;
        padding: 6px 12px;
        border-radius: 10px;
        width: 100%;
        margin-bottom: 3px;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    
    .header-logo-box {
        font-size: 20px;
        background: rgba(229, 9, 20, 0.2);
        padding: 4px 8px;
        border-radius: 8px;
        border: 1px solid rgba(229, 9, 20, 0.4);
        text-align: center;
        min-width: 30px;
    }
    
    .header-top-system h2 {
        font-size: 11px !important;
        font-weight: bold !important;
        color: #F87171 !important;
        margin: 0 0 1px 0 !important;
    }
    .comp-name-txt {
        font-size: 13px !important;
        font-weight: bold !important;
        color: #FFFFFF !important;
    }
    .comp-info-txt {
        font-size: 9.5px !important;
        color: #94A3B8 !important;
        margin-top: 1px;
    }
    
    .user-badge-box {
        background: rgba(229, 9, 20, 0.15);
        border: 1px solid rgba(229, 9, 20, 0.4);
        padding: 2px 6px;
        border-radius: 5px;
        font-size: 10px;
        color: #FCA5A5;
        font-weight: bold;
        text-align: center;
        margin-bottom: 2px;
    }
    
    .glass-card {
        background: rgba(30, 30, 30, 0.75);
        backdrop-filter: blur(15px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-right: 5px solid #E50914;
        padding: 14px 16px;
        border-radius: 14px;
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.4);
        text-align: right !important;
        margin-bottom: 12px;
    }
    .glass-card-title {
        font-size: 12px;
        color: #94A3B8;
        font-weight: bold;
        margin-bottom: 4px;
    }
    .glass-card-value {
        font-size: 22px;
        color: #FFFFFF;
        font-weight: bold;
    }
    
    .section-header {
        font-size: 16px !important;
        font-weight: bold !important;
        color: #F87171 !important;
        border-bottom: 2px solid #E50914;
        padding-bottom: 8px;
        margin-top: 18px !important;
        margin-bottom: 14px !important;
        text-align: right !important;
    }
    
    table.custom-table {
        width: 100%;
        border-collapse: separate;
        border-spacing: 0;
        margin-top: 8px !important;
        margin-bottom: 16px !important;
        background-color: rgba(24, 24, 24, 0.9);
        color: #FFFFFF;
        border-radius: 12px;
        overflow: hidden;
        border: 1px solid rgba(255, 255, 255, 0.08);
    }
    table.custom-table th, table.custom-table td {
        border-bottom: 1px solid #333333;
        padding: 10px 14px;
        text-align: right !important;
        font-size: 12.5px;
        color: #E2E8F0 !important;
    }
    table.custom-table th {
        background-color: rgba(229, 9, 20, 0.2) !important;
        font-weight: bold;
        color: #FCA5A5 !important;
        border-bottom: 2px solid #E50914;
    }
    
    .entry-form-area {
        background: rgba(30, 30, 30, 0.85);
        backdrop-filter: blur(15px);
        padding: 22px;
        border-radius: 16px;
        box-shadow: 0 6px 20px rgba(0,0,0,0.4);
        border: 1px solid rgba(255, 255, 255, 0.08);
        margin-bottom: 16px;
    }
    
    /* 🖨️ إخفاء تام لكل العناصر غير المرغوبة عند الطباعة */
    @media print {
        @page { size: A4 landscape; margin: 8mm; }
        body, .stApp, .block-container {
            background-color: #FFFFFF !important;
            color: #000000 !important;
            direction: rtl !important;
            text-align: right !important;
            width: 100% !important;
            margin: 0 !important;
            padding: 0 !important;
        }
        button, .stButton, iframe, div[data-testid="stHeader"], .no-print, .entry-form-area, hr, .sticky-top-wrapper, .cinema-top-bar, .user-badge-box, .glass-header, .glass-card, [data-testid="column"] { 
            display: none !important; 
        }
        .printable-right-align {
            display: block !important;
            width: 100% !important;
        }
        table.custom-table { 
            width: 100% !important; 
            border: 1px solid #000000 !important; 
            background-color: #FFFFFF !important;
            color: #000000 !important;
            display: table !important;
        }
        table.custom-table th { 
            background-color: #E2E8F0 !important; 
            color: #000000 !important; 
            border-bottom: 2px solid #000000 !important;
            display: table-header-group !important;
        }
        table.custom-table tr {
            page-break-inside: avoid !important;
            display: table-row !important;
        }
        table.custom-table td {
            color: #000000 !important;
            border-bottom: 1px solid #CBD5E1 !important;
            display: table-cell !important;
        }
    }
    </style>
""", unsafe_allow_html=True)

if 'is_authenticated' not in st.session_state: st.session_state.is_authenticated = False
if 'current_logged_user' not in st.session_state: st.session_state.current_logged_user = ""
if 'current_user_dept' not in st.session_state: st.session_state.current_user_dept = ""
if 'current_user_branch' not in st.session_state: st.session_state.current_user_branch = ""
if 'current_user_role' not in st.session_state: st.session_state.current_user_role = ""

if 'active_main_section' not in st.session_state: st.session_state.active_main_section = "الرئيسية"

def render_printable_table(df):
    if df.empty:
        st.info("لا توجد بيانات متاحة للعرض.")
        return
    html = f'<div class="printable-right-align">{df.to_html(classes="custom-table", index=False, escape=False)}</div>'
    st.markdown(html, unsafe_allow_html=True)

def render_company_header():
    info = st.session_state.company_info
    logo_val = info.get("logo", "")
    
    if logo_val and logo_val.startswith("data:image"):
        logo_html = f'<img src="{logo_val}" style="width: 32px; height: 32px; object-fit: contain; border-radius: 6px; background: white; padding: 2px;" />'
    elif logo_val and (logo_val.startswith("http://") or logo_val.startswith("https://")):
        logo_html = f'<img src="{logo_val}" style="width: 32px; height: 32px; object-fit: contain; border-radius: 6px;" />'
    else:
        logo_html = '<div class="header-logo-box">🏢</div>'

    contact_num = info.get("contact", "غير محدد")
    email_addr = info.get("email", "غير محدد")
    address_str = info.get("address", "غير محدد")
    cr_num = info.get("cr", "غير محدد")
    tax_num = info.get("tax", "غير محدد")
    lic_num = info.get("license", "غير محدد")
    comp_name = info.get("name", "")

    st.markdown(
        f"""
        <div class="glass-header">
            <div style="display: flex; align-items: center; gap: 8px; width: 100%;">
                {logo_html}
                <div style="width: 100%;">
                    <div class="header-top-system"><h2>برنامج شؤون الموظفين والإدارة</h2></div>
                    <div class="comp-name-txt">{comp_name}</div>
                    <div class="comp-info-txt">📍 العنوان: {address_str} &nbsp;|&nbsp; 📋 س.ت: {cr_num} &nbsp;|&nbsp; 🧾 ب.ض: {tax_num} &nbsp;|&nbsp; 📞 هاتف: {contact_num} &nbsp;|&nbsp; ✉️ بريد: {email_addr} &nbsp;|&nbsp; 🔑 ترخيص: {lic_num}</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

if not st.session_state.is_authenticated:
    lic_info = get_client_license()
    st.markdown(
        f"""
        <div style="max-width: 480px; margin: 60px auto; background: rgba(30, 30, 30, 0.9); backdrop-filter: blur(20px); padding: 40px; border-radius: 20px; box-shadow: 0 20px 40px rgba(0,0,0,0.7); text-align: center; border: 1px solid rgba(255,255,255,0.08);">
            <h2 style="color: #F87171; margin-bottom: 8px; font-size: 22px;">النظام المتكامل لشؤون الموظفين</h2>
            <p style="color: #FFFFFF; font-size: 15px; font-weight: bold; margin-bottom: 4px;">{lic_info.get('name', '')}</p>
            <p style="color: #94A3B8; font-size: 12.5px;">رقم الترخيص: {lic_info.get('license', '')}</p>
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
                if user_record.get("الحالة", "نشط") == "إيقاف":
                    st.error("❌ هذا المستخدم موقوف عن العمل!")
                elif pattern_input.strip() == str(user_record["الرسم السري"]).strip():
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
# 📌 الشريط العلوي الثابت بمسافات منظمة
# ---------------------------------------------------------
st.markdown('<div class="sticky-top-wrapper">', unsafe_allow_html=True)

render_company_header()

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

main_sections = [
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
]

sec_cols = st.columns(len(main_sections))
for idx, sec_name in enumerate(main_sections):
    with sec_cols[idx]:
        if st.button(sec_name, use_container_width=True, key=f"btn_sec_{idx}"):
            st.session_state.active_main_section = sec_name
            st.rerun()

selected_main_cat = st.session_state.active_main_section

sub_options_map = {
    "الرئيسية": ["لوحة التحكم والمؤشرات"],
    "الحضور والانصراف": ["تسجيل حضور وانصراف", "سجل الحضور والانصراف", "تعديل أو حذف حركة حضور"],
    "طلبات الاجازة": ["تسجيل طلب إجازة", "سجل طلبات قيد الانتظار", "سجل الطلبات المقبولة", "سجل الطلبات المرفوضة", "تعديل أو حذف طلب إجازة"],
    "المعاملات المالية": ["تسجيل معاملة مالية", "سجل المعاملات المالية", "تعديل أو حذف معاملة مالية"],
    "كشف الرواتب": ["كشف الرواتب والمستحقات الشامل"],
    "شؤون الموظفين": ["إضافة موظف جديد", "سجل الموظفين والأرصدة الشاملة", "تعديل أو حذف موظف"],
    "المستخدمين": ["إضافة مستخدم جديد", "إدارة المستخدمين والصلاحيات والسجل", "تعديل أو حذف مستخدم"],
    "التقارير": ["طباعة التقارير العامة"],
    "اعدادات الشركة": ["إعدادات الشركة وبياناتها الشاملة"],
    "أدوات النظام": ["تصدير وتحميل Excel", "نسخة احتياطية واستعادة", "مسح البيانات"]
}

st.markdown('<div class="cinema-top-bar" style="margin-top: 2px;">', unsafe_allow_html=True)
col_sub1, col_sub2 = st.columns([4, 1])

with col_sub1:
    sub_options_list = sub_options_map.get(selected_main_cat, ["لوحة التحكم والمؤشرات"])
    choice = st.selectbox(f"📑 العمليات الفرعية لقسم ({selected_main_cat}):", sub_options_list)

with col_sub2:
    st.write("")
    if st.button("⏹️ خروج", use_container_width=True):
        st.session_state.is_authenticated = False
        st.session_state.current_logged_user = ""
        st.rerun()

st.markdown('</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="main-content-spacer"></div>', unsafe_allow_html=True)

# ---------------------------------------------------------
# 🎯 بطاقات المؤشرات العامة العلوية
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
    active_users_count = len(st.session_state.users[st.session_state.users["الحالة"] == "نشط"]) if not st.session_state.users.empty else 0
    st.markdown(f'<div class="glass-card" style="border-right-color: #3B82F6;"><div class="glass-card-title">🛡️ المستخدمين النشطين</div><div class="glass-card-value" style="font-size: 18px; color: #3B82F6;">{active_users_count} مستخدم</div></div>', unsafe_allow_html=True)

st.markdown("<hr style='border: 0.5px solid rgba(255,255,255,0.08); margin: 12px 0 20px 0;'>", unsafe_allow_html=True)

# =========================================================
# منطق عرض الشاشات والأقسام الشاملة والمحدثة
# =========================================================
if selected_main_cat == "الرئيسية" or choice == "لوحة التحكم والمؤشرات":
    st.markdown(f'<div class="section-header">📊 داشبورد ومخطط بيانات لكل فرع (بيانات تفصيلية)</div>', unsafe_allow_html=True)
    
    all_branches = st.session_state.employees["الفرع"].unique().tolist() if not st.session_state.employees.empty else ["المركز الرئيسي"]
    
    for branch in all_branches:
        st.markdown(f"### 📍 فرع: {branch}")
        branch_emps = st.session_state.employees[st.session_state.employees["الفرع"] == branch]
        b_count = len(branch_emps)
        b_sal_total = float(branch_emps["الراتب الأساسي"].sum()) if not branch_emps.empty else 0.0
        
        b_att = st.session_state.attendance[st.session_state.attendance["الفرع"] == branch] if not st.session_state.attendance.empty else pd.DataFrame()
        b_att_count = len(b_att)
        
        bc1, bc2, bc3 = st.columns(3)
        with bc1:
            st.markdown(f'<div class="glass-card"><div class="glass-card-title">👥 عدد الموظفين بالفرع</div><div class="glass-card-value">{b_count}</div></div>', unsafe_allow_html=True)
        with bc2:
            st.markdown(f'<div class="glass-card" style="border-right-color: #3B82F6;"><div class="glass-card-title">💰 إجمالي رواتب الفرع</div><div class="glass-card-value" style="font-size: 18px; color: #3B82F6;">{b_sal_total:,.0f} ج.م</div></div>', unsafe_allow_html=True)
        with bc3:
            st.markdown(f'<div class="glass-card" style="border-right-color: #10B981;"><div class="glass-card-title">⏱️ حركات الحضور المسجلة</div><div class="glass-card-value" style="color: #10B981;">{b_att_count}</div></div>', unsafe_allow_html=True)
        
        if not branch_emps.empty:
            st.markdown(f"**📋 جدول موظفي فرع ({branch}):**")
            render_print_button()
            render_printable_table(branch_emps[["كود الموظف", "اسم الموظف", "الوظيفة", "القسم", "الراتب الأساسي"]])
        else:
            st.info(f"لا توجد موظفين مسجلين في فرع {branch}.")
        st.markdown("<hr style='border: 0.5px dashed rgba(255,255,255,0.1); margin: 15px 0;'>", unsafe_allow_html=True)

elif choice == "تسجيل حضور وانصراف":
    st.subheader("⏱️ تسجيل حركة الحضور والانصراف")
    emp_names = st.session_state.employees["اسم الموظف"].tolist()
    if emp_names:
        st.markdown('<div class="entry-form-area">', unsafe_allow_html=True)
        with st.form("att_form_custom_time_full"):
            selected_emp = st.selectbox("اختر الموظف", emp_names)
            att_date = st.date_input("تاريخ الحركة", value=date.today())
            
            emp_info = st.session_state.employees[st.session_state.employees["اسم الموظف"] == selected_emp].iloc[0]
            c_job = emp_info["الوظيفة"]
            c_branch = emp_info["الفرع"]
            
            st.info(f"📍 الفرع: {c_branch} &nbsp;|&nbsp; 💼 الوظيفة: {c_job}")
            
            st.markdown("---")
            st.markdown("🕒 **المواعيد الرسمية للعمل:**")
            col_rs1, col_rs2, col_rs3 = st.columns(3)
            with col_rs1: start_h = st.selectbox("ساعة البداية الرسمية", list(range(1, 13)), index=7)
            with col_rs2: start_m = st.selectbox("دقيقة البداية (00-59)", list(range(0, 60)), index=0)
            with col_rs3: start_ampm = st.selectbox("فترة البداية", ["AM", "PM"], index=0)

            col_re1, col_re2, col_re3 = st.columns(3)
            with col_re1: end_h = st.selectbox("ساعة النهاية الرسمية", list(range(1, 13)), index=3)
            with col_re2: end_m = st.selectbox("دقيقة النهاية (00-59)", list(range(0, 60)), index=0)
            with col_re3: end_ampm = st.selectbox("فترة النهاية", ["AM", "PM"], index=1)

            grace_period_min = st.number_input("فترة السماح (بالدقائق)", min_value=0, max_value=60, value=15)

            st.markdown("---")
            st.markdown("⏰ **الأوقات الفعلية للحضور والانصراف:**")
            
            col_in1, col_in2, col_in3 = st.columns(3)
            with col_in1: act_in_h = st.selectbox("ساعة الحضور الفعلي", list(range(1, 13)), index=7, key="ain_h")
            with col_in2: act_in_m = st.selectbox("دقيقة الحضور الفعلي (00-59)", list(range(0, 60)), index=0, key="ain_m")
            with col_in3: act_in_ampm = st.selectbox("فترة الحضور الفعلي", ["AM", "PM"], index=0, key="ain_ap")

            col_out1, col_out2, col_out3 = st.columns(3)
            with col_out1: act_out_h = st.selectbox("ساعة الانصراف الفعلي", list(range(1, 13)), index=3, key="aout_h")
            with col_out2: act_out_m = st.selectbox("دقيقة الانصراف الفعلي (00-59)", list(range(0, 60)), index=0, key="aout_m")
            with col_out3: act_out_ampm = st.selectbox("فترة الانصراف الفعلي", ["AM", "PM"], index=1, key="aout_ap")

            att_status = st.selectbox("حالة الحضور", ["حضور منتظم", "إجازة أسبوعية", "إجازة سنوية", "إجازة مرضية", "إجازة بدون أجر", "غياب"])
            
            if st.form_submit_button("💾 حساب تلقائي وحفظ الحركة", use_container_width=True):
                start_work_str = f"{start_h:02d}:{start_m:02d} {start_ampm}"
                end_work_str = f"{end_h:02d}:{end_m:02d} {end_ampm}"
                actual_in_str = f"{act_in_h:02d}:{act_in_m:02d} {act_in_ampm}"
                actual_out_str = f"{act_out_h:02d}:{act_out_m:02d} {act_out_ampm}"

                def to_minutes(h, m, ampm):
                    hour_24 = h % 12
                    if ampm == "PM":
                        hour_24 += 12
                    return hour_24 * 60 + m

                start_total_min = to_minutes(start_h, start_m, start_ampm)
                end_total_min = to_minutes(end_h, end_m, end_ampm)
                act_in_total_min = to_minutes(act_in_h, act_in_m, act_in_ampm)
                act_out_total_min = to_minutes(act_out_h, act_out_m, act_out_ampm)

                worked_minutes = act_out_total_min - act_in_total_min
                if worked_minutes < 0:
                    worked_minutes += 24 * 60

                standard_minutes = end_total_min - start_total_min
                if standard_minutes < 0:
                    standard_minutes += 24 * 60

                overtime_min = 0
                tardy_min = 0

                in_diff = act_in_total_min - start_total_min
                if in_diff > grace_period_min:
                    tardy_min += (in_diff - grace_period_min)

                diff_total = worked_minutes - standard_minutes
                if diff_total > 0:
                    overtime_min = int(diff_total)
                elif diff_total < 0:
                    shortage = abs(diff_total)
                    if shortage > grace_period_min:
                        tardy_min += int(shortage)

                new_att = {
                    "التاريخ": str(att_date),
                    "كود الموظف": emp_info["كود الموظف"],
                    "اسم الموظف": selected_emp,
                    "الوظيفة": c_job,
                    "الفرع": c_branch,
                    "بداية العمل الرسمية": start_work_str,
                    "نهاية العمل الرسمية": end_work_str,
                    "وقت الحضور الفعلي": actual_in_str,
                    "وقت الانصراف الفعلي": actual_out_str,
                    "فترة السماح (دقيقة)": grace_period_min,
                    "الحالة": att_status,
                    "التأخير (دقيقة)": int(tardy_min),
                    "إضافي (دقيقة)": int(overtime_min)
                }
                
                st.session_state.attendance = st.session_state.attendance[
                    ~((st.session_state.attendance["كود الموظف"] == emp_info["كود الموظف"]) & 
                      (st.session_state.attendance["التاريخ"] == str(att_date)))
                ]
                
                st.session_state.attendance = pd.concat([st.session_state.attendance, pd.DataFrame([new_att])], ignore_index=True)
                auto_save_data()
                st.success(f"تم الحساب والحفظ بنجاح! (إضافي: {overtime_min} دقيقة | تأخير: {tardy_min} دقيقة)")
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

elif choice == "سجل الحضور والانصراف":
    st.subheader("⏱️ سجل الحضور والانصراف الشامل")
    render_print_button()
    
    clean_att_df = st.session_state.attendance.copy()
    expected_cols = [
        "التاريخ", "كود الموظف", "اسم الموظف", "الوظيفة", "الفرع", 
        "بداية العمل الرسمية", "نهاية العمل الرسمية", "وقت الحضور الفعلي", "وقت الانصراف الفعلي", 
        "فترة السماح (دقيقة)", "الحالة", "التأخير (دقيقة)", "إضافي (دقيقة)"
    ]
    for col in expected_cols:
        if col not in clean_att_df.columns:
            clean_att_df[col] = 0 if "(دقيقة)" in col else ""
    clean_att_df = clean_att_df[expected_cols].fillna(0)
    render_printable_table(clean_att_df)

elif choice == "تعديل أو حذف حركة حضور":
    st.subheader("✏️ تعديل أو حذف حركة حضور والانصراف")
    if not st.session_state.attendance.empty:
        att_indices = st.session_state.attendance.index.tolist()
        selected_att_idx = st.selectbox("اختر رقم السجل للتعديل أو الحذف", att_indices)
        record = st.session_state.attendance.loc[selected_att_idx]
        
        st.markdown('<div class="entry-form-area">', unsafe_allow_html=True)
        with st.form("edit_att_form_comprehensive"):
            emp_names = st.session_state.employees["اسم الموظف"].tolist()
            current_emp_idx = emp_names.index(record["اسم الموظف"]) if record["اسم الموظف"] in emp_names else 0
            edit_emp = st.selectbox("اسم الموظف", emp_names, index=current_emp_idx)
            
            try:
                default_date = datetime.strptime(str(record["التاريخ"]), "%Y-%m-%d").date()
            except:
                default_date = date.today()
            edit_date = st.date_input("تاريخ الحركة", value=default_date)
            
            st.markdown("---")
            edit_start_work = st.text_input("بداية العمل الرسمية", value=str(record["بداية العمل الرسمية"]))
            edit_end_work = st.text_input("نهاية العمل الرسمية", value=str(record["نهاية العمل الرسمية"]))
            edit_grace = st.number_input("فترة السماح (دقيقة)", value=int(record.get("فترة السماح (دقيقة)", 15)))

            st.markdown("---")
            edit_act_in = st.text_input("وقت الحضور الفعلي", value=str(record["وقت الحضور الفعلي"]))
            edit_act_out = st.text_input("وقت الانصراف الفعلي", value=str(record["وقت الانصراف الفعلي"]))
            
            status_list = ["حضور منتظم", "إجازة أسبوعية", "إجازة سنوية", "إجازة مرضية", "إجازة بدون أجر", "غياب"]
            current_stat_idx = status_list.index(record["الحالة"]) if record["الحالة"] in status_list else 0
            edit_status = st.selectbox("حالة الحضور", status_list, index=current_stat_idx)
            
            edit_tardy = st.number_input("التأخير (دقيقة)", value=int(record["التأخير (دقيقة)"]))
            edit_over = st.number_input("إضافي (دقيقة)", value=int(record["إضافي (دقيقة)"]))
            
            col_eb1, col_eb2 = st.columns(2)
            with col_eb1:
                if st.form_submit_button("💾 حفظ كافة التعديلات", use_container_width=True):
                    emp_row = st.session_state.employees[st.session_state.employees["اسم الموظف"] == edit_emp].iloc[0]
                    st.session_state.attendance.at[selected_att_idx, "اسم الموظف"] = edit_emp
                    st.session_state.attendance.at[selected_att_idx, "كود الموظف"] = emp_row["كود الموظف"]
                    st.session_state.attendance.at[selected_att_idx, "الوظيفة"] = emp_row["الوظيفة"]
                    st.session_state.attendance.at[selected_att_idx, "الفرع"] = emp_row["الفرع"]
                    st.session_state.attendance.at[selected_att_idx, "التاريخ"] = str(edit_date)
                    st.session_state.attendance.at[selected_att_idx, "بداية العمل الرسمية"] = edit_start_work
                    st.session_state.attendance.at[selected_att_idx, "نهاية العمل الرسمية"] = edit_end_work
                    st.session_state.attendance.at[selected_att_idx, "فترة السماح (دقيقة)"] = edit_grace
                    st.session_state.attendance.at[selected_att_idx, "وقت الحضور الفعلي"] = edit_act_in
                    st.session_state.attendance.at[selected_att_idx, "وقت الانصراف الفعلي"] = edit_act_out
                    st.session_state.attendance.at[selected_att_idx, "الحالة"] = edit_status
                    st.session_state.attendance.at[selected_att_idx, "التأخير (دقيقة)"] = edit_tardy
                    st.session_state.attendance.at[selected_att_idx, "إضافي (دقيقة)"] = edit_over
                    
                    auto_save_data()
                    st.success("تم تحديث كافة حقول سجل الحضور والانصراف بنجاح!")
                    st.rerun()
            with col_eb2:
                if st.form_submit_button("🗑️ حذف السجل", use_container_width=True):
                    st.session_state.attendance = st.session_state.attendance.drop(selected_att_idx).reset_index(drop=True)
                    auto_save_data()
                    st.success("تم حذف السجل بنجاح!")
                    st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("لا توجد سجلات حضور متاحة للتعديل.")

elif choice == "تسجيل طلب إجازة":
    st.subheader("📝 تقديم طلب إجازة جديد")
    emp_names = st.session_state.employees["اسم الموظف"].tolist()
    if emp_names:
        st.markdown('<div class="entry-form-area">', unsafe_allow_html=True)
        with st.form("req_form_full"):
            emp_r = st.selectbox("الموظف الطالب", emp_names)
            r_type = st.selectbox("نوع الإجازة المطلوبة", [
                "إجازة سنوية", 
                "إجازة أسبوعية / عارضة", 
                "إجازة مرضية", 
                "إجازة بدون أجر"
            ])
            col_d1, col_d2 = st.columns(2)
            with col_d1: d_from = st.date_input("من تاريخ")
            with col_d2: d_to = st.date_input("إلى تاريخ")
            r_reas = st.text_area("السبب / ملاحظات الإجازة")
            
            if st.form_submit_button("📤 إرسال طلب الإجازة", use_container_width=True):
                days = (d_to - d_from).days + 1
                emp_data = st.session_state.employees[st.session_state.employees["اسم الموظف"] == emp_r].iloc[0]
                new_req = {
                    "رقم الطلب": int(st.session_state.requests["رقم الطلب"].max() + 1) if not st.session_state.requests.empty else 101, 
                    "كود الموظف": emp_data["كود الموظف"], 
                    "اسم الموظف": emp_r, 
                    "الوظيفة": emp_data["الوظيفة"], 
                    "الفرع": emp_data["الفرع"], 
                    "نوع الإجازة": r_type, 
                    "من تاريخ": str(d_from), 
                    "إلى تاريخ": str(d_to), 
                    "عدد الأيام": days, 
                    "السبب": r_reas, 
                    "الحالة": "قيد الانتظار"
                }
                st.session_state.requests = pd.concat([st.session_state.requests, pd.DataFrame([new_req])], ignore_index=True)
                auto_save_data()
                st.success("تم إرسال طلب الإجازة بنجاح!")
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

elif choice == "سجل طلبات قيد الانتظار":
    st.subheader("⏳ سجل الطلبات قيد الانتظار")
    render_print_button()
    pending_df = st.session_state.requests[st.session_state.requests["الحالة"] == "قيد الانتظار"] if not st.session_state.requests.empty else pd.DataFrame()
    render_printable_table(pending_df)
    if not pending_df.empty:
        st.markdown("### ⚙️ اتخاذ قرار على الطلبات")
        req_ids = pending_df["رقم الطلب"].tolist()
        selected_r_id = st.selectbox("اختر رقم الطلب للاعتماد أو الرفض", req_ids)
        col_act1, col_act2 = st.columns(2)
        with col_act1:
            if st.button("✅ قبول الطلب واعتماد الأرصدة", use_container_width=True):
                idx = st.session_state.requests[st.session_state.requests["رقم الطلب"] == selected_r_id].index[0]
                st.session_state.requests.at[idx, "الحالة"] = "مقبول"
                auto_save_data()
                st.success("تم قبول الطلب بنجاح!")
                st.rerun()
        with col_act2:
            if st.button("❌ رفض الطلب", use_container_width=True):
                idx = st.session_state.requests[st.session_state.requests["رقم الطلب"] == selected_r_id].index[0]
                st.session_state.requests.at[idx, "الحالة"] = "مرفوض"
                auto_save_data()
                st.warning("تم رفض الطلب.")
                st.rerun()

elif choice == "سجل الطلبات المقبولة":
    st.subheader("✅ سجل الطلبات المقبولة")
    render_print_button()
    render_printable_table(st.session_state.requests[st.session_state.requests["الحالة"] == "مقبول"] if not st.session_state.requests.empty else pd.DataFrame())

elif choice == "سجل الطلبات المرفوضة":
    st.subheader("❌ سجل الطلبات المرفوضة")
    render_print_button()
    render_printable_table(st.session_state.requests[st.session_state.requests["الحالة"] == "مرفوض"] if not st.session_state.requests.empty else pd.DataFrame())

elif choice == "تعديل أو حذف طلب إجازة":
    st.subheader("✏️ تعديل أو حذف طلب إجازة")
    if not st.session_state.requests.empty:
        req_ids = st.session_state.requests["رقم الطلب"].tolist()
        sel_req_id = st.selectbox("اختر رقم الطلب", req_ids)
        r_rec = st.session_state.requests[st.session_state.requests["رقم الطلب"] == sel_req_id].iloc[0]
        r_idx = st.session_state.requests[st.session_state.requests["رقم الطلب"] == sel_req_id].index[0]
        
        st.markdown('<div class="entry-form-area">', unsafe_allow_html=True)
        with st.form("edit_req_form_comprehensive"):
            emp_names = st.session_state.employees["اسم الموظف"].tolist()
            cur_emp_r = emp_names.index(r_rec["اسم الموظف"]) if r_rec["اسم الموظف"] in emp_names else 0
            edit_req_emp = st.selectbox("الموظف الطالب", emp_names, index=cur_emp_r)
            
            types_list = ["إجازة سنوية", "إجازة أسبوعية / عارضة", "إجازة مرضية", "إجازة بدون أجر"]
            cur_type_idx = types_list.index(r_rec["نوع الإجازة"]) if r_rec["نوع الإجازة"] in types_list else 0
            edit_req_type = st.selectbox("نوع الإجازة المطلوبة", types_list, index=cur_type_idx)
            
            try:
                d_from_def = datetime.strptime(str(r_rec["من تاريخ"]), "%Y-%m-%d").date()
            except:
                d_from_def = date.today()
            try:
                d_to_def = datetime.strptime(str(r_rec["إلى تاريخ"]), "%Y-%m-%d").date()
            except:
                d_to_def = date.today()
                
            col_ed1, col_ed2 = st.columns(2)
            with col_ed1: edit_d_from = st.date_input("من تاريخ", value=d_from_def)
            with col_ed2: edit_d_to = st.date_input("إلى تاريخ", value=d_to_def)
            
            edit_reason = st.text_area("السبب / ملاحظات الإجازة", value=str(r_rec["السبب"]))
            
            stat_list_req = ["قيد الانتظار", "مقبول", "مرفوض"]
            cur_stat_r = stat_list_req.index(r_rec["الحالة"]) if r_rec["الحالة"] in stat_list_req else 0
            edit_req_stat = st.selectbox("حالة الطلب", stat_list_req, index=cur_stat_r)
            
            col_er1, col_er2 = st.columns(2)
            with col_er1:
                if st.form_submit_button("💾 حفظ كافة تعديلات الطلب", use_container_width=True):
                    days_calc = (edit_d_to - edit_d_from).days + 1
                    emp_row_r = st.session_state.employees[st.session_state.employees["اسم الموظف"] == edit_req_emp].iloc[0]
                    
                    st.session_state.requests.at[r_idx, "اسم الموظف"] = edit_req_emp
                    st.session_state.requests.at[r_idx, "كود الموظف"] = emp_row_r["كود الموظف"]
                    st.session_state.requests.at[r_idx, "الوظيفة"] = emp_row_r["الوظيفة"]
                    st.session_state.requests.at[r_idx, "الفرع"] = emp_row_r["الفرع"]
                    st.session_state.requests.at[r_idx, "نوع الإجازة"] = edit_req_type
                    st.session_state.requests.at[r_idx, "من تاريخ"] = str(edit_d_from)
                    st.session_state.requests.at[r_idx, "إلى تاريخ"] = str(edit_d_to)
                    st.session_state.requests.at[r_idx, "عدد الأيام"] = days_calc
                    st.session_state.requests.at[r_idx, "السبب"] = edit_reason
                    st.session_state.requests.at[r_idx, "الحالة"] = edit_req_stat
                    
                    auto_save_data()
                    st.success("تم تحديث طلب الإجازة بكامل مدخلاته بنجاح!")
                    st.rerun()
            with col_er2:
                if st.form_submit_button("🗑️ حذف الطلب", use_container_width=True):
                    st.session_state.requests = st.session_state.requests.drop(r_idx).reset_index(drop=True)
                    auto_save_data()
                    st.success("تم حذف الطلب بنجاح!")
                    st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("لا توجد طلبات إجازة مسجلة.")

elif choice == "تسجيل معاملة مالية":
    st.subheader("💰 تسجيل معاملة مالية جديدة")
    emp_names = st.session_state.employees["اسم الموظف"].tolist()
    if emp_names:
        st.markdown('<div class="entry-form-area">', unsafe_allow_html=True)
        with st.form("fin_form_with_date"):
            emp_f = st.selectbox("الموظف", emp_names)
            trans_date = st.date_input("تاريخ المعاملة المالية", value=date.today())
            t_type = st.selectbox("نوع المعاملة", ["سلفة", "جزاء (خصم)", "غياب (خصم أيام)", "مكافأة (إضافي)", "بدلات"])
            t_amt = st.number_input("المبلغ / القيمة", min_value=0.0, value=100.0)
            t_reas = st.text_input("البيان / السبب")
            
            if st.form_submit_button("حفظ المعاملة المالية", use_container_width=True):
                emp_data = st.session_state.employees[st.session_state.employees["اسم الموظف"] == emp_f].iloc[0]
                new_f = {
                    "التاريخ": str(trans_date), 
                    "كود الموظف": emp_data["كود الموظف"], 
                    "اسم الموظف": emp_f, 
                    "الفرع": emp_data["الفرع"], 
                    "النوع": t_type, 
                    "المبلغ / القيمة": t_amt, 
                    "البيان / السبب": t_reas
                }
                st.session_state.financial_transactions = pd.concat([st.session_state.financial_transactions, pd.DataFrame([new_f])], ignore_index=True)
                auto_save_data()
                st.success("تم حفظ المعاملة المالية وتاريخها بنجاح!")
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

elif choice == "سجل المعاملات المالية":
    st.subheader("💰 سجل المعاملات المالية")
    render_print_button()
    render_printable_table(st.session_state.financial_transactions)

elif choice == "تعديل أو حذف معاملة مالية":
    st.subheader("✏️ تعديل أو حذف معاملة مالية")
    if not st.session_state.financial_transactions.empty:
        fin_indices = st.session_state.financial_transactions.index.tolist()
        sel_fin_idx = st.selectbox("اختر المعاملة المالية", fin_indices)
        f_rec = st.session_state.financial_transactions.loc[sel_fin_idx]
        
        st.markdown('<div class="entry-form-area">', unsafe_allow_html=True)
        with st.form("edit_fin_form_comprehensive"):
            emp_names = st.session_state.employees["اسم الموظف"].tolist()
            cur_emp_f = emp_names.index(f_rec["اسم الموظف"]) if f_rec["اسم الموظف"] in emp_names else 0
            edit_fin_emp = st.selectbox("الموظف", emp_names, index=cur_emp_f)
            
            try:
                trans_date_def = datetime.strptime(str(f_rec["التاريخ"]), "%Y-%m-%d").date()
            except:
                trans_date_def = date.today()
            edit_fin_date = st.date_input("تاريخ المعاملة المالية", value=trans_date_def)
            
            fin_types = ["سلفة", "جزاء (خصم)", "غياب (خصم أيام)", "مكافأة (إضافي)", "بدلات"]
            cur_fin_type = fin_types.index(f_rec["النوع"]) if f_rec["النوع"] in fin_types else 0
            new_type = st.selectbox("نوع المعاملة", fin_types, index=cur_fin_type)
            
            new_amt = st.number_input("المبلغ / القيمة", value=float(f_rec["المبلغ / القيمة"]))
            new_reas = st.text_input("البيان / السبب", value=str(f_rec["البيان / السبب"]))
            
            col_ef1, col_ef2 = st.columns(2)
            with col_ef1:
                if st.form_submit_button("💾 حفظ كافة تعديلات المعاملة", use_container_width=True):
                    emp_row_f = st.session_state.employees[st.session_state.employees["اسم الموظف"] == edit_fin_emp].iloc[0]
                    
                    st.session_state.financial_transactions.at[sel_fin_idx, "اسم الموظف"] = edit_fin_emp
                    st.session_state.financial_transactions.at[sel_fin_idx, "كود الموظف"] = emp_row_f["كود الموظف"]
                    st.session_state.financial_transactions.at[sel_fin_idx, "الفرع"] = emp_row_f["الفرع"]
                    st.session_state.financial_transactions.at[sel_fin_idx, "التاريخ"] = str(edit_fin_date)
                    st.session_state.financial_transactions.at[sel_fin_idx, "النوع"] = new_type
                    st.session_state.financial_transactions.at[sel_fin_idx, "المبلغ / القيمة"] = new_amt
                    st.session_state.financial_transactions.at[sel_fin_idx, "البيان / السبب"] = new_reas
                    
                    auto_save_data()
                    st.success("تم تحديث المعاملة المالية بكامل مدخلاتها وتاريخها بنجاح!")
                    st.rerun()
            with col_ef2:
                if st.form_submit_button("🗑️ حذف المعاملة", use_container_width=True):
                    st.session_state.financial_transactions = st.session_state.financial_transactions.drop(sel_fin_idx).reset_index(drop=True)
                    auto_save_data()
                    st.success("تم حذف المعاملة بنجاح!")
                    st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("لا توجد معاملات مالية مسجلة.")

elif choice == "كشف الرواتب والمستحقات الشامل":
    st.subheader("💰 إدارة كشف الرواتب والطباعة المستقلة لكل جزء على حدة")
    
    payroll_df = st.session_state.employees[["كود الموظف", "اسم الموظف", "الوظيفة", "القسم", "الفرع", "الراتب الأساسي"]].copy()
    
    if not st.session_state.financial_transactions.empty:
        fin_df = st.session_state.financial_transactions.copy()
        fin_df["مكافآت وبدلات"] = fin_df.apply(lambda r: r["المبلغ / القيمة"] if r["النوع"] in ["مكافأة (إضافي)", "بدلات"] else 0, axis=1)
        fin_df["سلف وجزاءات وغياب"] = fin_df.apply(lambda r: r["المبلغ / القيمة"] if r["النوع"] in ["سلفة", "جزاء (خصم)", "غياب (خصم أيام)"] else 0, axis=1)
        
        fin_grouped = fin_df.groupby("كود الموظف")[["مكافآت وبدلات", "سلف وجزاءات وغياب"]].sum().reset_index()
        payroll_df = payroll_df.merge(fin_grouped, on="كود الموظف", how="left")
    else:
        payroll_df["مكافآت وبدلات"] = 0.0
        payroll_df["سلف وجزاءات وغياب"] = 0.0

    if not st.session_state.attendance.empty:
        att_agg = st.session_state.attendance.groupby("كود الموظف")[["التأخير (دقيقة)", "إضافي (دقيقة)"]].sum().reset_index()
        payroll_df = payroll_df.merge(att_agg, on="كود الموظف", how="left")
    else:
        payroll_df["التأخير (دقيقة)"] = 0
        payroll_df["إضافي (دقيقة)"] = 0

    payroll_df = payroll_df.fillna(0)

    minute_rate = payroll_df["الراتب الأساسي"] / 10000
    payroll_df["قيمة الإضافي"] = payroll_df["إضافي (دقيقة)"] * minute_rate
    payroll_df["قيمة التأخير والاستقطاع"] = payroll_df["التأخير (دقيقة)"] * minute_rate

    payroll_df["إجمالي المستحقات"] = payroll_df["الراتب الأساسي"] + payroll_df["قيمة الإضافي"] + payroll_df["مكافآت وبدلات"]
    payroll_df["إجمالي الاستقطاعات"] = payroll_df["سلف وجزاءات وغياب"] + payroll_df["قيمة التأخير والاستقطاع"]
    payroll_df["صافي الراتب"] = payroll_df["إجمالي المستحقات"] - payroll_df["إجمالي الاستقطاعات"]

    display_payroll_cols = [
        "كود الموظف", "اسم الموظف", "الوظيفة", "الفرع", "الراتب الأساسي",
        "إضافي (دقيقة)", "قيمة الإضافي", "مكافآت وبدلات", "إجمالي المستحقات",
        "التأخير (دقيقة)", "قيمة التأخير والاستقطاع", "سلف وجزاءات وغياب", "إجمالي الاستقطاعات",
        "صافي الراتب"
    ]

    # الجزء الأول: ملخص الرواتب حسب الفروع
    st.markdown("### 🏢 1. ملخص الرواتب حسب الفروع (مستقل للطباعة)")
    branch_summary = payroll_df.groupby("الفرع").agg({
        "الراتب الأساسي": "sum",
        "إجمالي المستحقات": "sum",
        "إجمالي الاستقطاعات": "sum",
        "صافي الراتب": "sum"
    }).reset_index()
    render_print_button()
    render_printable_table(branch_summary)

    st.markdown("---")
    
    # الجزء الثاني: الكشف التفصيلي للرواتب لكافة الموظفين
    st.markdown("### 👥 2. الكشف التفصيلي للرواتب لكافة الموظفين (مستقل للطباعة)")
    render_print_button()
    render_printable_table(payroll_df[display_payroll_cols])

    st.markdown("---")
    
    # الجزء الثالث: كشف حساب تفصيلي لموظف محدد (على حدة)
    st.markdown("### 🧾 3. كشف حساب تفصيلي لموظف محدد (على حدة للطباعة)")
    selected_emp_acc = st.selectbox("اختر الموظف لطباعة كشف حسابه التفصيلي", payroll_df["اسم الموظف"].tolist())
    if selected_emp_acc:
        emp_acc_row = payroll_df[payroll_df["اسم الموظف"] == selected_emp_acc].iloc[0]
        render_print_button()
        st.markdown(f"""
        <div class="glass-card printable-right-align">
            <h4>📄 كشف حساب الموظف: {emp_acc_row['اسم الموظف']} ({emp_acc_row['الوظيفة']} - فرع {emp_acc_row['الفرع']})</h4>
            <p><b>الراتب الأساسي:</b> {emp_acc_row['الراتب الأساسي']:,.2f} ج.م</p>
            <p><b>إجمالي المستحقات (تشمل الإضافي والبدلات والمكافآت):</b> {emp_acc_row['إجمالي المستحقات']:,.2f} ج.م</p>
            <p><b>إجمالي الاستقطاعات (تشمل التأخير والسلف والجزاءات والغياب):</b> {emp_acc_row['إجمالي الاستقطاعات']:,.2f} ج.م</p>
            <p><b>صافي الراتب المستحق:</b> <span style="color: #10B981; font-size: 18px;">{emp_acc_row['صافي الراتب']:,.2f} ج.م</span></p>
        </div>
        """, unsafe_allow_html=True)

elif choice == "إضافة موظف جديد":
    st.subheader("👥 إضافة موظف جديد (مع رفع مسوغات التعيين PDF / صور)")
    st.markdown('<div class="entry-form-area">', unsafe_allow_html=True)
    
    uploaded_doc = st.file_uploader("📂 تحميل مسوغات التعيين (PDF أو صور)", type=["pdf", "png", "jpg", "jpeg"])
    
    with st.form("new_emp_full"):
        col_ne1, col_ne2 = st.columns(2)
        with col_ne1:
            c_code = st.text_input("كود الموظف", value="EMP002")
            c_name = st.text_input("اسم الموظف")
            c_job = st.text_input("الوظيفة")
        with col_ne2:
            c_dept = st.text_input("القسم")
            c_branch = st.text_input("الفرع")
            c_sal = st.number_input("الراتب الأساسي", min_value=0.0, value=5000.0)
        
        st.markdown("---")
        st.markdown("📋 **أرصدة الإجازات الافتتاحية:**")
        col_b1, col_b2, col_b3, col_b4 = st.columns(4)
        with col_b1: ann_tot = st.number_input("رصيد سنوي (إجمالي)", value=21)
        with col_b2: week_tot = st.number_input("رصيد أسبوعي (إجمالي)", value=4)
        with col_b3: off_tot = st.number_input("رصيد رسمي (إجمالي)", value=10)
        with col_b4: sick_tot = st.number_input("إجازات مرضية (أيام)", value=0)
        
        if st.form_submit_button("💾 حفظ وإضافة الموظف مع مسوغاته", use_container_width=True):
            doc_path_str = ""
            if uploaded_doc is not None:
                file_ext = uploaded_doc.name.split(".")[-1].lower()
                doc_filename = f"{c_code}_{c_name.replace(' ', '_')}_docs.{file_ext}"
                doc_path = os.path.join(DOCS_DIR, doc_filename)
                with open(doc_path, "wb") as f:
                    f.write(uploaded_doc.getbuffer())
                doc_path_str = doc_path

            new_e = {
                "كود الموظف": c_code, 
                "اسم الموظف": c_name, 
                "الوظيفة": c_job, 
                "القسم": c_dept, 
                "الفرع": c_branch, 
                "صلاحية الموظف": "إدخال", 
                "الراتب الأساسي": c_sal,
                "مسوغات التعيين": doc_path_str,
                "رصيد سنوي (إجمالي)": ann_tot, "سنوي مستهلك": 0, "سنوي متبقي": ann_tot, 
                "رصيد أسبوعي (إجمالي)": week_tot, "أسبوعي مستهلك": 0, "أسبوعي متبقي": week_tot, 
                "رصيد رسمي (إجمالي)": off_tot, "رسمي مستهلك": 0, "رسمي متبقي": off_tot, 
                "إجازات مرضية (أيام)": sick_tot
            }
            st.session_state.employees = pd.concat([st.session_state.employees, pd.DataFrame([new_e])], ignore_index=True)
            auto_save_data()
            st.success("تمت إضافة الموظف ومسوغات تعيينه بنجاح!")
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

elif choice == "سجل الموظفين والأرصدة الشاملة":
    st.subheader("👥 سجل الموظفين والأرصدة الشاملة")
    render_print_button()
    
    col_f1, col_f2, col_f3 = st.columns(3)
    with col_f1:
        branch_filter = st.selectbox("فلترة حسب الفرع", ["الكل"] + st.session_state.employees["الفرع"].unique().tolist())
    with col_f2:
        job_filter = st.selectbox("فلترة حسب الوظيفة", ["الكل"] + st.session_state.employees["الوظيفة"].unique().tolist())
    with col_f3:
        name_search = st.text_input("بحث باسم الموظف")

    filtered_emps = st.session_state.employees.copy()
    if branch_filter != "الكل":
        filtered_emps = filtered_emps[filtered_emps["الفرع"] == branch_filter]
    if job_filter != "الكل":
        filtered_emps = filtered_emps[filtered_emps["الوظيفة"] == job_filter]
    if name_search.strip() != "":
        filtered_emps = filtered_emps[filtered_emps["اسم الموظف"].str.contains(name_search.strip(), na=False)]

    render_printable_table(filtered_emps)

elif choice == "تعديل أو حذف موظف":
    st.subheader("✏️ تعديل أو حذف بيانات موظف")
    emp_names = st.session_state.employees["اسم الموظف"].tolist()
    if emp_names:
        sel_emp_edit = st.selectbox("اختر الموظف للتعديل أو الحذف", emp_names)
        emp_row = st.session_state.employees[st.session_state.employees["اسم الموظف"] == sel_emp_edit].iloc[0]
        emp_idx = st.session_state.employees[st.session_state.employees["اسم الموظف"] == sel_emp_edit].index[0]
        
        if emp_row.get("مسوغات التعيين", "") and os.path.exists(emp_row["مسوغات التعيين"]):
            st.info(f"📂 مسوغات التعيين مرفوعة ومحفوظة باسم الملف: {emp_row['مسوغات التعيين']}")

        st.markdown('<div class="entry-form-area">', unsafe_allow_html=True)
        with st.form("edit_emp_form_full"):
            e_job = st.text_input("الوظيفة", value=str(emp_row["الوظيفة"]))
            e_dept = st.text_input("القسم", value=str(emp_row["القسم"]))
            e_branch = st.text_input("الفرع", value=str(emp_row["الفرع"]))
            e_sal = st.number_input("الراتب الأساسي", value=float(emp_row["الراتب الأساسي"]))
            
            col_ee1, col_ee2 = st.columns(2)
            with col_ee1:
                if st.form_submit_button("💾 حفظ التعديلات", use_container_width=True):
                    st.session_state.employees.at[emp_idx, "الوظيفة"] = e_job
                    st.session_state.employees.at[emp_idx, "القسم"] = e_dept
                    st.session_state.employees.at[emp_idx, "الفرع"] = e_branch
                    st.session_state.employees.at[emp_idx, "الراتب الأساسي"] = e_sal
                    auto_save_data()
                    st.success("تم تحديث بيانات الموظف بكامل مدخلاتها بنجاح!")
                    st.rerun()
            with col_ee2:
                if st.form_submit_button("🗑️ حذف الموظف", use_container_width=True):
                    st.session_state.employees = st.session_state.employees.drop(emp_idx).reset_index(drop=True)
                    auto_save_data()
                    st.success("تم حذف الموظف بنجاح!")
                    st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

elif choice == "إضافة مستخدم جديد":
    st.subheader("➕ إضافة مستخدم جديد للنظام والصلاحيات")
    st.markdown('<div class="entry-form-area">', unsafe_allow_html=True)
    with st.form("add_user_form_with_status"):
        u_name = st.text_input("اسم المستخدم (Login Username)")
        u_full = st.text_input("الاسم الكامل")
        u_branch = st.text_input("الفرع التابع")
        u_dept = st.text_input("القسم التابع")
        u_role = st.selectbox("الصلاحية الممنوحة", ["مشرف عام (Admin)", "مدير فرع", "اعتماد الطلبات", "إدخال بيانات"])
        u_status = st.selectbox("حالة المستخدم", ["نشط", "إيقاف"])
        u_email = st.text_input("البريد الإلكتروني")
        u_pin = st.text_input("الرسم السري (Pattern / PIN)", placeholder="مثل: 1-2-3")
        
        if st.form_submit_button("💾 حفظ المستخدم الجديد", use_container_width=True):
            new_u = {
                "اسم المستخدم": u_name,
                "الاسم الكامل": u_full,
                "الفرع التابع": u_branch,
                "القسم التابع": u_dept,
                "الصلاحية": u_role,
                "البريد الإلكتروني": u_email,
                "الحالة": u_status,
                "الرسم السري": u_pin
            }
            st.session_state.users = pd.concat([st.session_state.users, pd.DataFrame([new_u])], ignore_index=True)
            auto_save_data()
            st.success("تمت إضافة المستخدم وحالته بنجاح!")
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

elif choice == "إدارة المستخدمين والصلاحيات والسجل":
    st.subheader("🔒 شيت سجل المستخدمين")
    render_print_button()
    render_printable_table(st.session_state.users[["اسم المستخدم", "الاسم الكامل", "الفرع التابع", "القسم التابع", "الصلاحية", "البريد الإلكتروني", "الحالة"]])

elif choice == "تعديل أو حذف مستخدم":
    st.subheader("✏️ تعديل أو حذف مستخدم النظام")
    user_list = st.session_state.users["اسم المستخدم"].tolist()
    if user_list:
        sel_usr = st.selectbox("اختر اسم المستخدم", user_list)
        usr_idx = st.session_state.users[st.session_state.users["اسم المستخدم"] == sel_usr].index[0]
        usr_row = st.session_state.users.loc[usr_idx]
        st.markdown('<div class="entry-form-area">', unsafe_allow_html=True)
        with st.form("edit_user_form_full"):
            new_full_u = st.text_input("الاسم الكامل", value=str(usr_row["الاسم الكامل"]))
            new_role_u = st.selectbox("الصلاحية", ["مشرف عام (Admin)", "مدير فرع", "اعتماد الطلبات", "إدخال بيانات"], index=["مشرف عام (Admin)", "مدير فرع", "اعتماد الطلبات", "إدخال بيانات"].index(usr_row["الصلاحية"]) if usr_row["الصلاحية"] in ["مشرف عام (Admin)", "مدير فرع", "اعتماد الطلبات", "إدخال بيانات"] else 0)
            
            statuses = ["نشط", "إيقاف"]
            cur_status_idx = statuses.index(usr_row.get("الحالة", "نشط")) if usr_row.get("الحالة", "نشط") in statuses else 0
            new_status_u = st.selectbox("حالة المستخدم", statuses, index=cur_status_idx)
            
            new_pin_u = st.text_input("الرسم السري الجديد", value=str(usr_row["الرسم السري"]))
            
            col_uu1, col_uu2 = st.columns(2)
            with col_uu1:
                if st.form_submit_button("💾 حفظ تعديلات المستخدم", use_container_width=True):
                    st.session_state.users.at[usr_idx, "الاسم الكامل"] = new_full_u
                    st.session_state.users.at[usr_idx, "الصلاحية"] = new_role_u
                    st.session_state.users.at[usr_idx, "الحالة"] = new_status_u
                    st.session_state.users.at[usr_idx, "الرسم السري"] = new_pin_u
                    auto_save_data()
                    st.success("تم تحديث بيانات المستخدم وحالته بنجاح!")
                    st.rerun()
            with col_uu2:
                if st.form_submit_button("🗑️ حذف المستخدم", use_container_width=True):
                    st.session_state.users = st.session_state.users.drop(usr_idx).reset_index(drop=True)
                    auto_save_data()
                    st.success("تم حذف المستخدم بنجاح!")
                    st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

elif choice == "طباعة التقارير العامة":
    st.subheader("🖨️ مركز التقارير الشامل والطباعة المخصصة")
    render_print_button()
    
    rep_type = st.selectbox("اختر نوع التقرير للطباعة والعرض", [
        "سجل الحضور والانصراف (حسب الفرع أو الموظف)",
        "سجل الإجازات والطلبات (حسب الفرع أو الموظف)",
        "سجل المعاملات المالية (سلف، جزاءات، غياب، مكافآت، بدلات)",
        "تقرير كشف الرواتب والتفصيل الشامل (مع الإجماليات)",
        "سجل الموظفين الشامل",
        "شيت أسماء المستخدمين وحالتهم"
    ])
    
    if "الحضور والانصراف" in rep_type:
        st.markdown("#### ⏱️ تقرير الحضور والانصراف المخصص")
        col_r1, col_r2 = st.columns(2)
        with col_r1: rep_branch = st.selectbox("الفرع", ["الكل"] + st.session_state.employees["الفرع"].unique().tolist())
        with col_r2: rep_emp = st.selectbox("الموظف", ["الكل"] + st.session_state.employees["اسم الموظف"].tolist())
        
        rep_df = st.session_state.attendance.copy()
        if rep_branch != "الكل":
            rep_df = rep_df[rep_df["الفرع"] == rep_branch]
        if rep_emp != "الكل":
            rep_df = rep_df[rep_df["اسم الموظف"] == rep_emp]
        render_printable_table(rep_df)

    elif "الإجازات والطلبات" in rep_type:
        st.markdown("#### 📝 تقرير الإجازات والطلبات المخصص")
        col_r1, col_r2 = st.columns(2)
        with col_r1: rep_branch = st.selectbox("الفرع", ["الكل"] + st.session_state.employees["الفرع"].unique().tolist())
        with col_r2: rep_emp = st.selectbox("الموظف", ["الكل"] + st.session_state.employees["اسم الموظف"].tolist())
        
        rep_df = st.session_state.requests.copy()
        if rep_branch != "الكل":
            rep_df = rep_df[rep_df["الفرع"] == rep_branch]
        if rep_emp != "الكل":
            rep_df = rep_df[rep_df["اسم الموظف"] == rep_emp]
        render_printable_table(rep_df)

    elif "المعاملات المالية" in rep_type:
        st.markdown("#### 💰 تقرير المعاملات المالية")
        col_r1, col_r2 = st.columns(2)
        with col_r1: rep_branch = st.selectbox("الفرع", ["الكل"] + st.session_state.employees["الفرع"].unique().tolist())
        with col_r2: fin_type_filter = st.selectbox("نوع المعاملة", ["الكل", "سلفة", "جزاء (خصم)", "غياب (خصم أيام)", "مكافأة (إضافي)", "بدلات"])
        
        rep_df = st.session_state.financial_transactions.copy()
        if rep_branch != "الكل":
            rep_df = rep_df[rep_df["الفرع"] == rep_branch]
        if fin_type_filter != "الكل":
            rep_df = rep_df[rep_df["النوع"] == fin_type_filter]
        render_printable_table(rep_df)

    elif "تقرير كشف الرواتب" in rep_type:
        st.markdown("#### 💵 تقرير كشف الرواتب التفصيلي (مع الإجماليات)")
        payroll_df = st.session_state.employees[["كود الموظف", "اسم الموظف", "الوظيفة", "القسم", "الفرع", "الراتب الأساسي"]].copy()
        render_printable_table(payroll_df)
        
        tot_sal = payroll_df["الراتب الأساسي"].sum()
        st.markdown(f"""
        <div class="glass-card printable-right-align" style="margin-top: 12px;">
            <p><b>إجمالي عدد الموظفين:</b> {len(payroll_df)}</p>
            <p><b>إجمالي الرواتب الأساسية في التقرير:</b> <span style="color: #10B981; font-size: 18px;">{tot_sal:,.2f} ج.م</span></p>
        </div>
        """, unsafe_allow_html=True)

    elif "سجل الموظفين الشامل" in rep_type:
        st.markdown("#### 👥 تقرير سجل الموظفين")
        render_printable_table(st.session_state.employees)

    elif "شيت أسماء المستخدمين" in rep_type:
        st.markdown("#### 🔒 تقرير شيت المستخدمين")
        render_printable_table(st.session_state.users[["اسم المستخدم", "الاسم الكامل", "الفرع التابع", "القسم التابع", "الصلاحية", "البريد الإلكتروني", "الحالة"]])

elif choice == "اعدادات الشركة وبياناتها الشاملة":
    st.subheader("⚙️ إعدادات الشركة وبياناتها الشاملة")
    info = st.session_state.company_info
    
    st.markdown('<div class="entry-form-area">', unsafe_allow_html=True)
    uploaded_logo = st.file_uploader("🖼️ اختر صورة شعار الشركة (PNG أو JPG)", type=["png", "jpg", "jpeg"])
    
    with st.form("settings_full"):
        c_name_set = st.text_input("اسم الشركة", value=info.get("name", ""))
        c_lic_set = st.text_input("رقم الترخيص", value=info.get("license", ""))
        c_tax_set = st.text_input("البطاقة الضريبية", value=info.get("tax", ""))
        c_cr_set = st.text_input("السجل التجاري", value=info.get("cr", ""))
        c_addr_set = st.text_input("العنوان", value=info.get("address", ""))
        c_contact_set = st.text_input("أرقام التواصل", value=info.get("contact", ""))
        c_email_set = st.text_input("البريد الإلكتروني", value=info.get("email", ""))
        
        if st.form_submit_button("💾 حفظ إعدادات الشركة", use_container_width=True):
            info["name"] = c_name_set
            info["license"] = c_lic_set
            info["tax"] = c_tax_set
            info["cr"] = c_cr_set
            info["address"] = c_addr_set
            info["contact"] = c_contact_set
            info["email"] = c_email_set
            
            if uploaded_logo is not None:
                bytes_data = uploaded_logo.getvalue()
                encoded_img = base64.b64encode(bytes_data).decode("utf-8")
                file_ext = uploaded_logo.name.split(".")[-1].lower()
                mime_type = f"image/{file_ext}" if file_ext in ["png", "jpg", "jpeg"] else "image/png"
                info["logo"] = f"data:{mime_type};base64,{encoded_img}"
                
            auto_save_data()
            st.success("تم تحديث إعدادات الشركة وشعارها بنجاح!")
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

elif choice == "تصدير وتحميل Excel":
    st.markdown('<div class="entry-form-area">', unsafe_allow_html=True)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        st.session_state.employees.to_excel(writer, sheet_name='الموظفين', index=False)
        st.session_state.attendance.to_excel(writer, sheet_name='الحضور والانصراف', index=False)
        st.session_state.requests.to_excel(writer, sheet_name='الطلبات والإجازات', index=False)
        st.session_state.financial_transactions.to_excel(writer, sheet_name='المعاملات المالية', index=False)
        st.session_state.users.to_excel(writer, sheet_name='المستخدمين', index=False)
    output.seek(0)
    st.download_button("📥 تحميل ملف الإكسيل الشامل", data=output, file_name="system_full_data.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    st.markdown('</div>', unsafe_allow_html=True)

elif choice == "نسخة احتياطية واستعادة":
    st.subheader("💾 النسخ الاحتياطي والاستعادة")
    st.markdown('<div class="entry-form-area">', unsafe_allow_html=True)
    if os.path.exists(COMPANY_FILE):
        with open(COMPANY_FILE, "r", encoding="utf-8") as f:
            json_str = f.read()
        st.download_button("📥 تحميل النسخة الاحتياطية (JSON)", data=json_str, file_name="backup_company_data.json", mime="application/json")
    st.markdown('</div>', unsafe_allow_html=True)

elif choice == "مسح البيانات":
    st.subheader("⚠️ مسح وتصفير البيانات")
    st.warning("تحذير: هذه العملية ستقوم بإعادة تعيين كافة البيانات الافتراضية للشركة!")
    if st.button("🚨 تنفيذ المسح والتصفير الشامل"):
        if os.path.exists(COMPANY_FILE):
            os.remove(COMPANY_FILE)
        st.success("تم مسح البيانات بنجاح، جاري إعادة تشغيل النظام...")
        st.rerun()

else:
    st.info(f"عنصر القائمة ({choice}) جاهز للعمل بكامل ميزاته.")