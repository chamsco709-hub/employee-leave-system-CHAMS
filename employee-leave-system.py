import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import altair as alt
from datetime import datetime, date, time, timedelta
import io
import base64
import json
import os

# ضبط إعدادات الصفحة وتفعيل الواجهة الواسعة مع إبقاء القائمة الجانبية مفتوحة ومثبتة
st.set_page_config(
    page_title="النظام المتكامل لإدارة الموارد البشرية",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
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
        <div style="text-align: left; margin-bottom: 15px;">
            <button onclick="window.parent.print()" style="
                background: linear-gradient(135deg, #1E3A8A 0%, #3B82F6 100%);
                color: white;
                padding: 9px 20px;
                border: none;
                border-radius: 8px;
                font-size: 13px;
                font-weight: bold;
                cursor: pointer;
                box-shadow: 0 4px 10px rgba(37, 99, 235, 0.2);
                font-family: 'Tahoma', sans-serif;
                transition: all 0.3s ease;
            ">
                🖨️ طباعة السجل الحالي
            </button>
        </div>
    """, height=45)

# 🎨 تصميم CSS المتطور والانسيابي (Modern & Fluid UI Design)
st.markdown("""
    <style>
    header[data-testid="stHeader"] { visibility: hidden; height: 0px; }
    
    html, body, [class*="css"], .stMarkdown, div, span, p, h1, h2, h3, h4, h5, h6, label {
        font-family: 'Tahoma', 'Segoe UI', sans-serif !important;
        direction: rtl !important;
        text-align: right !important;
        color: #1E293B !important;
    }
    
    .block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 3rem !important;
        max-width: 100% !important;
        background-color: #F8FAFC !important;
    }
    
    /* 📋 القائمة الجانبية الانسيابية المحدثة */
    [data-testid="stSidebar"] {
        transform: none !important;
        visibility: visible !important;
        display: block !important;
        background: linear-gradient(180deg, #0F172A 0%, #1E293B 100%) !important;
        color: #F8FAFC !important;
        padding-top: 1.5rem;
        border-left: 1px solid rgba(255, 255, 255, 0.08);
        min-width: 290px !important;
        box-shadow: -5px 0 25px rgba(0,0,0,0.1);
    }
    
    [data-testid="stSidebar"] div, [data-testid="stSidebar"] span, [data-testid="stSidebar"] p, [data-testid="stSidebar"] label, [data-testid="stSidebar"] h3 {
        color: #F1F5F9 !important;
        text-align: right !important;
        direction: rtl !important;
    }
    
    [data-testid="stSidebar"] div[data-baseweb="select"] {
        background-color: rgba(255, 255, 255, 0.08) !important;
        border-radius: 8px !important;
    }
    
    [data-testid="stSidebar"] div[data-baseweb="select"] > div {
        background-color: transparent !important;
        color: #FFFFFF !important;
        border-color: rgba(255, 255, 255, 0.15) !important;
    }
    
    [data-testid="stSidebar"] div[data-baseweb="select"] span, 
    [data-testid="stSidebar"] div[data-baseweb="select"] div,
    [data-testid="stSidebar"] div[data-baseweb="select"] input {
        color: #FFFFFF !important;
        -webkit-text-fill-color: #FFFFFF !important;
        font-weight: bold !important;
    }
    
    /* حقول الإدخال والتقويم بتصميم انسيابي ناعم */
    div[data-testid="stDateInput"],
    div[data-testid="stDateInput"] > div,
    div[data-testid="stDateInput"] input,
    div[data-testid="stDateInput"] div {
        background-color: #FFFFFF !important;
        color: #0F172A !important;
        -webkit-text-fill-color: #0F172A !important;
        font-weight: bold !important;
        border-radius: 8px !important;
        border-color: #0F172A !important;
    }

    div[data-baseweb="popover"],
    div[data-baseweb="calendar"],
    div[role="dialog"],
    div[data-baseweb="popover"] *,
    div[data-baseweb="calendar"] *,
    div[role="dialog"] * {
        background-color: #FFFFFF !important;
        color: #0F172A !important;
        -webkit-text-fill-color: #0F172A !important;
    }
    
    div[data-baseweb="calendar"] button,
    div[data-baseweb="popover"] button {
        background-color: #FFFFFF !important;
        color: #0F172A !important;
        -webkit-text-fill-color: #0F172A !important;
        font-weight: bold !important;
        border: none !important;
        border-radius: 6px !important;
    }
    
    div[data-baseweb="calendar"] button:hover,
    div[data-baseweb="popover"] button:hover {
        background-color: #FFFFFF !important;
        color: #0F172A !important;
        -webkit-text-fill-color: #0F172A !important;
    }

    div[data-baseweb="calendar"] [aria-selected="true"] {
        background-color: #0F172A !important;
        color: #FFFFFF !important;
        -webkit-text-fill-color: #FFFFFF !important;
    }

    div[data-baseweb="menu"], ul[data-baseweb="menu"], div[role="listbox"], div[role="option"] {
        background-color: #FFFFFF !important;
        color: #0F172A !important;
        -webkit-text-fill-color: #0F172A !important;
    }
    div[role="option"]:hover {
        background-color: #F1F5F9 !important;
        color: #2563EB !important;
        -webkit-text-fill-color: #2563EB !important;
    }
    
    label p, .stRadio label, .stSelectbox label, .stTextInput label, .stNumberInput label, .stDateInput label {
        color: #334155 !important;
        font-weight: bold !important;
        font-size: 13px !important;
    }
    
    input, textarea, select {
        background-color: #FFFFFF !important;
        color: #0F172A !important;
        -webkit-text-fill-color: #0F172A !important;
        font-size: 13px !important;
        font-weight: bold !important;
        border-radius: 8px !important;
        border: 1px solid #CBD5E1 !important;
    }
    
    /* 🏢 هيدر الشركة الاحترافي المتطور */
    .company-header-container {
        background: linear-gradient(135deg, #1E3A8A 0%, #0F172A 100%);
        color: #FFFFFF !important;
        padding: 22px 26px;
        border-radius: 14px;
        margin-bottom: 20px !important;
        width: 100%;
        box-shadow: 0 10px 25px -5px rgba(30, 58, 138, 0.25);
        box-sizing: border-box;
    }
    .header-top-system {
        text-align: center !important;
        width: 100%;
        margin-bottom: 10px;
        border-bottom: 1px solid rgba(255, 255, 255, 0.12);
        padding-bottom: 8px;
    }
    .header-top-system h2 {
        font-size: 17px !important;
        font-weight: bold !important;
        color: #FFFFFF !important;
        -webkit-text-fill-color: #FFFFFF !important;
        margin: 0 !important;
        padding: 0 !important;
        text-align: center !important;
        letter-spacing: 0.3px;
    }
    .header-bottom-content {
        display: flex;
        justify-content: space-between;
        align-items: center;
        width: 100%;
    }
    .header-right-info { text-align: right !important; flex: 3; }
    .header-left-logo {
        flex: 1.2;
        text-align: left !important;
        display: flex;
        justify-content: flex-end;
        align-items: center;
        padding-left: 5px;
    }
    .comp-name-txt {
        font-size: 16px !important;
        font-weight: bold !important;
        margin-bottom: 6px !important;
        color: #FFFFFF !important;
        -webkit-text-fill-color: #FFFFFF !important;
    }
    .comp-info-txt {
        font-size: 12px !important;
        margin: 3px 0 !important;
        color: #E2E8F0 !important;
        -webkit-text-fill-color: #E2E8F0 !important;
        line-height: 1.5;
    }
    
    /* 📊 بطاقات مؤشرات الأداء العصرية */
    .dashboard-card {
        background: #FFFFFF;
        border-right: 5px solid #2563EB;
        padding: 18px 20px;
        border-radius: 12px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.04);
        text-align: right !important;
        margin-bottom: 12px;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .dashboard-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.08);
    }
    .dashboard-card-title {
        font-size: 12px;
        color: #64748B;
        font-weight: bold;
        margin-bottom: 6px;
    }
    .dashboard-card-value {
        font-size: 24px;
        color: #1E3A8A;
        font-weight: bold;
    }
    
    /* 📌 رؤوس الأقسام المتميزة */
    .section-header {
        font-size: 16px !important;
        font-weight: bold !important;
        color: #1E3A8A !important;
        border-bottom: 2px solid #3B82F6;
        padding-bottom: 8px;
        margin-top: 18px !important;
        margin-bottom: 14px !important;
        text-align: right !important;
        direction: rtl !important;
    }
    
    /* 📋 الجداول الانسيابية النظيفة */
    table.custom-table {
        width: 100%;
        border-collapse: separate;
        border-spacing: 0;
        margin-top: 8px !important;
        margin-bottom: 16px !important;
        background-color: #FFFFFF;
        color: #0F172A;
        direction: rtl !important;
        text-align: right !important;
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 4px 15px rgba(0,0,0,0.03);
        border: 1px solid #E2E8F0;
    }
    table.custom-table th, table.custom-table td {
        border-bottom: 1px solid #E2E8F0;
        border-left: 1px solid #F1F5F9;
        padding: 10px 14px;
        text-align: right !important;
        font-size: 12.5px;
        color: #1E293B !important;
        background-color: #FFFFFF !important;
    }
    table.custom-table th {
        background-color: #F8FAFC !important;
        font-weight: bold;
        color: #1E3A8A !important;
        border-bottom: 2px solid #CBD5E1;
    }
    table.custom-table tr:last-child td {
        border-bottom: none;
    }
    
    /* 📝 مناطق النماذج والإدخال */
    .entry-form-area {
        background: #FFFFFF;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.03);
        border: 1px solid #E2E8F0;
        margin-bottom: 15px;
    }
    
    @media print {
        body, .stApp, .block-container {
            background-color: #FFFFFF !important;
            color: #000000 !important;
            direction: rtl !important;
            text-align: right !important;
            -webkit-print-color-adjust: exact !important;
            print-color-adjust: exact !important;
        }
        button, .stButton, iframe, div[data-testid="stHeader"], div[data-baseweb="select"],
        .dashboard-card, div[data-testid="stForm"], .no-print, .entry-form-area, hr, div[data-testid="stSidebar"] {
            display: none !important;
        }
        .company-header-container {
            background: #FFFFFF !important;
            color: #000000 !important;
            border: 1px solid #000;
            box-shadow: none;
        }
        .header-top-system h2, .comp-name-txt, .comp-info-txt {
            color: #000000 !important;
        }
        table.custom-table {
            width: 100% !important;
            margin-top: 15px !important;
            box-shadow: none !important;
            border: 1px solid #000 !important;
        }
    }
    </style>
    
    <!-- سكريبت جافاسكريبت فوري لضمان ظهور عناصر التقويم والواجهة بوضوح تام -->
    <script>
    const forceWhiteCalendar = () => {
        const popovers = document.querySelectorAll('div[data-baseweb="popover"], div[data-baseweb="calendar"], div[role="dialog"]');
        popovers.forEach(pop => {
            pop.removeAttribute('data-theme');
            pop.style.setProperty('background-color', '#FFFFFF', 'important');
            pop.style.setProperty('color', '#0F172A', 'important');
            
            const allElements = pop.querySelectorAll('*');
            allElements.forEach(el => {
                if (el.getAttribute('aria-selected') !== 'true') {
                    el.style.setProperty('background-color', '#FFFFFF', 'important');
                    el.style.setProperty('color', '#0F172A', 'important');
                    el.style.setProperty('-webkit-text-fill-color', '#0F172A', 'important');
                }
            });
        });
    };

    const observer = new MutationObserver(forceWhiteCalendar);
    observer.observe(document.body, { childList: true, subtree: true });
    
    document.addEventListener('click', () => {
        setTimeout(forceWhiteCalendar, 5);
        setTimeout(forceWhiteCalendar, 50);
    });
    </script>
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
    logo_html = '<div style="padding: 10px 16px; border: 1px dashed rgba(255,255,255,0.4); border-radius: 10px; font-size: 12px; color: white; background: rgba(255,255,255,0.06); font-weight: bold;">🏢 شعار الشركة</div>'
    if info.get("logo") is not None:
        try:
            # تم تكبير أبعاد الشعار هنا لتشغل مساحة أكبر وأوضح
            logo_html = f'<img src="data:image/png;base64,{info.get("logo")}" alt="Logo" style="max-height: 85px; max-width: 170px; object-fit: contain; background: white; border-radius: 8px; padding: 4px; box-shadow: 0 4px 10px rgba(0,0,0,0.15);" />'
        except Exception:
            pass
            
    st.markdown(
        f"""
        <div class="company-header-container">
            <div class="header-top-system">
                <h2>🏢 النظام المتكامل لإدارة الموارد البشرية والشؤون الإدارية &nbsp;|&nbsp; شركة: {info.get("name", "")}</h2>
            </div>
            <div class="header-bottom-content">
                <div class="header-right-info">
                    <div class="comp-name-txt">{info.get("name", "")}</div>
                    <div class="comp-info-txt">📍 {info.get("address", "")} &nbsp;|&nbsp; 📋 سجل تجاري: {info.get("cr", "")} &nbsp;|&nbsp; 🧾 رقم ضريبي: {info.get("tax", "")} &nbsp;|&nbsp; 🔑 ترخيص التشغيل: {info.get("license", "")}</div>
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
        <div style="max-width: 440px; margin: 70px auto; background: #FFFFFF; padding: 35px; border-radius: 16px; box-shadow: 0 15px 35px rgba(0,0,0,0.06); text-align: center; direction: rtl; border: 1px solid #E2E8F0;">
            <h2 style="color: #1E3A8A; margin-bottom: 12px; font-size: 21px;">🔐 تسجيل الدخول للنظام</h2>
            <p style="color: #64748B; font-size: 13px; margin-bottom: 22px;">{company_display_name} | رخصة التشغيل: {company_license}</p>
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
                    st.success(f"مرحباً بك يا {user_record['الاسم الكامل']}! تم تسجيل الدخول بنجاح.")
                    st.rerun()
                else:
                    st.error("❌ الرسم السري غير صحيح!")
    st.stop()

render_company_header()

# =========================================================
# 🗂️ القائمة الجانبية الثابتة والمنسقة (مع صندوق البحث كقسم رئيسي)
# =========================================================
with st.sidebar:
    st.markdown("### 🗂️ لوحة التحكم الرئيسية")
    st.markdown("---")
    
    main_menu = st.radio("اختر القسم الرئيسي:", [
        "🏠 الشاشة الرئيسية",
        "🔍 صندوق البحث الشامل",
        "⏱️ الحضور والانصراف",
        "💰 المعاملات المالية",
        "📝 طلبات الإجازات",
        "👥 شؤون الموظفين",
        "⚙️ الأدوات والنظام"
    ], index=0)
    
    st.markdown("---")
    
    if main_menu == "🏠 الشاشة الرئيسية":
        sub_options = ["لوحة المؤشرات والتحكم"]
        choice = st.selectbox("حدد الإجراء المطلوب:", sub_options)
    elif main_menu == "🔍 صندوق البحث الشامل":
        sub_options = ["محرك البحث المتطور والفلترة"]
        choice = st.selectbox("حدد الإجراء المطلوب:", sub_options)
    elif main_menu == "⏱️ الحضور والانصراف":
        sub_options = [
            "تسجيل حضور وانصراف", 
            "سجل الحضور والانصراف", 
            "تعديل أو حذف حركة حضور"
        ]
        choice = st.selectbox("حدد الإجراء المطلوب:", sub_options)
    elif main_menu == "💰 المعاملات المالية":
        sub_options = [
            "تسجيل معاملة مالية", 
            "سجل المعاملات المالية", 
            "تعديل أو حذف معاملة مالية"
        ]
        choice = st.selectbox("حدد الإجراء المطلوب:", sub_options)
    elif main_menu == "📝 طلبات الإجازات":
        sub_options = [
            "تسجيل طلب إجازة جديد", 
            "سجل طلبات قيد الانتظار", 
            "سجل الطلبات المقبولة", 
            "سجل الطلبات المرفوضة", 
            "تعديل أو حذف طلب إجازة"
        ]
        choice = st.selectbox("حدد الإجراء المطلوب:", sub_options)
    elif main_menu == "👥 شؤون الموظفين":
        sub_options = [
            "إضافة موظف جديد", 
            "سجل الموظفين والأرصدة", 
            "تعديل أو حذف موظف"
        ]
        choice = st.selectbox("حدد الإجراء المطلوب:", sub_options)
    elif main_menu == "⚙️ الأدوات والنظام":
        sub_options = [
            "إدارة المستخدمين والصلاحيات", 
            "كشف الرواتب والمستحقات", 
            "طباعة التقارير", 
            "إعدادات الشركة", 
            "تصدير وتحميل Excel", 
            "نسخة احتياطية واستعادة", 
            "مسح البيانات"
        ]
        choice = st.selectbox("حدد الإجراء المطلوب:", sub_options)
    
    st.markdown("---")
    st.markdown(f"**👤 المستخدم:** {st.session_state.current_logged_user}")
    st.markdown(f"**🛡️ الصلاحية:** {st.session_state.current_user_role}")
    st.markdown(f"**🏢 الفرع:** {st.session_state.current_user_branch}")
    
    st.markdown("---")
    if st.button("🚪 تسجيل خروج آمن", use_container_width=True):
        st.session_state.is_authenticated = False
        st.session_state.current_logged_user = ""
        st.rerun()

# =========================================================
# 🔍 صندوق البحث المتطور والشامل (قسم رئيسي مستقل)
# =========================================================
if main_menu == "🔍 صندوق البحث الشامل" or choice == "محرك البحث المتطور والفلترة":
    st.markdown(f'<div class="section-header">🔍 صندوق البحث المتطور والشامل في قواعد بيانات الشركة</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="entry-form-area">', unsafe_allow_html=True)
    with st.form("advanced_search_form"):
        col_s1, col_s2, col_s3 = st.columns(3)
        with col_s1:
            search_keyword = st.text_input("بحث نصي (الاسم، كود الموظف، الوظيفة، أو البيان):")
        with col_s2:
            branches_avail = ["الكل"] + sorted(st.session_state.employees["الفرع"].dropna().unique().tolist()) if not st.session_state.employees.empty else ["الكل"]
            selected_search_branch = st.selectbox("تصفية حسب الفرع:", branches_avail)
        with col_s3:
            search_target_section = st.selectbox("نطاق البحث في النظام:", ["جميع السجلات (شامل)", "سجل الموظفين والأرصدة", "سجل الحضور والانصراف", "سجل طلبات الإجازات", "سجل المعاملات المالية"])
            
        submit_adv_search = st.form_submit_button("🔍 تنفيذ البحث المتطور", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
        
    if submit_adv_search or True:
        keyword = search_keyword.strip().lower()
        
        if search_target_section in ["جميع السجلات (شامل)", "سجل الموظفين والأرصدة"]:
            st.markdown("##### 👥 نتائج البحث في (سجل الموظفين):")
            emp_df = st.session_state.employees.copy()
            if selected_search_branch != "الكل":
                emp_df = emp_df[emp_df["الفرع"] == selected_search_branch]
            if keyword:
                mask = emp_df.astype(str).apply(lambda x: x.str.lower().str.contains(keyword)).any(axis=1)
                emp_df = emp_df[mask]
            render_printable_table(emp_df)
            
        if search_target_section in ["جميع السجلات (شامل)", "سجل الحضور والانصراف"]:
            st.markdown("##### ⏱️ نتائج البحث في (سجل الحضور والانصراف):")
            att_df = st.session_state.attendance.copy()
            if not att_df.empty:
                if selected_search_branch != "الكل":
                    att_df = att_df[att_df["الفرع"] == selected_search_branch]
                if keyword:
                    mask = att_df.astype(str).apply(lambda x: x.str.lower().str.contains(keyword)).any(axis=1)
                    att_df = att_df[mask]
            render_printable_table(att_df)

        if search_target_section in ["جميع السجلات (شامل)", "سجل طلبات الإجازات"]:
            st.markdown("##### 📝 نتائج البحث في (سجل طلبات الإجازات):")
            req_df = st.session_state.requests.copy()
            if not req_df.empty:
                if selected_search_branch != "الكل":
                    req_df = req_df[req_df["الفرع"] == selected_search_branch]
                if keyword:
                    mask = req_df.astype(str).apply(lambda x: x.str.lower().str.contains(keyword)).any(axis=1)
                    req_df = req_df[mask]
            render_printable_table(req_df)

        if search_target_section in ["جميع السجلات (شامل)", "سجل المعاملات المالية"]:
            st.markdown("##### 💰 نتائج البحث في (سجل المعاملات المالية والسلف):")
            fin_df = st.session_state.financial_transactions.copy()
            if not fin_df.empty:
                if selected_search_branch != "الكل":
                    fin_df = fin_df[fin_df["الفرع"] == selected_search_branch]
                if keyword:
                    mask = fin_df.astype(str).apply(lambda x: x.str.lower().str.contains(keyword)).any(axis=1)
                    fin_df = fin_df[mask]
            render_printable_table(fin_df)

# =========================================================
# 🏠 الشاشة الرئيسية / لوحة المؤشرات
# =========================================================
elif choice == "لوحة المؤشرات والتحكم" or choice == "الشاشة الرئيسية":
    st.markdown(f'<div class="section-header">📈 مؤشرات الأداء العامة - شركة: {company_display_name}</div>', unsafe_allow_html=True)
    
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
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f'<div class="dashboard-card"><div class="dashboard-card-title">👥 إجمالي موظفي الشركة</div><div class="dashboard-card-value">{total_emps}</div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="dashboard-card" style="border-right-color: #D97706;"><div class="dashboard-card-title">⏳ الطلبات المعلقة</div><div class="dashboard-card-value" style="color: #D97706;">{pending_count}</div></div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div class="dashboard-card" style="border-right-color: #16A34A;"><div class="dashboard-card-title">✅ الطلبات المقبولة</div><div class="dashboard-card-value" style="color: #16A34A;">{accepted_count}</div></div>', unsafe_allow_html=True)

    if not pending_requests.empty:
        st.markdown(f'<div class="section-header">⏳ اتخاذ القرار بشأن الطلبات المعلقة ({pending_count} طلب)</div>', unsafe_allow_html=True)
        render_printable_table(pending_requests)
        
        st.markdown('<div class="entry-form-area">', unsafe_allow_html=True)
        col_dec1, col_dec2, col_dec3 = st.columns([2, 2, 2])
        
        with col_dec1:
            req_ids = pending_requests["رقم الطلب"].tolist()
            selected_req_id = st.selectbox("اختر رقم الطلب لاتخاذ القرار:", req_ids)
            
        selected_req = pending_requests[pending_requests["رقم الطلب"] == selected_req_id].iloc[0]
        emp_code_req = selected_req["كود الموظف"]
        days_req = selected_req["عدد الأيام"]
        type_req = selected_req["نوع الإجازة"]
        
        with col_dec2:
            st.write("")
            st.write("")
            if st.button("✅ قبول وتأكيد الإجازة", use_container_width=True):
                st.session_state.requests.loc[st.session_state.requests["رقم الطلب"] == selected_req_id, "الحالة"] = "مقبول"
                
                if "سنوية" in type_req:
                    st.session_state.employees.loc[st.session_state.employees["كود الموظف"] == emp_code_req, "سنوي مستهلك"] += days_req
                    st.session_state.employees.loc[st.session_state.employees["كود الموظف"] == emp_code_req, "سنوي متبقي"] -= days_req
                elif "أسبوعية" in type_req or "عارضة" in type_req:
                    st.session_state.employees.loc[st.session_state.employees["كود الموظف"] == emp_code_req, "أسبوعي مستهلك"] += days_req
                    st.session_state.employees.loc[st.session_state.employees["كود الموظف"] == emp_code_req, "أسبوعي متبقي"] -= days_req
                elif "مرضية" in type_req:
                    if "إجازات مرضية (أيام)" in st.session_state.employees.columns:
                        st.session_state.employees.loc[st.session_state.employees["كود الموظف"] == emp_code_req, "إجازات مرضية (أيام)"] += days_req
                        
                auto_save_data()
                st.success(f"تم قبول الطلب رقم #{selected_req_id} وخصم الأيام بنجاح!")
                st.rerun()

        with col_dec3:
            st.write("")
            st.write("")
            if st.button("❌ رفض الطلب", use_container_width=True):
                st.session_state.requests.loc[st.session_state.requests["رقم الطلب"] == selected_req_id, "الحالة"] = "مرفوض"
                auto_save_data()
                st.error(f"تم رفض الطلب رقم #{selected_req_id}.")
                st.rerun()
                
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown(f'<div class="section-header">📊 الرسم البياني التحليلي لإحصائيات وأرصدة الموظفين</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="entry-form-area">', unsafe_allow_html=True)
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
                    background-color: #1E3A8A;
                    color: white;
                    padding: 8px 14px;
                    border: none;
                    border-radius: 6px;
                    font-size: 13px;
                    font-weight: bold;
                    cursor: pointer;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.15);
                    font-family: 'Tahoma', sans-serif;
                    width: 100%;
                ">
                    🖨️ طباعة المخطط
                </button>
            </div>
        """, height=45)
    st.markdown('</div>', unsafe_allow_html=True)

    if not filtered_chart_emps.empty:
        st.markdown(f'<div style="text-align: right; direction: rtl; font-weight: bold; font-size: 14px; margin-bottom: 8px; color: #1E3A8A;">📌 {chart_subtitle}</div>', unsafe_allow_html=True)
        
        chart_df_melted = filtered_chart_emps.melt(
            id_vars=["اسم الموظف"],
            value_vars=["رصيد سنوي (إجمالي)", "سنوي مستهلك", "سنوي متبقي"],
            var_name="نوع الرصيد",
            value_name="عدد الأيام"
        )
        
        c1 = alt.Chart(chart_df_melted).mark_bar().encode(
            x=alt.X('اسم الموظف:N', title='الموظف', axis=alt.Axis(labelAngle=0, labelColor='#334155', titleColor='#1E3A8A')),
            y=alt.Y('عدد الأيام:Q', title='عدد الأيام', axis=alt.Axis(labelColor='#334155', titleColor='#1E3A8A')),
            color=alt.Color('نوع الرصيد:N', legend=alt.Legend(
                orient='bottom', 
                direction='horizontal',
                title='نوع الرصيد:',
                titleColor='#1E3A8A',
                labelColor='#334155',
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
# ⏱️ 1. تسجيل حضور وانصراف
# =========================================================
elif choice == "تسجيل حضور وانصراف":
    st.subheader("⏱️ 1. تسجيل حركة حضور / انصراف جديدة")
    
    emp_names = st.session_state.employees["اسم الموظف"].tolist()
    if not emp_names:
        st.warning("لا توجد موظفون متاحون.")
    else:
        st.markdown('<div class="entry-form-area">', unsafe_allow_html=True)
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
        st.markdown('</div>', unsafe_allow_html=True)

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
        
        st.markdown('<div class="entry-form-area">', unsafe_allow_html=True)
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
        st.markdown('</div>', unsafe_allow_html=True)

# =========================================================
# 💰 1. تسجيل معاملة مالية
# =========================================================
elif choice == "تسجيل معاملة مالية":
    st.subheader("💰 1. إضافة معاملة مالية جديدة (سلفة / جزاء / مكافأة / بدلات / إضافي)")
    
    emp_names = st.session_state.employees["اسم الموظف"].tolist()
    if not emp_names:
        st.warning("لا توجد موظفون مسجلون.")
    else:
        st.markdown('<div class="entry-form-area">', unsafe_allow_html=True)
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
        st.markdown('</div>', unsafe_allow_html=True)

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
        
        st.markdown('<div class="entry-form-area">', unsafe_allow_html=True)
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
        st.markdown('</div>', unsafe_allow_html=True)

# =========================================================
# 📝 1. تسجيل طلب إجازة جديد
# =========================================================
elif choice == "تسجيل طلب إجازة جديد":
    st.subheader(f"📝 1. تقديم طلب إجازة جديد - {company_display_name}")
    
    emp_list = st.session_state.employees["اسم الموظف"].dropna().astype(str).tolist()
    
    if not emp_list:
        st.warning("لا توجد موظفون متاحون لتسجيل إجازة لهم.")
    else:
        st.markdown('<div class="entry-form-area">', unsafe_allow_html=True)
        with st.form("leave_form"):
            emp_name = st.selectbox("اسم الموظف", emp_list)
            leave_type = st.selectbox("نوع الإجازة", [
                "إجازة سنوية (Annual)", "إجازة أسبوعية / عارضة", "إجازة مرضية (Sick Leave)", "إجازة رسمية", "بدون أجر"
            ])
            col_d1, col_d2 = st.columns(2)
            with col_d1: start_date = st.date_input("من تاريخ")
            with col_d2: end_date = st.date_input("إلى تاريخ")
            reason = st.text_area("سبب الإجازة / ملاحظات إضافية")
            submit_leave = st.form_submit_button("إرسال طلب الإجازة للمراجعة", use_container_width=True)
            
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
        st.markdown('</div>', unsafe_allow_html=True)

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
        
        st.markdown('<div class="entry-form-area">', unsafe_allow_html=True)
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
        st.markdown('</div>', unsafe_allow_html=True)

# =========================================================
# 👥 1. إضافة موظف جديد
# =========================================================
elif choice == "إضافة موظف جديد":
    st.subheader(f"👥 1. إضافة موظف جديد - {company_display_name}")
    
    st.markdown('<div class="entry-form-area">', unsafe_allow_html=True)
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
    st.markdown('</div>', unsafe_allow_html=True)

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
        
        st.markdown('<div class="entry-form-area">', unsafe_allow_html=True)
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
        st.markdown('</div>', unsafe_allow_html=True)

# =========================================================
# ⚙️ 1. إدارة المستخدمين والصلاحيات
# =========================================================
elif choice == "إدارة المستخدمين والصلاحيات":
    st.subheader("🔒 1. إدارة مستخدمي النظام والصلاحيات")
    st.markdown('<div class="entry-form-area">', unsafe_allow_html=True)
    with st.form("new_user_form"):
        u_username = st.text_input("اسم المستخدم (للدخول مثل: supervisor1)")
        u_fullname = st.text_input("الاسم الكامل للمستخدم")
        u_branch = st.text_input("الفرع التابع له")
        u_dept = st.text_input("القسم التابع له")
        u_role = st.selectbox("الصلاحية والدور في النظام", ["مشرف عام (Admin)", "مدير شؤون إدارية", "متابع فرع", "موظف إدخال"])
        u_pattern = st.text_input("الرسم السري (مثل: 1-2-3)")
        if st.form_submit_button("حفظ المستخدم الجديد", use_container_width=True):
            if u_username and u_pattern:
                new_u = {"اسم المستخدم": u_username, "الاسم الكامل": u_fullname, "الفرع التابع": u_branch, "القسم التابع": u_dept, "الصلاحية": u_role, "البريد الإلكتروني": "user@company.com", "الحالة": "نشط", "الرسم السري": u_pattern}
                st.session_state.users = pd.concat([st.session_state.users, pd.DataFrame([new_u])], ignore_index=True)
                auto_save_data()
                st.success("تم إضافة المستخدم بنجاح!")
                st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    render_printable_table(st.session_state.users.drop(columns=["الرسم السري"], errors="ignore"))

# =========================================================
# ⚙️ 2. كشف الرواتب والمستحقات
# =========================================================
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

# =========================================================
# ⚙️ 3. طباعة التقارير
# =========================================================
elif choice == "طباعة التقارير":
    col_t1, col_t2 = st.columns([3, 1])
    with col_t1: st.subheader("🖨️ 3. طباعة التقارير العامة")
    with col_t2: render_print_button()
    render_printable_table(st.session_state.employees)

# =========================================================
# ⚙️ 4. إعدادات الشركة
# =========================================================
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
    
    st.markdown('<div class="entry-form-area">', unsafe_allow_html=True)
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
    st.markdown('</div>', unsafe_allow_html=True)

# =========================================================
# ⚙️ 5. تصدير وتحميل Excel
# =========================================================
elif choice == "تصدير وتحميل Excel":
    st.subheader("📥 5. تصدير وتحميل بيانات النظام بصيغة Excel")
    st.markdown('<div class="entry-form-area">', unsafe_allow_html=True)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        st.session_state.employees.to_excel(writer, sheet_name='الموظفين', index=False)
        st.session_state.requests.to_excel(writer, sheet_name='سجل الإجازات', index=False)
        st.session_state.attendance.to_excel(writer, sheet_name='الحضور والانصراف', index=False)
        st.session_state.financial_transactions.to_excel(writer, sheet_name='السلف والماليات', index=False)
    output.seek(0)
    st.download_button(label="📥 تحميل ملف الإكسيل الآن", data=output, file_name=f"Leave_System_{company_id}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    st.markdown('</div>', unsafe_allow_html=True)

# =========================================================
# ⚙️ 6. نسخة احتياطية واستعادة
# =========================================================
elif choice == "نسخة احتياطية واستعادة":
    st.subheader("💾 6. النسخ الاحتياطي والاستعادة")
    st.markdown('<div class="entry-form-area">', unsafe_allow_html=True)
    backup_dict = {
        "employees": st.session_state.employees.to_dict(orient='records'),
        "requests": st.session_state.requests.to_dict(orient='records'),
        "attendance": st.session_state.attendance.to_dict(orient='records'),
        "financial_transactions": st.session_state.financial_transactions.to_dict(orient='records'),
        "users": st.session_state.users.to_dict(orient='records'),
        "company_info": st.session_state.company_info
    }
    st.download_button("💾 تحميل النسخة الاحتياطية (JSON)", data=json.dumps(backup_dict, ensure_ascii=False, indent=4), file_name=f"backup_{company_id}.json", mime="application/json")
    st.markdown('</div>', unsafe_allow_html=True)

# =========================================================
# ⚙️ 7. مسح البيانات
# =========================================================
elif choice == "مسح البيانات":
    st.subheader("🗑️ 7. مسح وحذف كافة بيانات الشركة")
    st.markdown('<div class="entry-form-area">', unsafe_allow_html=True)
    confirm_text = st.text_input("اكتب 'تأكيد الحذف' للتأكيد:")
    if confirm_text == "تأكيد الحذف" and st.button("حذف كافة البيانات نهائياً", type="primary"):
        st.session_state.employees = pd.DataFrame(columns=["كود الموظف", "اسم الموظف", "الوظيفة", "القسم", "الفرع", "صلاحية الموظف", "الراتب الأساسي", "رصيد سنوي (إجمالي)", "سنوي مستهلك", "سنوي متبقي", "رصيد أسبوعي (إجمالي)", "أسبوعي مستهلك", "أسبوعي متبقي", "رصيد رسمي (إجمالي)", "رسمي مستهلك", "رسمي متبقي", "إجازات مرضية (أيام)"])
        st.session_state.requests = pd.DataFrame(columns=["رقم الطلب", "كود الموظف", "اسم الموظف", "الوظيفة", "الفرع", "نوع الإجازة", "من تاريخ", "إلى تاريخ", "عدد الأيام", "السبب", "الحالة"])
        st.session_state.attendance = pd.DataFrame(columns=["التاريخ", "كود الموظف", "اسم الموظف", "الفرع", "بداية العمل الرسمية", "نهاية العمل الرسمية", "وقت الحضور الفعلي", "وقت الانصراف الفعلي", "الحالة", "التأخير الصباحي (دقيقة)", "انصراف مبكر (دقيقة)", "إضافي بعد العمل (دقيقة)", "حضور مبكر (دقيقة)", "خروج متأخر (دقيقة)", "دقائق التأخير"])
        st.session_state.financial_transactions = pd.DataFrame(columns=["التاريخ", "كود الموظف", "اسم الموظف", "الفرع", "النوع", "المبلغ / القيمة", "البيان / السبب"])
        auto_save_data()
        st.success("تم مسح كافة البيانات بنجاح!")
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)