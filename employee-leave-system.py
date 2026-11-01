import streamlit as str_lit
import pandas as pd
from datetime import datetime, date, time, timedelta
import json
import os
import io
import base64
import uuid

str_lit.set_page_config(
    page_title="النظام المتكامل لإدارة الموارد البشرية",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="collapsed"
)

LICENSE_FILE = "client_license.json"

def get_client_license():
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

def load_company_data():
    if os.path.exists(COMPANY_FILE):
        try:
            with open(COMPANY_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                
                if "employees" in data and len(data["employees"]) > 0:
                    df_emp = pd.DataFrame(data["employees"])
                    if "مسوغات التعيين" not in df_emp.columns:
                        df_emp["مسوغات التعيين"] = ""
                    if "تاريخ بداية العقد" not in df_emp.columns:
                        df_emp["تاريخ بداية العقد"] = str(date.today())
                    if "تاريخ نهاية العقد" not in df_emp.columns:
                        df_emp["تاريخ نهاية العقد"] = str(date.today() + timedelta(days=365))
                    str_lit.session_state.employees = df_emp
                else:
                    str_lit.session_state.employees = pd.DataFrame(columns=[
                        "كود الموظف", "اسم الموظف", "الوظيفة", "القسم", "الفرع", "صلاحية الموظف",
                        "الراتب الأساسي", "مسوغات التعيين", "تاريخ بداية العقد", "تاريخ نهاية العقد",
                        "رصيد سنوي (إجمالي)", "سنوي مستهلك", "سنوي متبقي",
                        "رصيد أسبوعي (إجمالي)", "أسبوعي مستهلك", "أسبوعي متبقي",
                        "رصيد رسمي (إجمالي)", "رسمي مستهلك", "رسمي متبقي",
                        "إجازات مرضية (أيام)"
                    ])

                if "requests" in data and len(data["requests"]) > 0:
                    str_lit.session_state.requests = pd.DataFrame(data["requests"])
                else:
                    str_lit.session_state.requests = pd.DataFrame(columns=[
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
                    str_lit.session_state.attendance = df_att[expected_att_cols]
                else:
                    str_lit.session_state.attendance = pd.DataFrame(columns=[
                        "التاريخ", "كود الموظف", "اسم الموظف", "الوظيفة", "الفرع", 
                        "بداية العمل الرسمية", "نهاية العمل الرسمية", "وقت الحضور الفعلي", "وقت الانصراف الفعلي", 
                        "فترة السماح (دقيقة)", "الحالة", "التأخير (دقيقة)", "إضافي (دقيقة)"
                    ])

                if "financial_transactions" in data and len(data["financial_transactions"]) > 0:
                    str_lit.session_state.financial_transactions = pd.DataFrame(data["financial_transactions"])
                else:
                    str_lit.session_state.financial_transactions = pd.DataFrame(columns=[
                        "التاريخ", "كود الموظف", "اسم الموظف", "الفرع", "النوع", "المبلغ / القيمة", "البيان / السبب"
                    ])

                if "users" in data and len(data["users"]) > 0:
                    df_users = pd.DataFrame(data["users"])
                    if "الحالة" not in df_users.columns:
                        df_users["الحالة"] = "نشط"
                    str_lit.session_state.users = df_users
                else:
                    str_lit.session_state.users = pd.DataFrame([
                        {"اسم المستخدم": "admin", "الاسم الكامل": "المدير العام", "الفرع التابع": "المركز الرئيسي", "القسم التابع": "الإدارة العليا", "الصلاحية": "مشرف عام (Admin)", "البريد الإلكتروني": "admin@company.com", "الحالة": "نشط", "الرسم السري": "1-2-3"}
                    ])

                if "company_info" in data:
                    str_lit.session_state.company_info = data["company_info"]
        except Exception as e:
            str_lit.error(f"خطأ في تحميل ملف الشركة: {e}")
    else:
        str_lit.session_state.employees = pd.DataFrame([
            {
                "كود الموظف": "EMP001", "اسم الموظف": "أحمد محمود", "الوظيفة": "محاسب أول", "القسم": "الإدارة المالية", "الفرع": "المركز الرئيسي",
                "صلاحية الموظف": "اعتماد الطلبات", "الراتب الأساسي": 5000, "مسوغات التعيين": "",
                "تاريخ بداية العقد": "2025-11-01", "تاريخ نهاية العقد": "2026-11-25",
                "رصيد سنوي (إجمالي)": 21, "سنوي مستهلك": 3, "سنوي متبقي": 18,
                "رصيد أسبوعي (إجمالي)": 4, "أسبوعي مستهلك": 1, "أسبوعي متبقي": 3,
                "رصيد رسمي (إجمالي)": 10, "رسمي مستهلك": 2, "رسمي متبقي": 8,
                "إجازات مرضية (أيام)": 0
            }
        ])
        str_lit.session_state.requests = pd.DataFrame(columns=[
            "رقم الطلب", "كود الموظف", "اسم الموظف", "الوظيفة", "الفرع", "نوع الإجازة", "من تاريخ", "إلى تاريخ", "عدد الأيام", "السبب", "الحالة"
        ])
        str_lit.session_state.attendance = pd.DataFrame(columns=[
            "التاريخ", "كود الموظف", "اسم الموظف", "الوظيفة", "الفرع", 
            "بداية العمل الرسمية", "نهاية العمل الرسمية", "وقت الحضور الفعلي", "وقت الانصراف الفعلي", 
            "فترة السماح (دقيقة)", "الحالة", "التأخير (دقيقة)", "إضافي (دقيقة)"
        ])
        str_lit.session_state.financial_transactions = pd.DataFrame(columns=[
            "التاريخ", "كود الموظف", "اسم الموظف", "الفرع", "النوع", "المبلغ / القيمة", "البيان / السبب"
        ])
        str_lit.session_state.users = pd.DataFrame([
            {"اسم المستخدم": "admin", "الاسم الكامل": "المدير العام", "الفرع التابع": "المركز الرئيسي", "القسم التابع": "الإدارة العليا", "الصلاحية": "مشرف عام (Admin)", "البريد الإلكتروني": "admin@company.com", "الحالة": "نشط", "الرسم السري": "1-2-3"}
        ])
        str_lit.session_state.company_info = {
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
    try:
        data_to_save = {
            "employees": str_lit.session_state.employees.to_dict(orient='records'),
            "requests": str_lit.session_state.requests.to_dict(orient='records'),
            "attendance": str_lit.session_state.attendance.to_dict(orient='records'),
            "financial_transactions": str_lit.session_state.financial_transactions.to_dict(orient='records'),
            "users": str_lit.session_state.users.to_dict(orient='records'),
            "company_info": str_lit.session_state.company_info
        }
        with open(COMPANY_FILE, "w", encoding="utf-8") as f:
            json.dump(data_to_save, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"خطأ في الحفظ التلقائي: {e}")

load_company_data()
str_lit.session_state.company_info["name"] = company_display_name
str_lit.session_state.company_info["license"] = company_license

if 'theme_mode' not in str_lit.session_state:
    str_lit.session_state.theme_mode = "Light"

def render_printable_table(df):
    if df.empty:
        str_lit.info("لا توجد بيانات متاحة للعرض.")
        return
    
    info = str_lit.session_state.company_info
    c_name = info.get("name", "")
    c_cr = info.get("cr", "")
    c_tax = info.get("tax", "")
    c_lic = info.get("license", "")
    
    logged_user = str_lit.session_state.get('current_logged_user', 'غير محدد')
    user_role = str_lit.session_state.get('current_user_role', 'غير محدد')
    user_branch = str_lit.session_state.get('current_user_branch', 'غير محدد')
    
    str_lit.dataframe(df, use_container_width=True)
    
    header_info_csv = f"# شركة: {c_name} | س.ت: {c_cr} | ب.ض: {c_tax} | ترخيص: {c_lic}\n"
    user_info_csv = f"# المسؤول: {logged_user} ({user_role}) | الفرع: {user_branch} | التاريخ: {datetime.now().strftime('%Y-%m-%d')}\n\n"
    
    csv_body = df.to_csv(index=False)
    full_csv_data = (header_info_csv + user_info_csv + csv_body).encode('utf-8-sig')
    
    unique_btn_key = f"dl_btn_{uuid.uuid4()}"
    str_lit.download_button(
        label="📥 تحميل هذا الجدول كملف CSV",
        data=full_csv_data,
        file_name=f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv",
        key=unique_btn_key
    )

is_dark = str_lit.session_state.theme_mode == "Dark"

bg_color = "linear-gradient(135deg, #121212 0%, #1A1A1A 50%, #0B0B0B 100%)" if is_dark else "linear-gradient(135deg, #F8FAFC 0%, #F1F5F9 50%, #E2E8F0 100%)"
text_color = "#F1F5F9" if is_dark else "#0F172A"
card_bg = "rgba(30, 30, 30, 0.75)" if is_dark else "rgba(255, 255, 255, 0.9)"
card_value_color = "#FFFFFF" if is_dark else "#0F172A"
wrapper_bg = "#121212" if is_dark else "#FFFFFF"
input_bg = "rgba(30, 41, 59, 0.9)" if is_dark else "#FFFFFF"
input_text = "#FFFFFF" if is_dark else "#0F172A"
input_border = "#475569" if is_dark else "#CBD5E1"
header_bg = "rgba(30, 30, 30, 0.85)" if is_dark else "rgba(255, 255, 255, 0.95)"
header_text = "#FFFFFF" if is_dark else "#0F172A"

str_lit.markdown(f"""
    <style>
    header[data-testid="stHeader"] {{ visibility: hidden; height: 0px; }}
    [data-testid="stSidebar"] {{ display: none !important; width: 0px !important; }}
    
    html, body, [class*="css"], .stMarkdown, div, span, p, h1, h2, h3, h4, h5, h6, label {{
        font-family: 'Tahoma', 'Segoe UI', sans-serif !important;
        direction: rtl !important;
        text-align: right !important;
        color: {text_color} !important;
    }}
    
    .block-container {{
        padding-top: 0.2rem !important;
        padding-bottom: 3rem !important;
        padding-left: 1.5rem !important;
        padding-right: 1.5rem !important;
        max-width: 100% !important;
        background: {bg_color} !important;
        min-height: 100vh;
    }}
    
    .sticky-top-wrapper {{
        position: fixed !important;
        top: 0 !important;
        left: 0 !important;
        right: 0 !important;
        z-index: 999999 !important;
        background: {wrapper_bg} !important;
        padding: 4px 15px 2px 15px !important;
        border-bottom: 2px solid #E50914;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }}
    
    .main-content-spacer {{
        margin-top: 220px !important;
    }}
    
    label p, .stRadio label, .stSelectbox label, .stTextInput label, .stNumberInput label, .stDateInput label {{
        color: {text_color} !important;
        font-weight: bold !important;
        font-size: 13px !important;
        margin-bottom: 2px !important;
    }}
    
    input, textarea, select {{
        background-color: {input_bg} !important;
        color: {input_text} !important;
        font-size: 13px !important;
        font-weight: bold !important;
        border-radius: 8px !important;
        border: 1.5px solid {input_border} !important;
        padding: 6px 10px !important;
    }}
    
    .glass-header {{
        background: {header_bg};
        border: 1px solid rgba(229, 9, 20, 0.3);
        color: {header_text} !important;
        padding: 0px !important;
        border-radius: 8px;
        width: 100%;
        margin-bottom: 3px;
        display: flex;
        align-items: stretch;
        overflow: hidden;
    }}
    
    .header-logo-box-full {{
        width: 65px;
        background: rgba(229, 9, 20, 0.2);
        border-left: 1px solid rgba(229, 9, 20, 0.4);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 22px;
        padding: 4px;
    }}
    
    .header-top-system h2 {{
        font-size: 10.5px !important;
        font-weight: bold !important;
        color: #F87171 !important;
        margin: 0 0 1px 0 !important;
    }}
    .comp-name-txt {{
        font-size: 12.5px !important;
        font-weight: bold !important;
        color: {header_text} !important;
    }}
    .comp-info-txt {{
        font-size: 9px !important;
        color: #94A3B8 !important;
        margin-top: 1px;
    }}
    
    .user-badge-box {{
        background: rgba(229, 9, 20, 0.15);
        border: 1px solid rgba(229, 9, 20, 0.4);
        padding: 2px 6px;
        border-radius: 5px;
        font-size: 10px;
        color: #FCA5A5;
        font-weight: bold;
        text-align: center;
        margin-bottom: 2px;
    }}
    
    .glass-card {{
        background: {card_bg};
        backdrop-filter: blur(15px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-right: 5px solid #E50914;
        padding: 10px 14px;
        border-radius: 12px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
        text-align: right !important;
        margin-bottom: 8px;
    }}
    .glass-card-title {{
        font-size: 11.5px;
        color: #94A3B8;
        font-weight: bold;
        margin-bottom: 2px;
    }}
    .glass-card-value {{
        font-size: 20px;
        color: {card_value_color};
        font-weight: bold;
    }}
    
    .section-header {{
        font-size: 15px !important;
        font-weight: bold !important;
        color: #F87171 !important;
        border-bottom: 2px solid #E50914;
        padding-bottom: 6px;
        margin-top: 10px !important;
        margin-bottom: 10px !important;
        text-align: right !important;
    }}
    
    .entry-form-area {{
        background: {card_bg};
        backdrop-filter: blur(15px);
        padding: 16px;
        border-radius: 14px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        border: 1px solid rgba(255, 255, 255, 0.08);
        margin-bottom: 12px;
    }}
    </style>
""", unsafe_allow_html=True)

if 'is_authenticated' not in str_lit.session_state: str_lit.session_state.is_authenticated = False
if 'current_logged_user' not in str_lit.session_state: str_lit.session_state.current_logged_user = ""
if 'current_user_dept' not in str_lit.session_state: str_lit.session_state.current_user_dept = ""
if 'current_user_branch' not in str_lit.session_state: str_lit.session_state.current_user_branch = ""
if 'current_user_role' not in str_lit.session_state: str_lit.session_state.current_user_role = ""

if 'active_main_section' not in str_lit.session_state: str_lit.session_state.active_main_section = "الرئيسية"

def render_company_header():
    info = str_lit.session_state.company_info
    logo_val = info.get("logo", "")
    
    if logo_val and logo_val.startswith("data:image"):
        logo_html = f'<div class="header-logo-box-full"><img src="{logo_val}" style="width: 100%; height: 100%; object-fit: contain; background: white; padding: 2px;" /></div>'
    elif logo_val and (logo_val.startswith("http://") or logo_val.startswith("https://")):
        logo_html = f'<div class="header-logo-box-full"><img src="{logo_val}" style="width: 100%; height: 100%; object-fit: contain;" /></div>'
    else:
        logo_html = '<div class="header-logo-box-full">🏢</div>'

    contact_num = info.get("contact", "غير محدد")
    email_addr = info.get("email", "غير محدد")
    address_str = info.get("address", "غير محدد")
    cr_num = info.get("cr", "غير محدد")
    tax_num = info.get("tax", "غير محدد")
    lic_num = info.get("license", "غير محدد")
    comp_name = info.get("name", "")

    str_lit.markdown(
        f"""
        <div class="glass-header">
            <div style="padding: 4px 10px; width: 100%;">
                <div class="header-top-system"><h2>برنامج شؤون الموظفين والإدارة</h2></div>
                <div class="comp-name-txt">{comp_name}</div>
                <div class="comp-info-txt">📍 العنوان: {address_str} &nbsp;|&nbsp; 📋 س.ت: {cr_num} &nbsp;|&nbsp; 🧾 ب.ض: {tax_num} &nbsp;|&nbsp; 📞 هاتف: {contact_num} &nbsp;|&nbsp; ✉️ بريد: {email_addr} &nbsp;|&nbsp; 🔑 ترخيص: {lic_num}</div>
            </div>
            {logo_html}
        </div>
        """,
        unsafe_allow_html=True
    )

if not str_lit.session_state.is_authenticated:
    lic_info = get_client_license()
    
    col_t_l1, col_t_l2, col_t_l3 = str_lit.columns([3, 1, 3])
    with col_t_l2:
        current_theme_idx = 0 if str_lit.session_state.theme_mode == "Dark" else 1
        new_theme = str_lit.radio("مظهر الشاشة", ["🌙 دارك (Dark)", "☀️ لايت (Light)"], index=current_theme_idx, horizontal=True)
        selected_mode = "Dark" if "دارك" in new_theme else "Light"
        if selected_mode != str_lit.session_state.theme_mode:
            str_lit.session_state.theme_mode = selected_mode
            str_lit.rerun()

    str_lit.markdown(
        f"""
        <div style="max-width: 480px; margin: 10px auto 20px auto; background: {card_bg}; backdrop-filter: blur(20px); padding: 30px; border-radius: 16px; box-shadow: 0 10px 30px rgba(0,0,0,0.2); text-align: center; border: 1px solid rgba(255,255,255,0.08);">
            <h2 style="color: #F87171; margin-bottom: 6px; font-size: 20px;">النظام المتكامل لشؤون الموظفين</h2>
            <p style="font-size: 14px; font-weight: bold; margin-bottom: 4px;">{lic_info.get('name', '')}</p>
            <p style="color: #94A3B8; font-size: 12px;">رقم الترخيص: {lic_info.get('license', '')}</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    col_l1, col_l2, col_l3 = str_lit.columns([1, 2, 1])
    with col_l2:
        with str_lit.form("login_pattern_form"):
            usernames = str_lit.session_state.users["اسم المستخدم"].tolist()
            selected_user_login = str_lit.selectbox("اختر المستخدم", usernames)
            pattern_input = str_lit.text_input("أدخل تسلسل الرسم السري", type="password", placeholder="مثل: 1-2-3")
            if str_lit.form_submit_button("▶️ تشغيل النظام", use_container_width=True):
                user_record = str_lit.session_state.users[str_lit.session_state.users["اسم المستخدم"] == selected_user_login].iloc[0]
                if user_record.get("الحالة", "نشط") == "إيقاف":
                    str_lit.error("❌ هذا المستخدم موقوف عن العمل!")
                elif pattern_input.strip() == str(user_record["الرسم السري"]).strip():
                    str_lit.session_state.is_authenticated = True
                    str_lit.session_state.current_logged_user = selected_user_login
                    str_lit.session_state.current_user_dept = user_record["القسم التابع"]
                    str_lit.session_state.current_user_branch = user_record["الفرع التابع"]
                    str_lit.session_state.current_user_role = user_record["الصلاحية"]
                    str_lit.success("تم تسجيل الدخول بنجاح!")
                    str_lit.rerun()
                else:
                    str_lit.error("❌ الرسم السري غير صحيح!")
    str_lit.stop()

str_lit.markdown('<div class="sticky-top-wrapper">', unsafe_allow_html=True)
render_company_header()

col_ub1, col_ub2 = str_lit.columns([4, 1])
with col_ub1:
    logged_username = str_lit.session_state.current_logged_user
    user_role = str_lit.session_state.current_user_role
    user_branch = str_lit.session_state.current_user_branch
    user_dept = str_lit.session_state.current_user_dept

    str_lit.markdown(
        f"""
        <div class="user-badge-box">
            👤 المستخدم الحالي: <b>{logged_username}</b> &nbsp;|&nbsp; 🛡️ الصلاحية: <b>{user_role}</b> &nbsp;|&nbsp; 📍 الفرع: <b>{user_branch}</b> &nbsp;|&nbsp; 🏢 القسم: <b>{user_dept}</b>
        </div>
        """,
        unsafe_allow_html=True
    )

with col_ub2:
    current_theme_idx = 0 if str_lit.session_state.theme_mode == "Dark" else 1
    new_theme_main = str_lit.selectbox("المظهر", ["🌙 دارك", "☀️ لايت"], index=current_theme_idx, key="theme_selector_main")
    main_selected_mode = "Dark" if "دارك" in new_theme_main else "Light"
    if main_selected_mode != str_lit.session_state.theme_mode:
        str_lit.session_state.theme_mode = main_selected_mode
        str_lit.rerun()

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

sec_cols = str_lit.columns(len(main_sections))
for idx, sec_name in enumerate(main_sections):
    with sec_cols[idx]:
        if str_lit.button(sec_name, use_container_width=True, key=f"btn_sec_{idx}"):
            str_lit.session_state.active_main_section = sec_name
            str_lit.rerun()

selected_main_cat = str_lit.session_state.active_main_section

sub_options_map = {
    "الرئيسية": ["لوحة التحكم والمؤشرات"],
    "الحضور والانصراف": ["تسجيل حضور وانصراف", "سجل الحضور والانصراف", "تعديل أو حذف حركة حضور"],
    "طلبات الاجازة": ["تسجيل طلب إجازة", "سجل طلبات قيد الانتظار", "سجل الطلبات المقبولة", "سجل الطلبات المرفوضة", "تعديل أو حذف طلب إجازة"],
    "المعاملات المالية": ["تسجيل معاملة مالية", "تسجيل إذن (انصراف / تأخير)", "سجل المعاملات المالية", "تعديل أو حذف معاملة مالية"],
    "كشف الرواتب": ["كشف الرواتب والمستحقات الشامل"],
    "شؤون الموظفين": ["إضافة موظف جديد", "سجل الموظفين والأرصدة الشاملة", "تعديل أو حذف موظف"],
    "المستخدمين": ["إضافة مستخدم جديد", "إدارة المستخدمين والصلاحيات والسجل", "تعديل أو حذف مستخدم"],
    "التقارير": ["طباعة التقارير العامة"],
    "اعدادات الشركة": ["إعدادات الشركة وبياناتها الشاملة"],
    "أدوات النظام": ["تصدير وتحميل Excel", "نسخة احتياطية واستعادة", "مسح البيانات"]
}

str_lit.markdown('<div class="cinema-top-bar" style="margin-top: 1px;">', unsafe_allow_html=True)
col_sub1, col_sub2 = str_lit.columns([4, 1])

with col_sub1:
    sub_options_list = sub_options_map.get(selected_main_cat, ["لوحة التحكم والمؤشرات"])
    choice = str_lit.selectbox(f"📑 العمليات الفرعية لقسم ({selected_main_cat}):", sub_options_list)

with col_sub2:
    str_lit.write("")
    if str_lit.button("⏹️ خروج", use_container_width=True):
        str_lit.session_state.is_authenticated = False
        str_lit.session_state.current_logged_user = ""
        str_lit.rerun()

str_lit.markdown('</div>', unsafe_allow_html=True)
str_lit.markdown('</div>', unsafe_allow_html=True)

str_lit.markdown('<div class="main-content-spacer"></div>', unsafe_allow_html=True)

if "Admin" in user_role or "الإدارة العليا" in user_dept:
    view_employees = str_lit.session_state.employees
    view_requests = str_lit.session_state.requests
else:
    view_employees = str_lit.session_state.employees[str_lit.session_state.employees["الفرع"] == user_branch]
    view_requests = str_lit.session_state.requests[str_lit.session_state.requests["الفرع"] == user_branch]

total_emps = len(view_employees)
pending_requests = view_requests[view_requests['الحالة'] == 'قيد الانتظار'] if not view_requests.empty else pd.DataFrame()
pending_count = len(pending_requests)
accepted_count = len(view_requests[view_requests['الحالة'] == 'مقبول']) if not view_requests.empty else 0

col1, col2, col3, col4 = str_lit.columns(4)
with col1:
    str_lit.markdown(f'<div class="glass-card"><div class="glass-card-title">👥 إجمالي نجوم الشركة</div><div class="glass-card-value">{total_emps}</div></div>', unsafe_allow_html=True)
with col2:
    str_lit.markdown(f'<div class="glass-card" style="border-right-color: #F59E0B;"><div class="glass-card-title">⏳ عروض قيد الانتظار</div><div class="glass-card-value" style="color: #F59E0B;">{pending_count}</div></div>', unsafe_allow_html=True)
with col3:
    str_lit.markdown(f'<div class="glass-card" style="border-right-color: #10B981;"><div class="glass-card-title">✅ العروض المقبولة</div><div class="glass-card-value" style="color: #10B981;">{accepted_count}</div></div>', unsafe_allow_html=True)
with col4:
    active_users_count = len(str_lit.session_state.users[str_lit.session_state.users["الحالة"] == "نشط"]) if not str_lit.session_state.users.empty else 0
    str_lit.markdown(f'<div class="glass-card" style="border-right-color: #3B82F6;"><div class="glass-card-title">🛡️ المستخدمين النشطين</div><div class="glass-card-value" style="font-size: 18px; color: #3B82F6;">{active_users_count} مستخدم</div></div>', unsafe_allow_html=True)

str_lit.markdown("<hr style='border: 0.5px solid rgba(255,255,255,0.08); margin: 8px 0 12px 0;'>", unsafe_allow_html=True)

# نظام التنبيهات والرسائل التحذيرية الذكية للعقود والمستندات (قبلها بشهر)
if selected_main_cat == "الرئيسية" and choice == "لوحة التحكم والمؤشرات":
    str_lit.markdown(f'<div class="section-header">🔔 التنبيهات والإنذارات المبكرة لعقود الموظفين (قبل انتهاء العقد بشهر)</div>', unsafe_allow_html=True)
    
    today = datetime.now()
    warning_flag = False

    if not str_lit.session_state.employees.empty:
        for idx, emp_row in str_lit.session_state.employees.iterrows():
            emp_name = emp_row.get("اسم الموظف", "غير معروف")
            end_contract_str = emp_row.get("تاريخ نهاية العقد", "")
            if end_contract_str:
                try:
                    exp_date = datetime.strptime(str(end_contract_str).strip(), "%Y-%m-%d")
                    days_remaining = (exp_date - today).days

                    if 0 <= days_remaining <= 30:
                        warning_flag = True
                        str_lit.warning(
                            f"⚠️ **تنبيه انتهاء عقد:** عقد الموظف (**{emp_name}**) متبقي على انتهائه **{days_remaining} يوم فقط** (تاريخ الانتهاء: {end_contract_str}).",
                            icon="🚨"
                        )
                    elif days_remaining < 0:
                        warning_flag = True
                        str_lit.error(
                            f"❌ **تجاوز موعد العقد:** عقد الموظف (**{emp_name}**) انتهى منذ {-days_remaining} يوم!",
                            icon="🚫"
                        )
                except Exception:
                    pass

    if not warning_flag:
        str_lit.success("✅ جميع عقود ومستندات الموظفين سارية ولا توجد أي تحذيرات قريبة خلال الشهر القادم.")
    
    str_lit.markdown("<hr style='border: 0.5px dashed rgba(255,255,255,0.1); margin: 10px 0;'>", unsafe_allow_html=True)

if selected_main_cat == "الرئيسية" or choice == "لوحة التحكم والمؤشرات":
    if selected_main_cat == "الرئيسية" and choice == "لوحة التحكم والمؤشرات":
        str_lit.markdown(f'<div class="section-header">📊 داشبورد ومخطط بيانات لكل فرع (بيانات تفصيلية)</div>', unsafe_allow_html=True)
        all_branches = str_lit.session_state.employees["الفرع"].unique().tolist() if not str_lit.session_state.employees.empty else ["المركز الرئيسي"]
        for branch in all_branches:
            str_lit.markdown(f"### 📍 فرع: {branch}")
            branch_emps = str_lit.session_state.employees[str_lit.session_state.employees["الفرع"] == branch]
            b_count = len(branch_emps)
            b_sal_total = float(branch_emps["الراتب الأساسي"].sum()) if (not branch_emps.empty and "الراتب الأساسي" in branch_emps.columns) else 0.0
            b_att = str_lit.session_state.attendance[str_lit.session_state.attendance["الفرع"] == branch] if not str_lit.session_state.attendance.empty else pd.DataFrame()
            b_att_count = len(b_att)
            
            bc1, bc2, bc3 = str_lit.columns(3)
            with bc1:
                str_lit.markdown(f'<div class="glass-card"><div class="glass-card-title">👥 عدد الموظفين بالفرع</div><div class="glass-card-value">{b_count}</div></div>', unsafe_allow_html=True)
            with bc2:
                str_lit.markdown(f'<div class="glass-card" style="border-right-color: #3B82F6;"><div class="glass-card-title">💰 إجمالي رواتب الفرع</div><div class="glass-card-value" style="font-size: 18px; color: #3B82F6;">{b_sal_total:,.0f} ج.م</div></div>', unsafe_allow_html=True)
            with bc3:
                str_lit.markdown(f'<div class="glass-card" style="border-right-color: #10B981;"><div class="glass-card-title">⏱️ حركات الحضور المسجلة</div><div class="glass-card-value" style="color: #10B981;">{b_att_count}</div></div>', unsafe_allow_html=True)
            
            if not branch_emps.empty:
                str_lit.markdown(f"**📋 جدول موظفي فرع ({branch}):**")
                default_cols = ["كود الموظف", "اسم الموظف", "الوظيفة", "القسم", "الراتب الأساسي", "تاريخ بداية العقد", "تاريخ نهاية العقد"]
                available_cols = [col for col in default_cols if col in branch_emps.columns]
                render_printable_table(branch_emps[available_cols])
            else:
                str_lit.info(f"لا توجد موظفين مسجلين في فرع {branch}.")
            str_lit.markdown("<hr style='border: 0.5px dashed rgba(255,255,255,0.1); margin: 10px 0;'>", unsafe_allow_html=True)

if choice == "تسجيل حضور وانصراف":
    str_lit.subheader("⏱️ تسجيل حركة الحضور والانصراف")
    emp_names = str_lit.session_state.employees["اسم الموظف"].tolist()
    if emp_names:
        str_lit.markdown('<div class="entry-form-area">', unsafe_allow_html=True)
        with str_lit.form("att_form_custom_time_full"):
            selected_emp = str_lit.selectbox("اختر الموظف", emp_names)
            att_date = str_lit.date_input("تاريخ الحركة", value=date.today())
            emp_info = str_lit.session_state.employees[str_lit.session_state.employees["اسم الموظف"] == selected_emp].iloc[0]
            c_job = emp_info["الوظيفة"]
            c_branch = emp_info["الفرع"]
            str_lit.info(f"📍 الفرع: {c_branch} &nbsp;|&nbsp; 💼 الوظيفة: {c_job}")
            
            str_lit.markdown("---")
            str_lit.markdown("🕒 **المواعيد الرسمية للعمل:**")
            col_rs1, col_rs2, col_rs3 = str_lit.columns(3)
            with col_rs1: start_h = str_lit.selectbox("ساعة البداية الرسمية", list(range(1, 13)), index=7)
            with col_rs2: start_m = str_lit.selectbox("دقيقة البداية (00-59)", list(range(0, 60)), index=0)
            with col_rs3: start_ampm = str_lit.selectbox("فترة البداية", ["AM", "PM"], index=0)

            col_re1, col_re2, col_re3 = str_lit.columns(3)
            with col_re1: end_h = str_lit.selectbox("ساعة النهاية الرسمية", list(range(1, 13)), index=3)
            with col_re2: end_m = str_lit.selectbox("دقيقة النهاية (00-59)", list(range(0, 60)), index=0)
            with col_re3: end_ampm = str_lit.selectbox("فترة النهاية", ["AM", "PM"], index=1)

            grace_period_min = str_lit.number_input("فترة السماح (بالدقائق)", min_value=0, max_value=60, value=15)

            str_lit.markdown("---")
            str_lit.markdown("⏰ **الأوقات الفعلية للحضور والانصراف:**")
            col_in1, col_in2, col_in3 = str_lit.columns(3)
            with col_in1: act_in_h = str_lit.selectbox("ساعة الحضور الفعلي", list(range(1, 13)), index=7, key="ain_h")
            with col_in2: act_in_m = str_lit.selectbox("دقيقة الحضور الفعلي (00-59)", list(range(0, 60)), index=0, key="ain_m")
            with col_in3: act_in_ampm = str_lit.selectbox("فترة الحضور الفعلي", ["AM", "PM"], index=0, key="ain_ap")

            col_out1, col_out2, col_out3 = str_lit.columns(3)
            with col_out1: act_out_h = str_lit.selectbox("ساعة الانصراف الفعلي", list(range(1, 13)), index=3, key="aout_h")
            with col_out2: act_out_m = str_lit.selectbox("دقيقة الانصراف الفعلي (00-59)", list(range(0, 60)), index=0, key="aout_m")
            with col_out3: act_out_ampm = str_lit.selectbox("فترة الانصراف الفعلي", ["AM", "PM"], index=1, key="aout_ap")

            att_status = str_lit.selectbox("حالة الحضور", ["حضور منتظم", "إجازة أسبوعية", "إجازة سنوية", "إجازة مرضية", "إجازة بدون أجر", "غياب"])
            
            if str_lit.form_submit_button("💾 حساب تلقائي وحفظ الحركة", use_container_width=True):
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

                new_att_row = {
                    "التاريخ": att_date.strftime("%Y-%m-%d"),
                    "كود الموظف": emp_info["كود الموظف"],
                    "اسم الموظف": selected_emp,
                    "الوظيفة": c_job,
                    "الفرع": c_branch,
                    "بداية العمل الرسمية": f"{start_h:02d}:{start_m:02d} {start_ampm}",
                    "نهاية العمل الرسمية": f"{end_h:02d}:{end_m:02d} {end_ampm}",
                    "وقت الحضور الفعلي": f"{act_in_h:02d}:{act_in_m:02d} {act_in_ampm}",
                    "وقت الانصراف الفعلي": f"{act_out_h:02d}:{act_out_m:02d} {act_out_ampm}",
                    "فترة السماح (دقيقة)": int(grace_period_min),
                    "الحالة": att_status,
                    "التأخير (دقيقة)": int(tardy_min),
                    "إضافي (دقيقة)": int(overtime_min)
                }

                str_lit.session_state.attendance = pd.concat([str_lit.session_state.attendance, pd.DataFrame([new_att_row])], ignore_index=True)
                auto_save_data()
                str_lit.success("✅ تم تسجيل وحفظ حركة الحضور والانصراف بنجاح!")
        str_lit.markdown('</div>', unsafe_allow_html=True)

if choice == "سجل الحضور والانصراف":
    str_lit.subheader("📋 سجل الحضور والانصراف الشامل")
    render_printable_table(str_lit.session_state.attendance)

if choice == "إضافة موظف جديد":
    str_lit.subheader("➕ إضافة موظف جديد إلى المنظومة وتحديد مدة العقد")
    str_lit.markdown('<div class="entry-form-area">', unsafe_allow_html=True)
    with str_lit.form("add_new_emp_form_full"):
        col_e1, col_e2 = str_lit.columns(2)
        with col_e1:
            emp_code_in = str_lit.text_input("كود الموظف", value=f"EMP{len(str_lit.session_state.employees)+1:03d}")
            emp_name_in = str_lit.text_input("اسم الموظف الرباعي")
            emp_job_in = str_lit.text_input("الوظيفة / المسمى الوظيفي")
            emp_dept_in = str_lit.text_input("القسم التابع")
            emp_branch_in = str_lit.selectbox("الفرع التابع", ["المركز الرئيسي", "فرع الإسكندرية", "فرع الشرم"])
        with col_e2:
            emp_role_in = str_lit.selectbox("صلاحية الموظف بالنظام", ["مستخدم عادي", "اعتماد الطلبات", "مدير الفرع"])
            emp_salary_in = str_lit.number_input("الراتب الأساسي (ج.م)", min_value=0.0, value=5000.0, step=100.0)
            emp_docs_in = str_lit.text_input("مسوغات التعيين (مستندات مكتملة/ناقصة)")
            contract_start_in = str_lit.date_input("تاريخ بداية العقد", value=date.today())
            contract_end_in = str_lit.date_input("تاريخ نهاية العقد", value=date.today() + timedelta(days=365))

        str_lit.markdown("---")
        str_lit.markdown("📌 **أرصدة الإجازات السنوية والأسبوعية والرسمية:**")
        col_b1, col_b2, col_b3, col_b4 = str_lit.columns(4)
        with col_b1:
            ann_total = str_lit.number_input("رصيد سنوي (إجمالي)", value=21)
            ann_used = str_lit.number_input("سنوي مستهلك", value=0)
        with col_b2:
            week_total = str_lit.number_input("رصيد أسبوعي (إجمالي)", value=4)
            week_used = str_lit.number_input("أسبوعي مستهلك", value=0)
        with col_b3:
            off_total = str_lit.number_input("رصيد رسمي (إجمالي)", value=10)
            off_used = str_lit.number_input("رسمي مستهلك", value=0)
        with col_b4:
            sick_days = str_lit.number_input("إجازات مرضية (أيام)", value=0)

        if str_lit.form_submit_button("💾 حفظ بيانات الموظف الجديد والعقد", use_container_width=True):
            if emp_name_in.strip() == "":
                str_lit.error("❌ يرجى إدخال اسم الموظف!")
            else:
                new_emp_data = {
                    "كود الموظف": emp_code_in,
                    "اسم الموظف": emp_name_in,
                    "الوظيفة": emp_job_in,
                    "القسم": emp_dept_in,
                    "الفرع": emp_branch_in,
                    "صلاحية الموظف": emp_role_in,
                    "الراتب الأساسي": float(emp_salary_in),
                    "مسوغات التعيين": emp_docs_in,
                    "تاريخ بداية العقد": contract_start_in.strftime("%Y-%m-%d"),
                    "تاريخ نهاية العقد": contract_end_in.strftime("%Y-%m-%d"),
                    "رصيد سنوي (إجمالي)": int(ann_total),
                    "سنوي مستهلك": int(ann_used),
                    "سنوي متبقي": int(ann_total - ann_used),
                    "رصيد أسبوعي (إجمالي)": int(week_total),
                    "أسبوعي مستهلك": int(week_used),
                    "أسبوعي متبقي": int(week_total - week_used),
                    "رصيد رسمي (إجمالي)": int(off_total),
                    "رسمي مستهلك": int(off_used),
                    "رسمي متبقي": int(off_total - off_used),
                    "إجازات مرضية (أيام)": int(sick_days)
                }
                str_lit.session_state.employees = pd.concat([str_lit.session_state.employees, pd.DataFrame([new_emp_data])], ignore_index=True)
                auto_save_data()
                str_lit.success(f"✅ تم إضافة الموظف ({emp_name_in}) وتحديد فترة عقده بنجاح!")
    str_lit.markdown('</div>', unsafe_allow_html=True)

if choice == "سجل الموظفين والأرصدة الشاملة":
    str_lit.subheader("👥 سجل الموظفين وتواريخ العقود والأرصدة الشاملة")
    render_printable_table(str_lit.session_state.employees)

if choice == "تعديل أو حذف موظف":
    str_lit.subheader("✏️ تعديل بيانات وتواريخ عقود الموظفين أو حذف موظف")
    if not str_lit.session_state.employees.empty:
        emp_names_edit = str_lit.session_state.employees["اسم الموظف"].tolist()
        selected_emp_edit = str_lit.selectbox("اختر الموظف للتعديل أو الحذف", emp_names_edit)
        
        emp_row_data = str_lit.session_state.employees[str_lit.session_state.employees["اسم الموظف"] == selected_emp_edit].iloc[0]
        emp_idx = str_lit.session_state.employees[str_lit.session_state.employees["اسم الموظف"] == selected_emp_edit].index[0]

        str_lit.markdown('<div class="entry-form-area">', unsafe_allow_html=True)
        with str_lit.form("edit_emp_contract_form"):
            str_lit.markdown(f"### تعديل بيانات الموظف: {selected_emp_edit}")
            
            e_name = str_lit.text_input("اسم الموظف", value=str(emp_row_data["اسم الموظف"]))
            e_job = str_lit.text_input("الوظيفة", value=str(emp_row_data["الوظيفة"]))
            e_dept = str_lit.text_input("القسم", value=str(emp_row_data["القسم"]))
            e_salary = str_lit.number_input("الراتب الأساسي", min_value=0.0, value=float(emp_row_data["الراتب الأساسي"]))
            
            # استخراج تواريخ البداية والنهاية للعقد الحالي لتعبئتها افتراضياً
            try:
                default_start = datetime.strptime(str(emp_row_data.get("تاريخ بداية العقد", date.today())), "%Y-%m-%d").date()
            except Exception:
                default_start = date.today()
                
            try:
                default_end = datetime.strptime(str(emp_row_data.get("تاريخ نهاية العقد", date.today())), "%Y-%m-%d").date()
            except Exception:
                default_end = date.today() + timedelta(days=365)

            e_contract_start = str_lit.date_input("تاريخ بداية العقد", value=default_start)
            e_contract_end = str_lit.date_input("تاريخ نهاية العقد", value=default_end)

            col_sub_ed1, col_sub_ed2 = str_lit.columns(2)
            with col_sub_ed1:
                update_btn = str_lit.form_submit_button("💾 حفظ التعديلات وتحديث العقد", use_container_width=True)
            with col_sub_ed2:
                delete_btn = str_lit.form_submit_button("🗑️ حذف هذا الموظف نهائياً", use_container_width=True)

            if update_btn:
                str_lit.session_state.employees.at[emp_idx, "اسم الموظف"] = e_name
                str_lit.session_state.employees.at[emp_idx, "الوظيفة"] = e_job
                str_lit.session_state.employees.at[emp_idx, "القسم"] = e_dept
                str_lit.session_state.employees.at[emp_idx, "الراتب الأساسي"] = float(e_salary)
                str_lit.session_state.employees.at[emp_idx, "تاريخ بداية العقد"] = e_contract_start.strftime("%Y-%m-%d")
                str_lit.session_state.employees.at[emp_idx, "تاريخ نهاية العقد"] = e_contract_end.strftime("%Y-%m-%d")
                auto_save_data()
                str_lit.success("✅ تم تحديث بيانات الموظف وتاريخ العقد بنجاح!")
                str_lit.rerun()

            if delete_btn:
                str_lit.session_state.employees = str_lit.session_state.employees.drop(emp_idx).reset_index(drop=True)
                auto_save_data()
                str_lit.warning("🗑️ تم حذف الموظف بنجاح من النظام!")
                str_lit.rerun()

        str_lit.markdown('</div>', unsafe_allow_html=True)
    else:
        str_lit.info("لا توجد مسجلات موظفين حالياً.")

if choice == "إعدادات الشركة وبياناتها الشاملة":
    str_lit.subheader("⚙️ إعدادات وبيانات الشركة الرسمية")
    info = str_lit.session_state.company_info
    str_lit.markdown('<div class="entry-form-area">', unsafe_allow_html=True)
    with str_lit.form("company_settings_form_full"):
        c_name_in = str_lit.text_input("اسم الشركة الرسمي", value=info.get("name", ""))
        c_addr_in = str_lit.text_input("عنوان الشركة", value=info.get("address", ""))
        col_s1, col_s2 = str_lit.columns(2)
        with col_s1:
            c_cr_in = str_lit.text_input("السجل التجاري", value=info.get("cr", ""))
            c_tax_in = str_lit.text_input("البطاقة الضريبية", value=info.get("tax", ""))
        with col_s2:
            c_contact_in = str_lit.text_input("رقم الهاتف", value=info.get("contact", ""))
            c_email_in = str_lit.text_input("البريد الإلكتروني", value=info.get("email", ""))
        
        c_lic_in = str_lit.text_input("رقم الترخيص الرسمي", value=info.get("license", ""))
        c_logo_in = str_lit.text_input("رابط الشعار (URL أو Base64)", value=info.get("logo", ""))

        if str_lit.form_submit_button("💾 حفظ تحديثات إعدادات الشركة", use_container_width=True):
            str_lit.session_state.company_info = {
                "name": c_name_in,
                "address": c_addr_in,
                "cr": c_cr_in,
                "tax": c_tax_in,
                "contact": c_contact_in,
                "email": c_email_in,
                "license": c_lic_in,
                "logo": c_logo_in
            }
            auto_save_data()
            str_lit.success("✅ تم تحديث وحفظ إعدادات الشركة بنجاح!")
    str_lit.markdown('</div>', unsafe_allow_html=True)

if choice == "تصدير وتحميل Excel":
    str_lit.subheader("📥 تصدير وتحميل بيانات النظام كملفات جاهزة")
    str_lit.info("يمكنك تصدير كافة بيانات النظام وجداول الموظفين والحضور والرواتب بكل سهولة واستخدام زر التحميل أسفل كل جدول.")
    render_printable_table(str_lit.session_state.employees)

if choice == "نسخة احتياطية واستعادة":
    str_lit.subheader("💾 النسخ الاحتياطي واستعادة بيانات المنظومة")
    col_bk1, col_bk2 = str_lit.columns(2)
    with col_bk1:
        str_lit.markdown("### تصدير نسخة احتياطية كاملة (JSON)")
        try:
            full_export_data = {
                "employees": str_lit.session_state.employees.to_dict(orient='records'),
                "requests": str_lit.session_state.requests.to_dict(orient='records'),
                "attendance": str_lit.session_state.attendance.to_dict(orient='records'),
                "financial_transactions": str_lit.session_state.financial_transactions.to_dict(orient='records'),
                "users": str_lit.session_state.users.to_dict(orient='records'),
                "company_info": str_lit.session_state.company_info
            }
            json_str = json.dumps(full_export_data, ensure_ascii=False, indent=4)
            str_lit.download_button(
                label="📥 تحميل النسخة الاحتياطية الكاملة",
                data=json_str.encode('utf-8-sig'),
                file_name=f"ERP_Backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                use_container_width=True
            )
        except Exception as e:
            str_lit.error(f"خطأ في تجهيز النسخة الاحتياطية: {e}")

    with col_bk2:
        str_lit.markdown("### استعادة البيانات من نسخة احتياطية")
        uploaded_backup = str_lit.file_uploader("اختر ملف النسخة الاحتياطية (.json)", type=["json"])
        if uploaded_backup is not None:
            if str_lit.button("🔄 تنفيذ استعادة البيانات", use_container_width=True):
                try:
                    imported_data = json.load(uploaded_backup)
                    if "employees" in imported_data:
                        str_lit.session_state.employees = pd.DataFrame(imported_data["employees"])
                    if "requests" in imported_data:
                        str_lit.session_state.requests = pd.DataFrame(imported_data["requests"])
                    if "attendance" in imported_data:
                        str_lit.session_state.attendance = pd.DataFrame(imported_data["attendance"])
                    if "financial_transactions" in imported_data:
                        str_lit.session_state.financial_transactions = pd.DataFrame(imported_data["financial_transactions"])
                    if "users" in imported_data:
                        str_lit.session_state.users = pd.DataFrame(imported_data["users"])
                    if "company_info" in imported_data:
                        str_lit.session_state.company_info = imported_data["company_info"]
                    auto_save_data()
                    str_lit.success("✅ تمت استعادة البيانات بنجاح تام!")
                    str_lit.rerun()
                except Exception as e:
                    str_lit.error(f"❌ خطأ أثناء استعادة الملف: {e}")

if choice == "إدارة المستخدمين والصلاحيات والسجل" or choice == "إضافة مستخدم جديد":
    str_lit.subheader("🛡️ إدارة مستخدمي النظام والصلاحيات")
    render_printable_table(str_lit.session_state.users)
    
    str_lit.markdown("### ➕ إضافة مستخدم جديد للنظام")
    str_lit.markdown('<div class="entry-form-area">', unsafe_allow_html=True)
    with str_lit.form("add_user_form_full"):
        u_name_in = str_lit.text_input("اسم المستخدم (Username لحساب الدخول)")
        u_full_in = str_lit.text_input("الاسم الكامل للموظف")
        col_u1, col_u2 = str_lit.columns(2)
        with col_u1:
            u_branch_in = str_lit.selectbox("الفرع التابع", ["المركز الرئيسي", "فرع الإسكندرية", "فرع الشرم"])
            u_dept_in = str_lit.text_input("القسم التابع", value="شؤون الموظفين")
        with col_u2:
            u_role_in = str_lit.selectbox("الصلاحية", ["مشرف عام (Admin)", "مدير فرع", "مستخدم عادي"])
            u_email_in = str_lit.text_input("البريد الإلكتروني")
        
        u_pattern_in = str_lit.text_input("الرسم السري (مثل: 1-2-3)", value="1-2-3")
        u_status_in = str_lit.selectbox("حالة المستخدم", ["نشط", "إيقاف"])

        if str_lit.form_submit_button("💾 حفظ وتسجيل المستخدم الجديد", use_container_width=True):
            if u_name_in.strip() == "":
                str_lit.error("❌ يرجى إدخال اسم المستخدم!")
            else:
                new_user_row = {
                    "اسم المستخدم": u_name_in.strip(),
                    "الاسم الكامل": u_full_in,
                    "الفرع التابع": u_branch_in,
                    "القسم التابع": u_dept_in,
                    "الصلاحية": u_role_in,
                    "البريد الإلكتروني": u_email_in,
                    "الحالة": u_status_in,
                    "الرسم السري": u_pattern_in.strip()
                }
                str_lit.session_state.users = pd.concat([str_lit.session_state.users, pd.DataFrame([new_user_row])], ignore_index=True)
                auto_save_data()
                str_lit.success(f"✅ تم إضافة المستخدم ({u_name_in}) بنجاح!")
    str_lit.markdown('</div>', unsafe_allow_html=True)

if choice == "كشف الرواتب والمستحقات الشامل":
    str_lit.subheader("💰 كشف الرواتب والمستحقات الشامل للشركة")
    if not str_lit.session_state.employees.empty:
        df_sal = str_lit.session_state.employees[["كود الموظف", "اسم الموظف", "الوظيفة", "القسم", "الفرع", "الراتب الأساسي"]].copy()
        df_sal["بدلات وحوافز"] = 0.0
        df_sal["خصومات وإذونات"] = 0.0
        df_sal["الصافي المستحق"] = df_sal["الراتب الأساسي"]
        render_printable_table(df_sal)
    else:
        str_lit.info("لا توجد بيانات رواتب لعرضها.")

if choice == "مسح البيانات":
    str_lit.subheader("⚠️ مسح وتصفير بيانات المنظومة")
    str_lit.warning("تحذير: سيؤدي هذا الإجراء إلى مسح كافة البيانات المسجلة وإعادة ضبط المصنع للبرنامج.")
    if str_lit.button("🚨 تأكيد مسح كافة البيانات", type="primary"):
        str_lit.session_state.employees = pd.DataFrame(columns=[
            "كود الموظف", "اسم الموظف", "الوظيفة", "القسم", "الفرع", "صلاحية الموظف",
            "الراتب الأساسي", "مسوغات التعيين", "تاريخ بداية العقد", "تاريخ نهاية العقد",
            "رصيد سنوي (إجمالي)", "سنوي مستهلك", "سنوي متبقي",
            "رصيد أسبوعي (إجمالي)", "أسبوعي مستهلك", "أسبوعي متبقي",
            "رصيد رسمي (إجمالي)", "رسمي مستهلك", "رسمي متبقي",
            "إجازات مرضية (أيام)"
        ])
        str_lit.session_state.requests = pd.DataFrame(columns=[
            "رقم الطلب", "كود الموظف", "اسم الموظف", "الوظيفة", "الفرع", "نوع الإجازة", "من تاريخ", "إلى تاريخ", "عدد الأيام", "السبب", "الحالة"
        ])
        str_lit.session_state.attendance = pd.DataFrame(columns=[
            "التاريخ", "كود الموظف", "اسم الموظف", "الوظيفة", "الفرع", 
            "بداية العمل الرسمية", "نهاية العمل الرسمية", "وقت الحضور الفعلي", "وقت الانصراف الفعلي", 
            "فترة السماح (دقيقة)", "الحالة", "التأخير (دقيقة)", "إضافي (دقيقة)"
        ])
        str_lit.session_state.financial_transactions = pd.DataFrame(columns=[
            "التاريخ", "كود الموظف", "اسم الموظف", "الفرع", "النوع", "المبلغ / القيمة", "البيان / السبب"
        ])
        auto_save_data()
        str_lit.success("✅ تم تصفير بيانات المنظومة بنجاح!")
        str_lit.rerun()

str_lit.markdown("<hr style='border: 0.5px solid rgba(255,255,255,0.08); margin: 20px 0;'>", unsafe_allow_html=True)
str_lit.markdown("<p style='text-align: center; color: #94A3B8; font-size: 11px;'>جميع الحقوق محفوظة © النظام المتكامل لإدارة الموارد البشرية (ERP)</p>", unsafe_allow_html=True)