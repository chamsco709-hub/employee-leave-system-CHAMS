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
    page_icon="💼",
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
os.makedirs(COMPANIES_DIR, exist_ok=True)

DOCS_DIR = "client_employees_docs"
os.makedirs(DOCS_DIR, exist_ok=True)

COMPANY_FILE = os.path.join(COMPANIES_DIR, f"{company_id}_data.json")

def load_company_data():
    if os.path.exists(COMPANY_FILE):
        try:
            with open(COMPANY_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                
                if "employees" in data and len(data["employees"]) > 0:
                    df_emp = pd.DataFrame(data["employees"])
                    if "مسوغات التعيين" not in df_emp.columns: df_emp["مسوغات التعيين"] = "مكتملة"
                    if "ملف المستندات" not in df_emp.columns: df_emp["ملف المستندات"] = ""
                    if "تاريخ بداية العقد" not in df_emp.columns: df_emp["تاريخ بداية العقد"] = str(date.today())
                    if "تاريخ نهاية العقد" not in df_emp.columns: df_emp["تاريخ نهاية العقد"] = str(date.today() + timedelta(days=365))
                    if "رصيد سنوي (إجمالي)" not in df_emp.columns: df_emp["رصيد سنوي (إجمالي)"] = 21
                    if "رصيد أسبوعي (إجمالي)" not in df_emp.columns: df_emp["رصيد أسبوعي (إجمالي)"] = 4
                    if "رصيد رسمي (إجمالي)" not in df_emp.columns: df_emp["رصيد رسمي (إجمالي)"] = 10
                    if "إجازات مرضية (أيام)" not in df_emp.columns: df_emp["إجازات مرضية (أيام)"] = 0
                    str_lit.session_state.employees = df_emp
                else:
                    str_lit.session_state.employees = pd.DataFrame(columns=[
                        "كود الموظف", "اسم الموظف", "الوظيفة", "القسم", "الفرع", "صلاحية الموظف",
                        "الراتب الأساسي", "مسوغات التعيين", "ملف المستندات", "تاريخ بداية العقد", "تاريخ نهاية العقد",
                        "رصيد سنوي (إجمالي)", "رصيد أسبوعي (إجمالي)", "رصيد رسمي (إجمالي)", "إجازات مرضية (أيام)"
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
                        if col not in df_att.columns: df_att[col] = 0 if "(دقيقة)" in col else ""
                    str_lit.session_state.attendance = df_att[expected_att_cols]
                else:
                    str_lit.session_state.attendance = pd.DataFrame(columns=[
                        "التاريخ", "كود الموظف", "اسم الموظف", "الوظيفة", "الفرع", 
                        "بداية العمل الرسمية", "نهاية العمل الرسمية", "وقت الحضور الفعلي", "وقت الانصراف الفعلي", 
                        "فترة السماح (دقيقة)", "الحالة", "التأخير (دقيقة)", "إضافي (دقيقة)"
                    ])

                if "financial_transactions" in data and len(data["financial_transactions"]) > 0:
                    df_fin = pd.DataFrame(data["financial_transactions"])
                    if "الحالة" not in df_fin.columns: df_fin["الحالة"] = "معتمد"
                    str_lit.session_state.financial_transactions = df_fin
                else:
                    str_lit.session_state.financial_transactions = pd.DataFrame(columns=[
                        "التاريخ", "كود الموظف", "اسم الموظف", "الفرع", "النوع", "المبلغ / القيمة", "البيان / السبب", "الحالة"
                    ])

                if "users" in data and len(data["users"]) > 0:
                    df_users = pd.DataFrame(data["users"])
                    if "الحالة" not in df_users.columns: df_users["الحالة"] = "نشط"
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
                "صلاحية الموظف": "اعتماد الطلبات", "الراتب الأساسي": 5000, "مسوغات التعيين": "مكتملة", "ملف المستندات": "",
                "تاريخ بداية العقد": "2025-11-01", "تاريخ نهاية العقد": "2026-11-25",
                "رصيد سنوي (إجمالي)": 21, "رصيد أسبوعي (إجمالي)": 4, "رصيد رسمي (إجمالي)": 10, "إجازات مرضية (أيام)": 0
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
            "التاريخ", "كود الموظف", "اسم الموظف", "الفرع", "النوع", "المبلغ / القيمة", "البيان / السبب", "الحالة"
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

def render_printable_table(df, table_title="جدول البيانات"):
    if df.empty:
        str_lit.info("لا توجد بيانات متاحة للعرض في هذا السجل.")
        return
    
    str_lit.markdown(f"### 📊 {table_title}")
    
    with str_lit.expander("⚙️ خيارات تنسيق وفلترة الجدول (عرض/إخفاء الأعمدة)"):
        all_cols = df.columns.tolist()
        selected_cols = str_lit.multiselect(
            "اختر الأعمدة المراد إظهارها في الجدول:", 
            options=all_cols, 
            default=all_cols,
            key=f"ms_{uuid.uuid4()}"
        )
    
    if selected_cols:
        display_df = df[selected_cols]
    else:
        display_df = df
        
    info = str_lit.session_state.company_info
    c_name = info.get("name", "")
    c_cr = info.get("cr", "")
    c_tax = info.get("tax", "")
    c_lic = info.get("license", "")
    
    logged_user = str_lit.session_state.get('current_logged_user', 'غير محدد')
    user_role = str_lit.session_state.get('current_user_role', 'غير محدد')
    user_branch = str_lit.session_state.get('current_user_branch', 'غير محدد')
    
    try:
        styled_df = display_df.style.set_properties(**{
            'text-align': 'center !important',
            'vertical-align': 'middle !important',
            'white-space': 'nowrap !important'
        }).set_table_styles([
            {
                'selector': 'th', 
                'props': [
                    ('text-align', 'center !important'), 
                    ('background-color', '#0284C7'), 
                    ('color', 'white'),
                    ('vertical-align', 'middle !important'),
                    ('direction', 'rtl'),
                    ('padding', '8px')
                ]
            },
            {
                'selector': 'td', 
                'props': [
                    ('text-align', 'center !important'),
                    ('vertical-align', 'middle !important'),
                    ('direction', 'rtl'),
                    ('padding', '6px')
                ]
            }
        ])
        str_lit.dataframe(styled_df, use_container_width=True)
    except Exception:
        str_lit.dataframe(display_df, use_container_width=True)
    
    header_info_csv = f"# شركة: {c_name} | س.ت: {c_cr} | ب.ض: {c_tax} | ترخيص: {c_lic}\n"
    user_info_csv = f"# المسؤول: {logged_user} ({user_role}) | الفرع: {user_branch} | التاريخ: {datetime.now().strftime('%Y-%m-%d')}\n\n"
    
    csv_body = display_df.to_csv(index=False)
    full_csv_data = (header_info_csv + user_info_csv + csv_body).encode('utf-8-sig')
    
    unique_btn_key = f"dl_btn_{uuid.uuid4()}"
    str_lit.download_button(
        label="📥 تحميل هذا السجل المنسق كملف CSV",
        data=full_csv_data,
        file_name=f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv",
        key=unique_btn_key
    )

is_dark = str_lit.session_state.theme_mode == "Dark"

bg_color = "#F4F6F8" if not is_dark else "#121212"
text_color = "#111827" if not is_dark else "#F9FAFB"
card_bg = "#FFFFFF" if not is_dark else "#1E1E1E"
card_value_color = "#111827" if not is_dark else "#FFFFFF"
wrapper_bg = "#FFFFFF" if not is_dark else "#18181B"
input_bg = "#F9FAFB" if not is_dark else "#27272A"
input_text = "#111827" if not is_dark else "#FFFFFF"
input_border = "#D1D5DB" if not is_dark else "#3F3F46"
header_bg = "#FFFFFF" if not is_dark else "#18181B"
header_text = "#111827" if not is_dark else "#FFFFFF"

str_lit.markdown(f"""
    <style>
    header[data-testid="stHeader"] {{ visibility: hidden; height: 0px; }}
    
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
        border-bottom: 2px solid #00A3FF;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
    }}
    
    .main-content-spacer {{
        margin-top: 75px !important;
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
        border: 1px solid rgba(0, 163, 255, 0.2);
        color: {header_text} !important;
        padding: 0px !important;
        border-radius: 10px;
        width: 100%;
        margin-bottom: 3px;
        display: flex;
        align-items: stretch;
        overflow: hidden;
    }}
    
    .header-logo-box-full {{
        width: 65px;
        background: rgba(0, 163, 255, 0.1);
        border-left: 1px solid rgba(0, 163, 255, 0.2);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 22px;
        padding: 4px;
    }}
    
    .header-top-system h2 {{
        font-size: 10.5px !important;
        font-weight: bold !important;
        color: #00A3FF !important;
        margin: 0 0 1px 0 !important;
    }}
    .comp-name-txt {{
        font-size: 12.5px !important;
        font-weight: bold !important;
        color: {header_text} !important;
    }}
    .comp-info-txt {{
        font-size: 9px !important;
        color: #64748B !important;
        margin-top: 1px;
    }}
    
    .user-badge-box {{
        background: rgba(0, 163, 255, 0.1);
        border: 1px solid rgba(0, 163, 255, 0.3);
        padding: 2px 6px;
        border-radius: 6px;
        font-size: 10px;
        color: #0284C7;
        font-weight: bold;
        text-align: center;
        margin-bottom: 2px;
    }}
    
    .foodics-card {{
        background: {card_bg};
        border: 1px solid #E2E8F0;
        border-right: 5px solid #00A3FF;
        padding: 12px 16px;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.04);
        text-align: right !important;
        margin-bottom: 8px;
    }}
    .foodics-card-title {{
        font-size: 11.5px;
        color: #64748B;
        font-weight: bold;
        margin-bottom: 2px;
    }}
    .foodics-card-value {{
        font-size: 20px;
        color: {card_value_color};
        font-weight: bold;
    }}
    
    .section-header {{
        font-size: 15px !important;
        font-weight: bold !important;
        color: #0284C7 !important;
        border-bottom: 2px solid #00A3FF;
        padding-bottom: 6px;
        margin-top: 10px !important;
        margin-bottom: 10px !important;
        text-align: right !important;
    }}
    
    .entry-form-area {{
        background: {card_bg};
        padding: 18px;
        border-radius: 14px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.04);
        border: 1px solid #E2E8F0;
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
        logo_html = '<div class="header-logo-box-full">💼</div>'

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
                <div class="header-top-system"><h2>نظام الموارد البشرية المتكامل (ERP)</h2></div>
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
        <div style="max-width: 480px; margin: 10px auto 20px auto; background: {card_bg}; padding: 30px; border-radius: 16px; box-shadow: 0 10px 30px rgba(0,0,0,0.08); text-align: center; border: 1px solid #E2E8F0;">
            <h2 style="color: #0284C7; margin-bottom: 6px; font-size: 20px;">تسجيل الدخول - النظام المتكامل</h2>
            <p style="font-size: 14px; font-weight: bold; margin-bottom: 4px;">{lic_info.get('name', '')}</p>
            <p style="color: #64748B; font-size: 12px;">رقم الترخيص: {lic_info.get('license', '')}</p>
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
            if str_lit.form_submit_button("▶️ دخول النظام", use_container_width=True):
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

str_lit.markdown('</div>', unsafe_allow_html=True)
str_lit.markdown('<div class="main-content-spacer"></div>', unsafe_allow_html=True)

# -------------------------------------------------------------------------
# شبكة البطاقات الرئيسية (Dashboard Grid) بدلاً من الأزرار العلوية التقليدية
# -------------------------------------------------------------------------
str_lit.markdown("### 🎛️ لوحة التحكم الرئيسية (Dashboard Grid)")

r1_c1, r1_c2, r1_c3 = str_lit.columns(3)
with r1_c1:
    if str_lit.button("📊 لوحة التحكم والمؤشرات", use_container_width=True):
        str_lit.session_state.active_main_section = "الرئيسية"
        str_lit.session_state.active_sub_choice = "لوحة التحكم والمؤشرات"
        str_lit.rerun()
with r1_c2:
    if str_lit.button("⏱️ الحضور والانصراف", use_container_width=True):
        str_lit.session_state.active_main_section = "الحضور والانصراف"
        str_lit.session_state.active_sub_choice = "تسجيل حضور وانصراف"
        str_lit.rerun()
with r1_c3:
    if str_lit.button("👥 شؤون الموظفين والعقود", use_container_width=True):
        str_lit.session_state.active_main_section = "شؤون الموظفين"
        str_lit.session_state.active_sub_choice = "سجل الموظفين والأرصدة الشاملة"
        str_lit.rerun()

r2_c1, r2_c2, r2_c3 = str_lit.columns(3)
with r2_c1:
    if str_lit.button("📝 طلبات الإجازات", use_container_width=True):
        str_lit.session_state.active_main_section = "طلبات الاجازة"
        str_lit.session_state.active_sub_choice = "تسجيل طلب إجازة"
        str_lit.rerun()
with r2_c2:
    if str_lit.button("💵 المعاملات المالية والسلف", use_container_width=True):
        str_lit.session_state.active_main_section = "المعاملات المالية"
        str_lit.session_state.active_sub_choice = "تسجيل معاملة مالية"
        str_lit.rerun()
with r2_c3:
    if str_lit.button("💰 كشف الرواتب", use_container_width=True):
        str_lit.session_state.active_main_section = "كشف الرواتب"
        str_lit.session_state.active_sub_choice = "كشف الرواتب والمستحقات الشامل"
        str_lit.rerun()

r3_c1, r3_c2, r3_c3 = str_lit.columns(3)
with r3_c1:
    if str_lit.button("🛡️ إدارة المستخدمين", use_container_width=True):
        str_lit.session_state.active_main_section = "المستخدمين"
        str_lit.session_state.active_sub_choice = "إدارة المستخدمين والصلاحيات والسجل"
        str_lit.rerun()
with r3_c2:
    if str_lit.button("🖨️ التقارير العامة", use_container_width=True):
        str_lit.session_state.active_main_section = "التقارير"
        str_lit.session_state.active_sub_choice = "طباعة التقارير العامة"
        str_lit.rerun()
with r3_c3:
    if str_lit.button("⚙️ إعدادات وبرمجة النظام", use_container_width=True):
        str_lit.session_state.active_main_section = "اعدادات الشركة"
        str_lit.session_state.active_sub_choice = "إعدادات الشركة وبياناتها الشاملة"
        str_lit.rerun()

str_lit.markdown("<hr style='border: 0.5px solid #E2E8F0; margin: 15px 0;'>", unsafe_allow_html=True)

# تحديد القسم والعملية الفرعية بناءً على التفاعل
selected_main_cat = str_lit.session_state.get("active_main_section", "الرئيسية")

sub_options_map = {
    "الرئيسية": ["لوحة التحكم والمؤشرات"],
    "الحضور والانصراف": ["تسجيل حضور وانصراف", "سجل الحضور والانصراف", "تعديل أو حذف حركة حضور"],
    "طلبات الاجازة": ["تسجيل طلب إجازة", "سجل طلبات قيد الانتظار", "سجل الطلبات المقبولة", "سجل الطلبات المرفوضة", "إدارة واعتماد طلبات الإجازة"],
    "المعاملات المالية": ["تسجيل معاملة مالية", "تسجيل إذن (انصراف / تأخير)", "سجل المعاملات المالية والأذونات", "إدارة واعتماد المعاملات والأذونات"],
    "كشف الرواتب": ["كشف الرواتب والمستحقات الشامل"],
    "شؤون الموظفين": ["إضافة موظف جديد", "سجل الموظفين والأرصدة الشاملة", "تعديل أو حذف موظف", "رفع نموذج بيانات الموظفين"],
    "المستخدمين": ["إضافة مستخدم جديد", "إدارة المستخدمين والصلاحيات والسجل", "تعديل أو حذف مستخدم"],
    "التقارير": ["طباعة التقارير العامة"],
    "اعدادات الشركة": ["إعدادات الشركة وبياناتها الشاملة"],
    "أدوات النظام": ["تحميل النماذج (Templates)", "نسخة احتياطية واستعادة", "مسح البيانات"]
}

sub_options_list = sub_options_map.get(selected_main_cat, ["لوحة التحكم والمؤشرات"])
default_sub_choice = str_lit.session_state.get("active_sub_choice", sub_options_list[0])
if default_sub_choice not in sub_options_list:
    default_sub_choice = sub_options_list[0]

col_sub_sel, col_exit_btn = str_lit.columns([4, 1])
with col_sub_sel:
    choice = str_lit.selectbox(f"📑 العمليات الفرعية للقسم الحالي:", sub_options_list, index=sub_options_list.index(default_sub_choice))
with col_exit_btn:
    str_lit.write("")
    if str_lit.button("⏹️ خروج النظام", use_container_width=True):
        str_lit.session_state.is_authenticated = False
        str_lit.session_state.current_logged_user = ""
        str_lit.rerun()

str_lit.markdown("<hr style='border: 0.5px dashed #E2E8F0; margin: 10px 0;'>", unsafe_allow_html=True)

# -------------------------------------------------------------------------
# زر تصفية البيانات المتقدمة (Popover Filter Button)
# -------------------------------------------------------------------------
col_filter_btn, col_filter_info = str_lit.columns([1, 4])
selected_sidebar_branch = "الكل"
selected_sidebar_status = "الكل"
sidebar_search_text = ""
enable_date_filter = False
filter_start_date = date.today() - timedelta(days=30)
filter_end_date = date.today()

with col_filter_btn:
    with str_lit.popover("⚙️ تصفية البيانات المتقدمة"):
        str_lit.markdown("### 🍔 خيارات الفلتر")
        available_branches = ["الكل", "المركز الرئيسي", "فرع الإسكندرية", "فرع الشرم"]
        selected_sidebar_branch = str_lit.selectbox("📍 فرع المنشأة", available_branches, key="pop_branch")
        
        selected_sidebar_status = str_lit.selectbox("📌 حالة السجلات", ["الكل", "مقبول / معتمد", "قيد الانتظار", "مرفوض"], key="pop_status")
        
        sidebar_search_text = str_lit.text_input("🔍 بحث فوري بالاسم / الكود", placeholder="اكتب للفلترة...", key="pop_search")
        
        str_lit.markdown("---")
        enable_date_filter = str_lit.checkbox("تفعيل فلتر التاريخ", key="pop_chk_date")
        if enable_date_filter:
            filter_start_date = str_lit.date_input("من تاريخ", value=date.today() - timedelta(days=30), key="pop_sdate")
            filter_end_date = str_lit.date_input("إلى تاريخ", value=date.today(), key="pop_edate")
        
        if str_lit.button("🔄 إعادة ضبط الفلاتر", use_container_width=True, key="pop_reset"):
            str_lit.rerun()

def apply_foodics_filter(df, date_col_name=None):
    if df.empty:
        return df
    filtered_df = df.copy()
    
    if selected_sidebar_branch != "الكل" and "الفرع" in filtered_df.columns:
        filtered_df = filtered_df[filtered_df["الفرع"] == selected_sidebar_branch]
        
    if selected_sidebar_status != "الكل" and "الحالة" in filtered_df.columns:
        if selected_sidebar_status == "مقبول / معتمد":
            filtered_df = filtered_df[filtered_df["الحالة"].isin(["مقبول", "معتمد"])]
        else:
            filtered_df = filtered_df[filtered_df["الحالة"] == selected_sidebar_status]
            
    if sidebar_search_text.strip() != "":
        mask = False
        for col in ["اسم الموظف", "كود الموظف", "رقم الطلب", "البيان / السبب"]:
            if col in filtered_df.columns:
                mask = mask | filtered_df[col].astype(str).str.contains(sidebar_search_text, case=False, na=False)
        filtered_df = filtered_df[mask]
        
    if enable_date_filter and date_col_name and date_col_name in filtered_df.columns:
        try:
            filtered_df[date_col_name] = pd.to_datetime(filtered_df[date_col_name]).dt.date
            filtered_df = filtered_df[
                (filtered_df[date_col_name] >= filter_start_date) & 
                (filtered_df[date_col_name] <= filter_end_date)
            ]
        except Exception:
            pass
            
    return filtered_df

filtered_employees = apply_foodics_filter(str_lit.session_state.employees, "تاريخ بداية العقد")
filtered_requests = apply_foodics_filter(str_lit.session_state.requests, "من تاريخ")
filtered_attendance = apply_foodics_filter(str_lit.session_state.attendance, "التاريخ")
filtered_fin = apply_foodics_filter(str_lit.session_state.financial_transactions, "التاريخ")

total_emps = len(filtered_employees)
pending_requests = filtered_requests[filtered_requests['الحالة'] == 'قيد الانتظار'] if not filtered_requests.empty else pd.DataFrame()
pending_count = len(pending_requests)
accepted_count = len(filtered_requests[filtered_requests['الحالة'] == 'مقبول']) if not filtered_requests.empty else 0

# -------------------------------------------------------------------------
# بطاقات الـ KPI الإحصائية السفلية
# -------------------------------------------------------------------------
col1, col2, col3, col4 = str_lit.columns(4)
with col1:
    str_lit.markdown(f'<div class="foodics-card"><div class="foodics-card-title">👥 الموظفون (حسب الفلتر)</div><div class="foodics-card-value">{total_emps}</div></div>', unsafe_allow_html=True)
with col2:
    str_lit.markdown(f'<div class="foodics-card" style="border-right-color: #F59E0B;"><div class="foodics-card-title">⏳ طلبات قيد الانتظار</div><div class="foodics-card-value" style="color: #F59E0B;">{pending_count}</div></div>', unsafe_allow_html=True)
with col3:
    str_lit.markdown(f'<div class="foodics-card" style="border-right-color: #10B981;"><div class="foodics-card-title">✅ الطلبات المقبولة</div><div class="foodics-card-value" style="color: #10B981;">{accepted_count}</div></div>', unsafe_allow_html=True)
with col4:
    active_users_count = len(str_lit.session_state.users[str_lit.session_state.users["الحالة"] == "نشط"]) if not str_lit.session_state.users.empty else 0
    str_lit.markdown(f'<div class="foodics-card" style="border-right-color: #0284C7;"><div class="foodics-card-title">🛡️ المستخدمين النشطين</div><div class="foodics-card-value" style="font-size: 18px; color: #0284C7;">{active_users_count} مستخدم</div></div>', unsafe_allow_html=True)

str_lit.markdown("<hr style='border: 0.5px solid #E2E8F0; margin: 8px 0 12px 0;'>", unsafe_allow_html=True)

# عرض المحتوى حسب القسم المختار
if selected_main_cat == "الرئيسية" and choice == "لوحة التحكم والمؤشرات":
    str_lit.markdown(f'<div class="section-header">🔔 التنبيهات والإنذارات المبكرة لعقود الموظفين</div>', unsafe_allow_html=True)
    today = datetime.now()
    warning_flag = False

    if not filtered_employees.empty:
        for idx, emp_row in filtered_employees.iterrows():
            emp_name = emp_row.get("اسم الموظف", "غير معروف")
            end_contract_str = emp_row.get("تاريخ نهاية العقد", "")
            if end_contract_str:
                try:
                    exp_date = datetime.strptime(str(end_contract_str).strip(), "%Y-%m-%d")
                    days_remaining = (exp_date - today).days

                    if 0 <= days_remaining <= 30:
                        warning_flag = True
                        str_lit.warning(f"⚠️ **تنبيه انتهاء عقد:** عقد الموظف (**{emp_name}**) متبقي على انتهائه **{days_remaining} يوم فقط** (تاريخ الانتهاء: {end_contract_str}).", icon="🚨")
                    elif days_remaining < 0:
                        warning_flag = True
                        str_lit.error(f"❌ **تجاوز موعد العقد:** عقد الموظف (**{emp_name}**) انتهى منذ {-days_remaining} يوم!", icon="🚫")
                except Exception:
                    pass

    if not warning_flag:
        str_lit.success("✅ جميع العقود والمستندات ضمن نطاق الفلتر سارية ولا توجد تحذيرات قريبة.")
    
    str_lit.markdown("<hr style='border: 0.5px dashed #E2E8F0; margin: 10px 0;'>", unsafe_allow_html=True)
    str_lit.markdown(f'<div class="section-header">📊 داشبورد ومخطط بياني ومؤشرات (حسب الفلتر النشط)</div>', unsafe_allow_html=True)
    all_branches = filtered_employees["الفرع"].unique().tolist() if not filtered_employees.empty else ["المركز الرئيسي"]
    
    for branch in all_branches:
        str_lit.markdown(f"### 📍 فرع: {branch}")
        branch_emps = filtered_employees[filtered_employees["الفرع"] == branch]
        b_count = len(branch_emps)
        b_sal_total = float(branch_emps["الراتب الأساسي"].sum()) if (not branch_emps.empty and "الراتب الأساسي" in branch_emps.columns) else 0.0
        b_att = filtered_attendance[filtered_attendance["الفرع"] == branch] if not filtered_attendance.empty else pd.DataFrame()
        b_att_count = len(b_att)
        
        bc1, bc2, bc3 = str_lit.columns(3)
        with bc1:
            str_lit.markdown(f'<div class="foodics-card"><div class="foodics-card-title">👥 عدد الموظفين بالفرع</div><div class="foodics-card-value">{b_count}</div></div>', unsafe_allow_html=True)
        with bc2:
            str_lit.markdown(f'<div class="foodics-card" style="border-right-color: #0284C7;"><div class="foodics-card-title">💰 إجمالي رواتب الفرع</div><div class="foodics-card-value" style="font-size: 18px; color: #0284C7;">{b_sal_total:,.0f} ج.م</div></div>', unsafe_allow_html=True)
        with bc3:
            str_lit.markdown(f'<div class="foodics-card" style="border-right-color: #10B981;"><div class="foodics-card-title">⏱️ حركات الحضور المسجلة</div><div class="foodics-card-value" style="color: #10B981;">{b_att_count}</div></div>', unsafe_allow_html=True)
        
        if not branch_emps.empty:
            str_lit.markdown(f"**📈 مخطط الرواتب حسب الوظيفة في فرع ({branch}):**")
            chart_data = branch_emps.set_index("الوظيفة")["الراتب الأساسي"]
            str_lit.bar_chart(chart_data)
            
            str_lit.markdown(f"**📋 جدول موظفي فرع ({branch}):**")
            default_cols = ["كود الموظف", "اسم الموظف", "الوظيفة", "القسم", "الراتب الأساسي", "مسوغات التعيين", "تاريخ بداية العقد", "تاريخ نهاية العقد"]
            available_cols = [col for col in default_cols if col in branch_emps.columns]
            render_printable_table(branch_emps[available_cols], f"موظفي فرع {branch}")
        str_lit.markdown("<hr style='border: 0.5px dashed #E2E8F0; margin: 10px 0;'>", unsafe_allow_html=True)

elif choice == "تسجيل حضور وانصراف":
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
            col_in1, col_in2, col_in3 = str_lit.columns(3)
            with col_in1: act_in_h = str_lit.selectbox("ساعة الحضور الفعلي", list(range(1, 13)), index=7, key="ain_h")
            with col_in2: act_in_m = str_lit.selectbox("دقيقة الحضور (00-59)", list(range(0, 60)), index=0, key="ain_m")
            with col_in3: act_in_ampm = str_lit.selectbox("فترة الحضور", ["AM", "PM"], index=0, key="ain_ap")

            col_out1, col_out2, col_out3 = str_lit.columns(3)
            with col_out1: act_out_h = str_lit.selectbox("ساعة الانصراف الفعلي", list(range(1, 13)), index=3, key="aout_h")
            with col_out2: act_out_m = str_lit.selectbox("دقيقة الانصراف (00-59)", list(range(0, 60)), index=0, key="aout_m")
            with col_out3: act_out_ampm = str_lit.selectbox("فترة الانصراف", ["AM", "PM"], index=1, key="aout_ap")

            att_status = str_lit.selectbox("حالة الحضور", ["حضور منتظم", "إجازة أسبوعية", "إجازة سنوية", "إجازة مرضية", "إجازة بدون أجر", "غياب"])
            
            if str_lit.form_submit_button("💾 حفظ حركة الحضور والانصراف", use_container_width=True):
                new_att_row = {
                    "التاريخ": att_date.strftime("%Y-%m-%d"),
                    "كود الموظف": emp_info["كود الموظف"],
                    "اسم الموظف": selected_emp,
                    "الوظيفة": c_job,
                    "الفرع": c_branch,
                    "بداية العمل الرسمية": "08:00 AM",
                    "نهاية العمل الرسمية": "04:00 PM",
                    "وقت الحضور الفعلي": f"{act_in_h:02d}:{act_in_m:02d} {act_in_ampm}",
                    "وقت الانصراف الفعلي": f"{act_out_h:02d}:{act_out_m:02d} {act_out_ampm}",
                    "فترة السماح (دقيقة)": 15,
                    "الحالة": att_status,
                    "التأخير (دقيقة)": 0,
                    "إضافي (دقيقة)": 0
                }
                str_lit.session_state.attendance = pd.concat([str_lit.session_state.attendance, pd.DataFrame([new_att_row])], ignore_index=True)
                auto_save_data()
                str_lit.success("✅ تم تسجيل وحفظ حركة الحضور والانصراف بنجاح!")
        str_lit.markdown('</div>', unsafe_allow_html=True)

elif choice == "سجل الحضور والانصراف":
    render_printable_table(filtered_attendance, "سجل الحضور والانصراف المفلتر")

elif choice == "تسجيل طلب إجازة":
    str_lit.subheader("📝 تسجيل طلب إجازة جديد للموظف")
    emp_names = str_lit.session_state.employees["اسم الموظف"].tolist()
    if emp_names:
        str_lit.markdown('<div class="entry-form-area">', unsafe_allow_html=True)
        with str_lit.form("request_vacation_form_full"):
            req_emp_name = str_lit.selectbox("اختر الموظف", emp_names)
            emp_rec = str_lit.session_state.employees[str_lit.session_state.employees["اسم الموظف"] == req_emp_name].iloc[0]
            req_type = str_lit.selectbox("نوع الإجازة", ["إجازة سنوية", "إجازة أسبوعية", "إجازة رسمية", "إجازة مرضية", "إجازة بدون أجر"])
            col_d1, col_d2 = str_lit.columns(2)
            with col_d1: req_start_date = str_lit.date_input("من تاريخ", value=date.today())
            with col_d2: req_end_date = str_lit.date_input("إلى تاريخ", value=date.today() + timedelta(days=1))
            req_reason = str_lit.text_input("سبب طلب الإجازة")
            
            if str_lit.form_submit_button("💾 تقديم طلب الإجازة", use_container_width=True):
                delta_days = (req_end_date - req_start_date).days + 1
                new_req_row = {
                    "رقم الطلب": f"REQ-{len(str_lit.session_state.requests)+1:03d}",
                    "كود الموظف": emp_rec["كود الموظف"],
                    "اسم الموظف": req_emp_name,
                    "الوظيفة": emp_rec["الوظيفة"],
                    "الفرع": emp_rec["الفرع"],
                    "نوع الإجازة": req_type,
                    "من تاريخ": req_start_date.strftime("%Y-%m-%d"),
                    "إلى تاريخ": req_end_date.strftime("%Y-%m-%d"),
                    "عدد الأيام": int(delta_days),
                    "السبب": req_reason,
                    "الحالة": "قيد الانتظار"
                }
                str_lit.session_state.requests = pd.concat([str_lit.session_state.requests, pd.DataFrame([new_req_row])], ignore_index=True)
                auto_save_data()
                str_lit.success("✅ تم تقديم طلب الإجازة بنجاح وهو قيد الانتظار للإعتماد!")
        str_lit.markdown('</div>', unsafe_allow_html=True)

elif choice == "سجل طلبات قيد الانتظار":
    render_printable_table(filtered_requests[filtered_requests["الحالة"] == "قيد الانتظار"], "طلبات الإجازة قيد الانتظار")

elif choice == "سجل الطلبات المقبولة":
    render_printable_table(filtered_requests[filtered_requests["الحالة"] == "مقبول"], "طلبات الإجازة المقبولة")

elif choice == "تسجيل معاملة مالية":
    str_lit.subheader("💵 تسجيل معاملة مالية (سلفة، حافز، أو خصم)")
    emp_names = str_lit.session_state.employees["اسم الموظف"].tolist()
    if emp_names:
        str_lit.markdown('<div class="entry-form-area">', unsafe_allow_html=True)
        with str_lit.form("fin_trans_form_full"):
            f_emp = str_lit.selectbox("اختر الموظف", emp_names)
            f_emp_rec = str_lit.session_state.employees[str_lit.session_state.employees["اسم الموظف"] == f_emp].iloc[0]
            f_type = str_lit.selectbox("نوع المعاملة", ["سلفة", "حافز / مكافأة", "خصم غياب أو جزاء"])
            f_amount = str_lit.number_input("المبلغ / القيمة (ج.م)", min_value=0.0, value=500.0, step=50.0)
            f_reason = str_lit.text_input("البيان أو السبب بالتفصيل")
            f_date = str_lit.date_input("تاريخ المعاملة", value=date.today())

            if str_lit.form_submit_button("💾 حفظ المعاملة المالية", use_container_width=True):
                new_fin_row = {
                    "التاريخ": f_date.strftime("%Y-%m-%d"),
                    "كود الموظف": f_emp_rec["كود الموظف"],
                    "اسم الموظف": f_emp,
                    "الفرع": f_emp_rec["الفرع"],
                    "النوع": f_type,
                    "المبلغ / القيمة": float(f_amount),
                    "البيان / السبب": f_reason,
                    "الحالة": "قيد الانتظار"
                }
                str_lit.session_state.financial_transactions = pd.concat([str_lit.session_state.financial_transactions, pd.DataFrame([new_fin_row])], ignore_index=True)
                auto_save_data()
                str_lit.success("✅ تم تسجيل المعاملة المالية بنجاح!")
        str_lit.markdown('</div>', unsafe_allow_html=True)

elif choice == "سجل المعاملات المالية والأذونات":
    render_printable_table(filtered_fin, "سجل المعاملات المالية والأذونات")

elif choice == "إضافة موظف جديد":
    str_lit.subheader("➕ إضافة موظف جديد، مسوغات التعيين وتحديد العقود")
    str_lit.markdown('<div class="entry-form-area">', unsafe_allow_html=True)
    with str_lit.form("new_emp_form_full"):
        emp_code_in = str_lit.text_input("كود الموظف", value=f"EMP{len(str_lit.session_state.employees)+1:03d}")
        emp_name_in = str_lit.text_input("اسم الموظف الرباعي")
        emp_job_in = str_lit.text_input("الوظيفة / المسمى الوظيفي")
        emp_branch_in = str_lit.selectbox("الفرع التابع", ["المركز الرئيسي", "فرع الإسكندرية", "فرع الشرم"])
        emp_salary_in = str_lit.number_input("الراتب الأساسي (ج.م)", min_value=0.0, value=5000.0, step=100.0)
        
        if str_lit.form_submit_button("💾 حفظ بيانات الموظف", use_container_width=True):
            new_emp_data = {
                "كود الموظف": emp_code_in,
                "اسم الموظف": emp_name_in,
                "الوظيفة": emp_job_in,
                "القسم": "الإدارة",
                "الفرع": emp_branch_in,
                "صلاحية الموظف": "مستخدم عادي",
                "الراتب الأساسي": float(emp_salary_in),
                "مسوغات التعيين": "مكتملة",
                "ملف المستندات": "",
                "تاريخ بداية العقد": str(date.today()),
                "تاريخ نهاية العقد": str(date.today() + timedelta(days=365)),
                "رصيد سنوي (إجمالي)": 21,
                "رصيد أسبوعي (إجمالي)": 4,
                "رصيد رسمي (إجمالي)": 10,
                "إجازات مرضية (أيام)": 0
            }
            str_lit.session_state.employees = pd.concat([str_lit.session_state.employees, pd.DataFrame([new_emp_data])], ignore_index=True)
            auto_save_data()
            str_lit.success(f"✅ تم إضافة الموظف ({emp_name_in}) بنجاح تام!")
    str_lit.markdown('</div>', unsafe_allow_html=True)

elif choice == "سجل الموظفين والأرصدة الشاملة":
    render_printable_table(filtered_employees, "سجل الموظفين الشامل")

elif choice == "كشف الرواتب والمستحقات الشامل":
    if not filtered_employees.empty:
        df_sal = filtered_employees[["كود الموظف", "اسم الموظف", "الوظيفة", "القسم", "الفرع", "الراتب الأساسي"]].copy()
        df_sal["الصافي المستحق"] = df_sal["الراتب الأساسي"]
        render_printable_table(df_sal, "كشف الرواتب والمستحقات")

elif choice == "إدارة المستخدمين والصلاحيات والسجل":
    render_printable_table(str_lit.session_state.users, "سجل مستخدمي النظام")

elif choice == "طباعة التقارير العامة":
    render_printable_table(filtered_employees, "التقرير الشامل للموظفين")

elif choice == "إعدادات الشركة وبياناتها الشاملة":
    str_lit.subheader("⚙️ إعدادات وبيانات الشركة الرسمية")
    info = str_lit.session_state.company_info
    str_lit.markdown('<div class="entry-form-area">', unsafe_allow_html=True)
    with str_lit.form("company_settings_form_full"):
        c_name_in = str_lit.text_input("اسم الشركة الرسمي", value=info.get("name", ""))
        c_lic_in = str_lit.text_input("رقم الترخيص الرسمي", value=info.get("license", ""))
        if str_lit.form_submit_button("💾 حفظ تحديثات إعدادات الشركة", use_container_width=True):
            str_lit.session_state.company_info["name"] = c_name_in
            str_lit.session_state.company_info["license"] = c_lic_in
            auto_save_data()
            str_lit.success("✅ تم تحديث وحفظ إعدادات الشركة بنجاح!")
    str_lit.markdown('</div>', unsafe_allow_html=True)

else:
    str_lit.info(f"القسم الحالي ({choice}) جاهز للتشغيل والعمليات التنفيذية.")

str_lit.markdown("<hr style='border: 0.5px solid #E2E8F0; margin: 20px 0;'>", unsafe_allow_html=True)
str_lit.markdown("<p style='text-align: center; color: #64748B; font-size: 11px;'>جميع الحقوق محفوظة © النظام المتكامل لإدارة الموارد البشرية (ERP)</p>", unsafe_allow_html=True)