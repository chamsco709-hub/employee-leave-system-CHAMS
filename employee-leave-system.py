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
                    if "حالة الموظف" not in df_emp.columns: df_emp["حالة الموظف"] = "نشط"
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
                        "كود الموظف", "اسم الموظف", "الوظيفة", "القسم", "الفرع", "صلاحية الموظف", "حالة الموظف",
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
                "صلاحية الموظف": "اعتماد الطلبات", "حالة الموظف": "نشط", "الراتب الأساسي": 5000, "مسوغات التعيين": "مكتملة", "ملف المستندات": "",
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
    
    with str_lit.expander("⚙️ خيارات عرض الأعمدة"):
        all_cols = df.columns.tolist()
        selected_cols = str_lit.multiselect(
            "اختر الأعمدة المراد إظهارها في الجدول:", 
            options=all_cols, 
            default=all_cols,
            key=f"ms_{uuid.uuid4()}"
        )
    
    display_df = df[selected_cols] if selected_cols else df
        
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
        label="📥 تحميل السجل المنسق (CSV)",
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
sub_card_bg = "#F8FAFC" if not is_dark else "#27272A"

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
        padding: 4px 15px 4px 15px !important;
        border-bottom: 2px solid #00A3FF;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
    }}
    
    .main-content-spacer {{
        margin-top: 1px !important;
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
    
    .stButton > button {{
        border-radius: 12px !important;
        font-weight: bold !important;
        padding: 10px 14px !important;
        border: 1px solid #E2E8F0 !important;
        background-color: {card_bg} !important;
        color: {text_color} !important;
        box-shadow: 0 3px 10px rgba(0, 0, 0, 0.04) !important;
        transition: all 0.2s ease !important;
    }}
    .stButton > button:hover {{
        border-color: #00A3FF !important;
        box-shadow: 0 6px 15px rgba(0, 163, 255, 0.15) !important;
        transform: translateY(-1px);
    }}
    
    .glass-header {{
        background: {header_bg};
        border: 1px solid rgba(0, 163, 255, 0.2);
        color: {header_text} !important;
        padding: 0px !important;
        border-radius: 10px;
        width: 100%;
        margin-bottom: 4px;
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
        padding: 6px 10px;
        border-radius: 8px;
        font-size: 11px;
        color: #0284C7;
        font-weight: bold;
        text-align: center;
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
    
    .sub-grid-container {{
        background: {sub_card_bg};
        padding: 12px;
        border-radius: 12px;
        border: 1px dashed #CBD5E1;
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
if 'active_sub_choice' not in str_lit.session_state: str_lit.session_state.active_sub_choice = "الرئيسية"

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
    
    col_t_l1, col_t_l2, col_t_l3 = str_lit.columns([4, 1, 4])
    with col_t_l2:
        theme_icon = "🌙" if str_lit.session_state.theme_mode == "Light" else "☀️"
        if str_lit.button(theme_icon, key="login_theme_toggle", use_container_width=True, help="تبديل مظهر الشاشة"):
            str_lit.session_state.theme_mode = "Dark" if str_lit.session_state.theme_mode == "Light" else "Light"
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

col_ub1, col_ub2, col_ub3 = str_lit.columns([6, 0.8, 1.2])
with col_ub1:
    logged_username = str_lit.session_state.current_logged_user
    user_role = str_lit.session_state.current_user_role
    user_branch = str_lit.session_state.current_user_branch
    user_dept = str_lit.session_state.current_user_dept

    str_lit.markdown(
        f"""
        <div class="user-badge-box">
            👤 المستخدم: <b>{logged_username}</b> &nbsp;|&nbsp; 🛡️ الصلاحية: <b>{user_role}</b> &nbsp;|&nbsp; 📍 الفرع: <b>{user_branch}</b> &nbsp;|&nbsp; 🏢 القسم: <b>{user_dept}</b>
        </div>
        """,
        unsafe_allow_html=True
    )

with col_ub2:
    theme_icon_main = "🌙" if str_lit.session_state.theme_mode == "Light" else "☀️"
    if str_lit.button(theme_icon_main, key="theme_icon_btn", use_container_width=True, help="تغيير المظهر (ليلي / نهاري)"):
        str_lit.session_state.theme_mode = "Dark" if str_lit.session_state.theme_mode == "Light" else "Light"
        str_lit.rerun()

with col_ub3:
    if str_lit.button("⏹️ خروج", key="top_logout_btn", use_container_width=True):
        str_lit.session_state.is_authenticated = False
        str_lit.session_state.current_logged_user = ""
        str_lit.rerun()

str_lit.markdown('</div>', unsafe_allow_html=True)
str_lit.markdown('<div class="main-content-spacer"></div>', unsafe_allow_html=True)

# أزرار التحكم الرئيسية (Dashboard Grid)
r1_c1, r1_c2, r1_c3 = str_lit.columns(3)
with r1_c1:
    if str_lit.button("🏠  الرئيسية", use_container_width=True):
        str_lit.session_state.active_main_section = "الرئيسية"
        str_lit.session_state.active_sub_choice = " الرئيسية"
        str_lit.rerun()
with r1_c2:
    if str_lit.button("📈  المؤشرات والتحليلات", use_container_width=True):
        str_lit.session_state.active_main_section = "المؤشرات والتحليلات"
        str_lit.session_state.active_sub_choice = " المؤشرات والتحليلات"
        str_lit.rerun()
with r1_c3:
    if str_lit.button("⏱️ الحضور والانصراف", use_container_width=True):
        str_lit.session_state.active_main_section = "الحضور والانصراف"
        str_lit.session_state.active_sub_choice = "تسجيل حضور وانصراف"
        str_lit.rerun()

r2_c1, r2_c2, r2_c3 = str_lit.columns(3)
with r2_c1:
    if str_lit.button("👥 شؤون الموظفين والعقود", use_container_width=True):
        str_lit.session_state.active_main_section = "شؤون الموظفين"
        str_lit.session_state.active_sub_choice = "سجل الموظفين النشطين والشامل"
        str_lit.rerun()
with r2_c2:
    if str_lit.button("📝 طلبات الإجازات (تعديل وحذف)", use_container_width=True):
        str_lit.session_state.active_main_section = "طلبات الاجازة"
        str_lit.session_state.active_sub_choice = "تعديل أو حذف طلب إجازة"
        str_lit.rerun()
with r2_c3:
    if str_lit.button("💵 المعاملات المالية والسلف", use_container_width=True):
        str_lit.session_state.active_main_section = "المعاملات المالية"
        str_lit.session_state.active_sub_choice = "تسجيل معاملة مالية"
        str_lit.rerun()

r3_c1, r3_c2, r3_c3 = str_lit.columns(3)
with r3_c1:
    if str_lit.button("💰 كشف الرواتب", use_container_width=True):
        str_lit.session_state.active_main_section = "كشف الرواتب"
        str_lit.session_state.active_sub_choice = "كشف الرواتب والمستحقات الشامل"
        str_lit.rerun()
with r3_c2:
    if str_lit.button("🛡️ إدارة المستخدمين", use_container_width=True):
        str_lit.session_state.active_main_section = "المستخدمين"
        str_lit.session_state.active_sub_choice = "إدارة المستخدمين والصلاحيات والسجل"
        str_lit.rerun()
with r3_c3:
    if str_lit.button("⚙️ إعدادات وأدوات النظام", use_container_width=True):
        str_lit.session_state.active_main_section = "اعدادات الشركة"
        str_lit.session_state.active_sub_choice = "إعدادات الشركة وبياناتها الشاملة"
        str_lit.rerun()

str_lit.markdown("<hr style='border: 0.5px solid #E2E8F0; margin: 12px 0;'>", unsafe_allow_html=True)

selected_main_cat = str_lit.session_state.get("active_main_section", "الرئيسية")

sub_options_map = {
    "الرئيسية": [
        ("🏠  الرئيسية", " الرئيسية")
    ],
    "المؤشرات والتحليلات": [
        ("📈  المؤشرات والتحليلات", " المؤشرات والتحليلات")
    ],
    "الحضور والانصراف": [
        ("➕ تسجيل حضور وانصراف", "تسجيل حضور وانصراف"),
        ("📋 سجل الحضور والانصراف", "سجل الحضور والانصراف"),
        ("✏️ تعديل أو حذف حركة", "تعديل أو حذف حركة حضور")
    ],
    "طلبات الاجازة": [
        ("➕ تسجيل طلب إجازة", "تسجيل طلب إجازة"),
        ("⏳ طلبات قيد الانتظار", "سجل طلبات قيد الانتظار"),
        ("✅ الطلبات المقبولة", "سجل الطلبات المقبولة"),
        ("❌ الطلبات المرفوضة", "سجل الطلبات المرفوضة"),
        ("✏️ تعديل أو حذف طلب إجازة", "تعديل أو حذف طلب إجازة")
    ],
    "المعاملات المالية": [
        ("💵 تسجيل معاملة مالية", "تسجيل معاملة مالية"),
        ("⏱️ تسجيل إذن (انصراف/تأخير)", "تسجيل إذن (انصراف / تأخير)"),
        ("📋 سجل المعاملات والأذونات", "سجل المعاملات المالية والأذونات"),
        ("⚖️ اعتماد المعاملات والأذونات", "إدارة واعتماد المعاملات والأذونات")
    ],
    "كشف الرواتب": [
        ("💰 كشف الرواتب والمستحقات", "كشف الرواتب والمستحقات الشامل")
    ],
    "شؤون الموظفين": [
        ("➕ إضافة موظف جديد", "إضافة موظف جديد"),
        ("👥 سجل الموظفين النشطين", "سجل الموظفين النشطين والشامل"),
        ("🚪 سجل المستقيلين والموقوفين", "سجل الموظفين المستقيلين والموقوفين"),
        ("✏️ تعديل أو حذف موظف", "تعديل أو حذف موظف"),
        ("📤 رفع ملف موظفين (CSV)", "رفع نموذج بيانات الموظفين")
    ],
    "المستخدمين": [
        ("➕ إضافة مستخدم جديد", "إضافة مستخدم جديد"),
        ("🛡️ سجل المستخدمين والصلاحيات", "إدارة المستخدمين والصلاحيات والسجل"),
        ("✏️ تعديل أو حذف مستخدم", "تعديل أو حذف مستخدم")
    ],
    "التقارير": [
        ("🖨️ طباعة التقارير العامة", "طباعة التقارير العامة")
    ],
    "اعدادات الشركة": [
        ("🏢 إعدادات وبيانات الشركة", "إعدادات الشركة وبياناتها الشاملة"),
        ("📥 تحميل النماذج الجاهزة", "تحميل النماذج (Templates)"),
        ("💾 نسخة احتياطية واستعادة", "نسخة احتياطية واستعادة"),
        ("⚠️ مسح وتصفير البيانات", "مسح البيانات")
    ]
}

current_sub_cards = sub_options_map.get(selected_main_cat, [("🏠  الرئيسية", " الرئيسية")])

if len(current_sub_cards) > 1:
    str_lit.markdown('<div class="sub-grid-container">', unsafe_allow_html=True)
    cols_per_row = min(len(current_sub_cards), 3)
    for i in range(0, len(current_sub_cards), cols_per_row):
        row_items = current_sub_cards[i:i + cols_per_row]
        sub_cols = str_lit.columns(len(row_items))
        for j, (card_label, card_val) in enumerate(row_items):
            with sub_cols[j]:
                if str_lit.button(card_label, key=f"sub_card_{selected_main_cat}_{i}_{j}", use_container_width=True):
                    str_lit.session_state.active_sub_choice = card_val
                    str_lit.rerun()
    str_lit.markdown('</div>', unsafe_allow_html=True)

valid_sub_values = [item[1] for item in current_sub_cards]
choice = str_lit.session_state.get("active_sub_choice", valid_sub_values[0])
if choice not in valid_sub_values:
    choice = valid_sub_values[0]
    str_lit.session_state.active_sub_choice = choice

df_all_employees = str_lit.session_state.employees
df_active_employees = df_all_employees[df_all_employees["حالة الموظف"] == "نشط"] if not df_all_employees.empty else df_all_employees
df_resigned_employees = df_all_employees[df_all_employees["حالة الموظف"].isin(["استقالة", "إيقاف"])] if not df_all_employees.empty else pd.DataFrame()
df_requests = str_lit.session_state.requests
df_attendance = str_lit.session_state.attendance
df_fin = str_lit.session_state.financial_transactions
df_users_local = str_lit.session_state.users

if choice == " الرئيسية":
    
    str_lit.markdown("### 💬 اعتماد طلبات الإجازة السريع :")
    
    pending_requests = df_requests[df_requests["الحالة"] == "قيد الانتظار"] if not df_requests.empty else pd.DataFrame()
    if not pending_requests.empty:
        for p_idx, p_row in pending_requests.iterrows():
            with str_lit.container():
                str_lit.markdown(f"""
                <div style="background: {card_bg}; padding: 12px; border-radius: 10px; border: 1px solid #00A3FF; margin-bottom: 8px;">
                    <b>رقم الطلب:</b> {p_row['رقم الطلب']} &nbsp;|&nbsp; <b>الموظف:</b> {p_row['اسم الموظف']} &nbsp;|&nbsp; <b>النوع:</b> {p_row['نوع الإجازة']} &nbsp;|&nbsp; <b>الفترة:</b> {p_row['من تاريخ']} إلى {p_row['إلى تاريخ']} ({p_row['عدد الأيام']} يوم)<br>
                    <b>السبب الأصلي:</b> {p_row['السبب']}
                </div>
                """, unsafe_allow_html=True)
                
                with str_lit.form(key=f"feedback_form_{p_idx}"):
                    reject_reason_input = str_lit.text_input("سبب الرفض (مطلوب في حال الرغبة برفض الطلب):", value="", key=f"rej_reason_{p_idx}")
                    
                    col_fb1, col_fb2 = str_lit.columns(2)
                    with col_fb1:
                        accept_btn = str_lit.form_submit_button(f"✅ قبول الطلب ", use_container_width=True)
                    with col_fb2:
                        reject_btn = str_lit.form_submit_button(f"❌ رفض الطلب ", use_container_width=True)
                        
                    if accept_btn:
                        df_requests.at[p_idx, "الحالة"] = "مقبول"
                        str_lit.session_state.requests = df_requests
                        auto_save_data()
                        str_lit.success(f"تم اعتماد قبول طلب الموظف ({p_row['اسم الموظف']}) بنجاح!")
                        str_lit.rerun()
                        
                    if reject_btn:
                        df_requests.at[p_idx, "الحالة"] = "مرفوض"
                        if reject_reason_input.strip():
                            df_requests.at[p_idx, "السبب"] = f"{p_row['السبب']} | سبب الرفض: {reject_reason_input.strip()}"
                        str_lit.session_state.requests = df_requests
                        auto_save_data()
                        str_lit.warning(f"تم رفض طلب الموظف ({p_row['اسم الموظف']}).")
                        str_lit.rerun()
    else:
        str_lit.info("لا توجد طلبات إجازة معلقة قيد الانتظار حالياً للإعتماد.")

    str_lit.markdown("---")
    str_lit.markdown("### 🚨 الإنذارات المبكرة لعقود الموظفين التي توشك على الانتهاء:")
    today = datetime.now()
    warning_flag = False

    if not df_active_employees.empty:
        for idx, emp_row in df_active_employees.iterrows():
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
        str_lit.success("✅ جميع عقود الموظفين النشطين سارية ولا توجد تحذيرات قريبة.")

elif choice == " المؤشرات والتحليلات":
    str_lit.markdown(f'<div class="section-header">📈 بطاقة المؤشرات والتحليلات (عدد الموظفين لكل فرع، عدد الموظفين النشطين، والمخططات البيانية بالأعمدة)</div>', unsafe_allow_html=True)
    
    total_active_emps = len(df_active_employees)
    total_active_users = len(df_users_local[df_users_local["الحالة"] == "نشط"]) if not df_users_local.empty else 0
    pending_req_cnt = len(df_requests[df_requests['الحالة'] == 'قيد الانتظار']) if not df_requests.empty else 0

    col1, col2, col3, col4 = str_lit.columns(4)
    with col1:
        str_lit.markdown(f'<div class="foodics-card"><div class="foodics-card-title">👥 عدد الموظفين النشطين</div><div class="foodics-card-value">{total_active_emps}</div></div>', unsafe_allow_html=True)
    with col2:
        str_lit.markdown(f'<div class="foodics-card" style="border-right-color: #10B981;"><div class="foodics-card-title">🛡️ عدد المستخدمين النشطين</div><div class="foodics-card-value" style="color: #10B981;">{total_active_users}</div></div>', unsafe_allow_html=True)
    with col3:
        str_lit.markdown(f'<div class="foodics-card" style="border-right-color: #F59E0B;"><div class="foodics-card-title">⏳ طلبات قيد الانتظار</div><div class="foodics-card-value" style="color: #F59E0B;">{pending_req_cnt}</div></div>', unsafe_allow_html=True)
    with col4:
        str_lit.markdown(f'<div class="foodics-card" style="border-right-color: #0284C7;"><div class="foodics-card-title">📋 إجمالي حركات الحضور</div><div class="foodics-card-value" style="color: #0284C7;">{len(df_attendance)}</div></div>', unsafe_allow_html=True)

    str_lit.markdown("<hr style='border: 0.5px solid #E2E8F0; margin: 12px 0;'>", unsafe_allow_html=True)

    all_branches = df_active_employees["الفرع"].unique().tolist() if not df_active_employees.empty else ["المركز الرئيسي"]
    
    for branch in all_branches:
        str_lit.markdown(f"### 📍 فرع: {branch}")
        branch_emps = df_active_employees[df_active_employees["الفرع"] == branch]
        b_count = len(branch_emps)
        b_sal_total = float(branch_emps["الراتب الأساسي"].sum()) if (not branch_emps.empty and "الراتب الأساسي" in branch_emps.columns) else 0.0
        
        bc1, bc2 = str_lit.columns(2)
        with bc1:
            str_lit.markdown(f'<div class="foodics-card"><div class="foodics-card-title">👥 عدد الموظفين النشطين في فرع {branch}</div><div class="foodics-card-value">{b_count}</div></div>', unsafe_allow_html=True)
        with bc2:
            str_lit.markdown(f'<div class="foodics-card" style="border-right-color: #0284C7;"><div class="foodics-card-title">💰 إجمالي رواتب فرع {branch}</div><div class="foodics-card-value" style="font-size: 18px; color: #0284C7;">{b_sal_total:,.0f} ج.م</div></div>', unsafe_allow_html=True)
        
        if not branch_emps.empty:
            str_lit.markdown(f"**📈 المخطط البياني بالأعمدة لكل فرع على حدة (توزيع الرواتب حسب الوظيفة):**")
            chart_data = branch_emps.set_index("الوظيفة")["الراتب الأساسي"]
            str_lit.bar_chart(chart_data)
            default_cols = ["كود الموظف", "اسم الموظف", "الوظيفة", "القسم", "حالة الموظف", "الراتب الأساسي", "تاريخ بداية العقد", "تاريخ نهاية العقد"]
            available_cols = [col for col in default_cols if col in branch_emps.columns]
            render_printable_table(branch_emps[available_cols], f"قائمة موظفي فرع {branch}")
        str_lit.markdown("<hr style='border: 0.5px dashed #E2E8F0; margin: 10px 0;'>", unsafe_allow_html=True)

elif choice == "تسجيل حضور وانصراف":
    str_lit.subheader("⏱️ تسجيل حركة الحضور والانصراف مع فترة السماح")
    emp_names = df_active_employees["اسم الموظف"].tolist() if not df_active_employees.empty else []
    if emp_names:
        str_lit.markdown('<div class="entry-form-area">', unsafe_allow_html=True)
        with str_lit.form("att_form_custom_time_full"):
            selected_emp = str_lit.selectbox("اختر الموظف", emp_names)
            att_date = str_lit.date_input("تاريخ الحركة", value=date.today())
            emp_info = df_active_employees[df_active_employees["اسم الموظف"] == selected_emp].iloc[0]
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
                    if ampm == "PM": hour_24 += 12
                    return hour_24 * 60 + m

                start_total_min = to_minutes(start_h, start_m, start_ampm)
                end_total_min = to_minutes(end_h, end_m, end_ampm)
                act_in_total_min = to_minutes(act_in_h, act_in_m, act_in_ampm)
                act_out_total_min = to_minutes(act_out_h, act_out_m, act_out_ampm)

                worked_minutes = act_out_total_min - act_in_total_min
                if worked_minutes < 0: worked_minutes += 24 * 60

                standard_minutes = end_total_min - start_total_min
                if standard_minutes < 0: standard_minutes += 24 * 60

                overtime_min = 0
                tardy_min = 0

                in_diff = act_in_total_min - start_total_min
                if in_diff > grace_period_min: tardy_min += (in_diff - grace_period_min)

                diff_total = worked_minutes - standard_minutes
                if diff_total > 0: overtime_min = int(diff_total)

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
                str_lit.success(f"✅ تم تسجيل وحفظ حركة الحضور بنجاح! (التأخير المحسوب: {tardy_min} دقيقة)")
        str_lit.markdown('</div>', unsafe_allow_html=True)
    else:
        str_lit.warning("لا يوجد موظفون نشطون حالياً لتسجيل الحضور.")

elif choice == "سجل الحضور والانصراف":
    render_printable_table(df_attendance, "سجل الحضور والانصراف الشامل")

elif choice == "تعديل أو حذف حركة حضور":
    str_lit.subheader("✏️ تعديل أو حذف حركة حضور والانصراف")
    if not df_attendance.empty:
        att_indices = df_attendance.index.tolist()
        selected_att_idx = str_lit.selectbox("اختر رقم السجل للتعديل أو الحذف", att_indices)
        record = df_attendance.loc[selected_att_idx]
        str_lit.markdown('<div class="entry-form-area">', unsafe_allow_html=True)
        with str_lit.form("edit_att_form_comprehensive"):
            emp_names = df_all_employees["اسم الموظف"].tolist()
            current_emp_idx = emp_names.index(record["اسم الموظف"]) if record["اسم الموظف"] in emp_names else 0
            edit_emp = str_lit.selectbox("اسم الموظف", emp_names, index=current_emp_idx)
            try: default_date = datetime.strptime(str(record["التاريخ"]), "%Y-%m-%d").date()
            except: default_date = date.today()
            edit_date = str_lit.date_input("تاريخ الحركة", value=default_date)
            
            edit_act_in = str_lit.text_input("وقت الحضور الفعلي", value=str(record["وقت الحضور الفعلي"]))
            edit_act_out = str_lit.text_input("وقت الانصراف الفعلي", value=str(record["وقت الانصراف الفعلي"]))
            edit_grace = str_lit.number_input("فترة السماح (دقيقة)", value=int(record.get("فترة السماح (دقيقة)", 15)))
            
            status_list = ["حضور منتظم", "إجازة أسبوعية", "إجازة سنوية", "إجازة مرضية", "إجازة بدون أجر", "غياب"]
            current_stat_idx = status_list.index(record["الحالة"]) if record["الحالة"] in status_list else 0
            edit_status = str_lit.selectbox("حالة الحضور", status_list, index=current_stat_idx)
            
            col_eb1, col_eb2 = str_lit.columns(2)
            with col_eb1:
                if str_lit.form_submit_button("💾 حفظ التعديلات", use_container_width=True):
                    emp_row = df_all_employees[df_all_employees["اسم الموظف"] == edit_emp].iloc[0]
                    str_lit.session_state.attendance.at[selected_att_idx, "اسم الموظف"] = edit_emp
                    str_lit.session_state.attendance.at[selected_att_idx, "كود الموظف"] = emp_row["كود الموظف"]
                    str_lit.session_state.attendance.at[selected_att_idx, "الوظيفة"] = emp_row["الوظيفة"]
                    str_lit.session_state.attendance.at[selected_att_idx, "الفرع"] = emp_row["الفرع"]
                    str_lit.session_state.attendance.at[selected_att_idx, "التاريخ"] = str(edit_date)
                    str_lit.session_state.attendance.at[selected_att_idx, "وقت الحضور الفعلي"] = edit_act_in
                    str_lit.session_state.attendance.at[selected_att_idx, "وقت الانصراف الفعلي"] = edit_act_out
                    str_lit.session_state.attendance.at[selected_att_idx, "فترة السماح (دقيقة)"] = edit_grace
                    str_lit.session_state.attendance.at[selected_att_idx, "الحالة"] = edit_status
                    auto_save_data()
                    str_lit.success("تم تحديث سجل الحضور والانصراف بنجاح!")
                    str_lit.rerun()
            with col_eb2:
                if str_lit.form_submit_button("🗑️ حذف السجل", use_container_width=True):
                    str_lit.session_state.attendance = str_lit.session_state.attendance.drop(selected_att_idx).reset_index(drop=True)
                    auto_save_data()
                    str_lit.success("تم حذف السجل بنجاح!")
                    str_lit.rerun()
        str_lit.markdown('</div>', unsafe_allow_html=True)
    else:
        str_lit.info("لا توجد سجلات حضور متاحة للتعديل.")

elif choice == "تسجيل طلب إجازة":
    str_lit.subheader("📝 تسجيل طلب إجازة جديد للموظف")
    emp_names = df_active_employees["اسم الموظف"].tolist() if not df_active_employees.empty else []
    if emp_names:
        str_lit.markdown('<div class="entry-form-area">', unsafe_allow_html=True)
        with str_lit.form("request_vacation_form_full"):
            req_emp_name = str_lit.selectbox("اختر الموظف", emp_names)
            emp_rec = df_active_employees[df_active_employees["اسم الموظف"] == req_emp_name].iloc[0]
            req_type = str_lit.selectbox("نوع الإجازة", ["إجازة سنوية", "إجازة أسبوعية", "إجازة رسمية", "إجازة مرضية", "إجازة بدون أجر"])
            col_d1, col_d2 = str_lit.columns(2)
            with col_d1: req_start_date = str_lit.date_input("من تاريخ", value=date.today())
            with col_d2: req_end_date = str_lit.date_input("إلى تاريخ", value=date.today() + timedelta(days=1))
            req_reason = str_lit.text_input("سبب طلب الإجازة")
            
            if str_lit.form_submit_button("💾 تقديم طلب الإجازة", use_container_width=True):
                delta_days = (req_end_date - req_start_date).days + 1
                if delta_days <= 0:
                    str_lit.error("❌ تاريخ النهاية يجب أن يكون بعد تاريخ البداية!")
                else:
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
    pending_df = df_requests[df_requests["الحالة"] == "قيد الانتظار"] if not df_requests.empty else pd.DataFrame()
    render_printable_table(pending_df, "طلبات الإجازة قيد الانتظار")

elif choice == "سجل الطلبات المقبولة":
    acc_df = df_requests[df_requests["الحالة"] == "مقبول"] if not df_requests.empty else pd.DataFrame()
    render_printable_table(acc_df, "طلبات الإجازة المقبولة")

elif choice == "سجل الطلبات المرفوضة":
    rej_df = df_requests[df_requests["الحالة"] == "مرفوض"] if not df_requests.empty else pd.DataFrame()
    render_printable_table(rej_df, "طلبات الإجازة المرفوضة")

elif choice == "تعديل أو حذف طلب إجازة":
    str_lit.subheader("✏️ بطاقة تعديل أو حذف طلب الإجازة (تعديل كامل لكافة حقول الطلب)")
    if not df_requests.empty:
        req_ids = df_requests["رقم الطلب"].tolist()
        sel_req_id = str_lit.selectbox("اختر رقم الطلب لتعديله أو حذفه", req_ids)
        req_idx = df_requests[df_requests["رقم الطلب"] == sel_req_id].index[0]
        req_row = df_requests.loc[req_idx]

        str_lit.markdown('<div class="entry-form-area">', unsafe_allow_html=True)
        with str_lit.form("edit_delete_req_form_full"):
            emp_names_list = df_active_employees["اسم الموظف"].tolist() if not df_active_employees.empty else [req_row['اسم الموظف']]
            curr_emp_name = req_row['اسم الموظف']
            edit_req_emp = str_lit.selectbox("اسم الموظف صاحب الطلب", emp_names_list, index=emp_names_list.index(curr_emp_name) if curr_emp_name in emp_names_list else 0)
            
            leave_types = ["إجازة سنوية", "إجازة أسبوعية", "إجازة رسمية", "إجازة مرضية", "إجازة بدون أجر"]
            curr_leave_t = req_row['نوع الإجازة']
            edit_leave_type = str_lit.selectbox("نوع الإجازة", leave_types, index=leave_types.index(curr_leave_t) if curr_leave_t in leave_types else 0)

            try: def_s_date = datetime.strptime(str(req_row['من تاريخ']), "%Y-%m-%d").date()
            except: def_s_date = date.today()
            try: def_e_date = datetime.strptime(str(req_row['إلى تاريخ']), "%Y-%m-%d").date()
            except: def_e_date = date.today() + timedelta(days=1)

            col_ed_d1, col_ed_d2 = str_lit.columns(2)
            with col_ed_d1: edit_start_d = str_lit.date_input("من تاريخ", value=def_s_date)
            with col_ed_d2: edit_end_d = str_lit.date_input("إلى تاريخ", value=def_e_date)

            edit_reason = str_lit.text_input("السبب / ملاحظات الطلب", value=str(req_row['السبب']))

            status_options = ["قيد الانتظار", "مقبول", "مرفوض"]
            curr_st = req_row["الحالة"]
            edit_r_status = str_lit.selectbox("حالة الاعتماد والقرار (إبداء الرأي)", status_options, index=status_options.index(curr_st) if curr_st in status_options else 0)

            col_rq1, col_rq2 = str_lit.columns(2)
            with col_rq1: up_req_btn = str_lit.form_submit_button("💾 حفظ كافة التعديلات للطلب", use_container_width=True)
            with col_rq2: del_req_btn = str_lit.form_submit_button("🗑️ حذف هذا الطلب نهائياً", use_container_width=True)

            if up_req_btn:
                delta_days = (edit_end_d - edit_start_d).days + 1
                if delta_days <= 0:
                    str_lit.error("❌ تاريخ النهاية يجب أن يكون بعد تاريخ البداية!")
                else:
                    emp_info_rec = df_active_employees[df_active_employees["اسم الموظف"] == edit_req_emp].iloc[0] if not df_active_employees.empty else None
                    str_lit.session_state.requests.at[req_idx, "اسم الموظف"] = edit_req_emp
                    if emp_info_rec is not None:
                        str_lit.session_state.requests.at[req_idx, "كود الموظف"] = emp_info_rec["كود الموظف"]
                        str_lit.session_state.requests.at[req_idx, "الوظيفة"] = emp_info_rec["الوظيفة"]
                        str_lit.session_state.requests.at[req_idx, "الفرع"] = emp_info_rec["الفرع"]
                    str_lit.session_state.requests.at[req_idx, "نوع الإجازة"] = edit_leave_type
                    str_lit.session_state.requests.at[req_idx, "من تاريخ"] = edit_start_d.strftime("%Y-%m-%d")
                    str_lit.session_state.requests.at[req_idx, "إلى تاريخ"] = edit_end_d.strftime("%Y-%m-%d")
                    str_lit.session_state.requests.at[req_idx, "عدد الأيام"] = int(delta_days)
                    str_lit.session_state.requests.at[req_idx, "السبب"] = edit_reason
                    str_lit.session_state.requests.at[req_idx, "الحالة"] = edit_r_status
                    auto_save_data()
                    str_lit.success("✅ تم تحديث كافة حقول طلب الإجازة بنجاح تام!")
                    str_lit.rerun()

            if del_req_btn:
                str_lit.session_state.requests = str_lit.session_state.requests.drop(req_idx).reset_index(drop=True)
                auto_save_data()
                str_lit.warning("🗑️ تم حذف طلب الإجازة بنجاح!")
                str_lit.rerun()
        str_lit.markdown('</div>', unsafe_allow_html=True)
    else:
        str_lit.info("لا توجد طلبات إجازة مسجلة لتعديلها أو حذفها.")

elif choice == "تسجيل معاملة مالية":
    str_lit.subheader("💵 تسجيل معاملة مالية ")
    emp_names = df_active_employees["اسم الموظف"].tolist() if not df_active_employees.empty else []
    if emp_names:
        str_lit.markdown('<div class="entry-form-area">', unsafe_allow_html=True)
        with str_lit.form("fin_trans_form_full"):
            f_emp = str_lit.selectbox("اختر الموظف", emp_names)
            f_emp_rec = df_active_employees[df_active_employees["اسم الموظف"] == f_emp].iloc[0]
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

elif choice == "تسجيل إذن (انصراف / تأخير)":
    str_lit.subheader("⏱️ تسجيل إذن رسمي (انصراف مبكر أو تأخير مستأذن)")
    emp_names = df_active_employees["اسم الموظف"].tolist() if not df_active_employees.empty else []
    if emp_names:
        str_lit.markdown('<div class="entry-form-area">', unsafe_allow_html=True)
        with str_lit.form("permission_form_full"):
            p_emp = str_lit.selectbox("اختر الموظف للإذن", emp_names)
            p_emp_rec = df_active_employees[df_active_employees["اسم الموظف"] == p_emp].iloc[0]
            p_type = str_lit.selectbox("نوع الإذن", ["إذن انصراف مبكر", "إذن تأخير عن الحضور", "إذن طارئ خلال العمل"])
            p_hours = str_lit.number_input("عدد ساعات الإذن المستأذنة", min_value=0.5, max_value=8.0, value=1.0, step=0.5)
            p_reason = str_lit.text_input("سبب الإذن")
            p_date = str_lit.date_input("تاريخ الإذن", value=date.today())

            if str_lit.form_submit_button("💾 حفظ الإذن الرسمي", use_container_width=True):
                new_perm_row = {
                    "التاريخ": p_date.strftime("%Y-%m-%d"),
                    "كود الموظف": p_emp_rec["كود الموظف"],
                    "اسم الموظف": p_emp,
                    "الفرع": p_emp_rec["الفرع"],
                    "النوع": f"إذن: {p_type} ({p_hours} ساعات)",
                    "المبلغ / القيمة": 0.0,
                    "البيان / السبب": p_reason,
                    "الحالة": "قيد الانتظار"
                }
                str_lit.session_state.financial_transactions = pd.concat([str_lit.session_state.financial_transactions, pd.DataFrame([new_perm_row])], ignore_index=True)
                auto_save_data()
                str_lit.success("✅ تم تسجيل الإذن الرسمي بنجاح!")
        str_lit.markdown('</div>', unsafe_allow_html=True)

elif choice == "سجل المعاملات المالية والأذونات":
    render_printable_table(df_fin, "سجل المعاملات المالية والأذونات الشامل")

elif choice == "إدارة واعتماد المعاملات والأذونات":
    str_lit.subheader("⚖️ إدارة واعتماد أو حذف المعاملات المالية والأذونات")
    if not df_fin.empty:
        fin_options = [f"{idx} - {row['التاريخ']} - {row['اسم الموظف']} ({row['النوع']}: {row['المبلغ / القيمة']})" for idx, row in df_fin.iterrows()]
        sel_fin = str_lit.selectbox("اختر المعاملة للاعتماد", fin_options)
        fin_idx = int(sel_fin.split(" - ")[0])
        fin_row = df_fin.loc[fin_idx]

        str_lit.markdown('<div class="entry-form-area">', unsafe_allow_html=True)
        with str_lit.form("manage_fin_form_integrated"):
            str_lit.markdown(f"**الموظف:** {fin_row['اسم الموظف']} | **النوع:** {fin_row['النوع']} | **القيمة:** {fin_row['المبلغ / القيمة']}")
            fin_status_options = ["معتمد", "قيد الانتظار", "مرفوض"]
            current_f_st = fin_row.get("الحالة", "معتمد")
            current_f_idx = fin_status_options.index(current_f_st) if current_f_st in fin_status_options else 0
            edit_fin_status = str_lit.selectbox("حالة الاعتماد والقرار", fin_status_options, index=current_f_idx)

            col_f1, col_f2 = str_lit.columns(2)
            with col_f1: up_f_btn = str_lit.form_submit_button("💾 حفظ الاعتماد", use_container_width=True)
            with col_f2: del_f_btn = str_lit.form_submit_button("🗑️ حذف المعاملة", use_container_width=True)

            if up_f_btn:
                str_lit.session_state.financial_transactions.at[fin_idx, "الحالة"] = edit_fin_status
                auto_save_data()
                str_lit.success(f"✅ تم تحديث المعاملة كـ ({edit_fin_status})!")
                str_lit.rerun()

            if del_f_btn:
                str_lit.session_state.financial_transactions = str_lit.session_state.financial_transactions.drop(fin_idx).reset_index(drop=True)
                auto_save_data()
                str_lit.warning("🗑️ تم حذف المعاملة بنجاح!")
                str_lit.rerun()
        str_lit.markdown('</div>', unsafe_allow_html=True)
    else:
        str_lit.info("لا توجد معاملات مالية مسجلة.")

elif choice == "إضافة موظف جديد":
    str_lit.subheader("➕ إضافة موظف جديد، مسوغات التعيين وتحديد الحالة والعقود")
    str_lit.markdown('<div class="entry-form-area">', unsafe_allow_html=True)
    
    emp_code_in = str_lit.text_input("كود الموظف", value=f"EMP{len(df_all_employees)+1:03d}")
    emp_name_in = str_lit.text_input("اسم الموظف الرباعي")
    col_e1, col_e2 = str_lit.columns(2)
    with col_e1:
        emp_job_in = str_lit.text_input("الوظيفة / المسمى الوظيفي")
        emp_dept_in = str_lit.text_input("القسم التابع")
        emp_branch_in = str_lit.selectbox("الفرع التابع", ["المركز الرئيسي", "فرع الإسكندرية", "فرع الشرم"])
        emp_salary_in = str_lit.number_input("الراتب الأساسي (ج.م)", min_value=0.0, value=5000.0, step=100.0)
    with col_e2:
        emp_status_in = str_lit.selectbox("حالة الموظف", ["نشط", "استقالة", "إيقاف"])
        emp_role_in = str_lit.selectbox("صلاحية الموظف بالنظام", ["مستخدم عادي", "اعتماد الطلبات", "مدير الفرع"])
        emp_docs_status = str_lit.selectbox("حالة مسوغات التعيين", ["مكتملة", "ناقصة مستندات"])
        contract_start_in = str_lit.date_input("تاريخ بداية العقد", value=date.today())
        contract_end_in = str_lit.date_input("تاريخ نهاية العقد", value=date.today() + timedelta(days=365))

    str_lit.markdown("📁 **رفع ملف مسوغات ومستندات التعيين (PDF أو صور):**")
    uploaded_doc_file = str_lit.file_uploader("اختر ملف المستندات للموظف", type=["pdf", "png", "jpg", "jpeg"])
    
    saved_file_path = ""
    if uploaded_doc_file is not None:
        try:
            file_extension = uploaded_doc_file.name.split('.')[-1]
            safe_file_name = f"{emp_code_in}_{datetime.now().strftime('%Y%m%d%H%M%S')}.{file_extension}"
            saved_file_path = os.path.join(DOCS_DIR, safe_file_name)
            with open(saved_file_path, "wb") as f:
                f.write(uploaded_doc_file.getbuffer())
            str_lit.success(f"📁 تم رفع وحفظ ملف المستندات بنجاح: {safe_file_name}")
        except Exception as e:
            str_lit.error(f"خطأ في رفع الملف: {e}")

    str_lit.markdown("---")
    str_lit.markdown("📌 **أرصدة الإجازات الإجمالية:**")
    col_b1, col_b2, col_b3, col_b4 = str_lit.columns(4)
    with col_b1: ann_total = str_lit.number_input("رصيد سنوي (إجمالي)", value=21)
    with col_b2: week_total = str_lit.number_input("رصيد أسبوعي (إجمالي)", value=4)
    with col_b3: off_total = str_lit.number_input("رصيد رسمي (إجمالي)", value=10)
    with col_b4: sick_days = str_lit.number_input("إجازات مرضية (أيام)", value=0)

    if str_lit.button("💾 حفظ بيانات الموظف", use_container_width=True):
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
                "حالة الموظف": emp_status_in,
                "الراتب الأساسي": float(emp_salary_in),
                "مسوغات التعيين": emp_docs_status,
                "ملف المستندات": saved_file_path,
                "تاريخ بداية العقد": contract_start_in.strftime("%Y-%m-%d"),
                "تاريخ نهاية العقد": contract_end_in.strftime("%Y-%m-%d"),
                "رصيد سنوي (إجمالي)": int(ann_total),
                "رصيد أسبوعي (إجمالي)": int(week_total),
                "رصيد رسمي (إجمالي)": int(off_total),
                "إجازات مرضية (أيام)": int(sick_days)
            }
            str_lit.session_state.employees = pd.concat([str_lit.session_state.employees, pd.DataFrame([new_emp_data])], ignore_index=True)
            auto_save_data()
            str_lit.success(f"✅ تم إضافة الموظف ({emp_name_in}) بحالة ({emp_status_in}) بنجاح تام!")
    str_lit.markdown('</div>', unsafe_allow_html=True)

elif choice == "سجل الموظفين النشطين والشامل":
    render_printable_table(df_active_employees, "سجل الموظفين النشطين")

elif choice == "سجل الموظفين المستقيلين والموقوفين":
    str_lit.subheader("🚪 سجل الموظفين المستقيلين والموقوفين عن العمل")
    render_printable_table(df_resigned_employees, "سجل الموظفين (استقالة / إيقاف)")
    
    if not df_resigned_employees.empty:
        str_lit.markdown("---")
        str_lit.markdown("### 🔄 تعديل بيانات أو إعادة تفعيل موظف مستقيـل / موقوف")
        res_names = df_resigned_employees["اسم الموظف"].tolist()
        sel_res_emp = str_lit.selectbox("اختر الموظف من سجل المستقيلين/الموقوفين للتعديل:", res_names, key="sel_res_emp_box")
        res_idx = df_all_employees[df_all_employees["اسم الموظف"] == sel_res_emp].index[0]
        res_row = df_all_employees.loc[res_idx]

        str_lit.markdown('<div class="entry-form-area">', unsafe_allow_html=True)
        with str_lit.form("edit_resigned_emp_form"):
            r_name = str_lit.text_input("اسم الموظف", value=str(res_row["اسم الموظف"]))
            col_r1, col_r2 = str_lit.columns(2)
            with col_r1:
                r_job = str_lit.text_input("الوظيفة", value=str(res_row["الوظيفة"]))
                r_salary = str_lit.number_input("الراتب الأساسي", value=float(res_row["الراتب الأساسي"]))
            with col_r2:
                status_opts = ["نشط", "استقالة", "إيقاف"]
                curr_st = res_row.get("حالة الموظف", "استقالة")
                r_status = str_lit.selectbox("تحديث حالة الموظف (إعادة للعمل كـ نشط أو تعديل)", status_opts, index=status_opts.index(curr_st) if curr_st in status_opts else 1)
                try: r_end_d = datetime.strptime(str(res_row.get("تاريخ نهاية العقد", date.today())), "%Y-%m-%d").date()
                except: r_end_d = date.today()
                r_contract_end = str_lit.date_input("تاريخ نهاية العقد / الاستقالة", value=r_end_d)

            if str_lit.form_submit_button("💾 حفظ التعديلات وتحديث الحالة", use_container_width=True):
                str_lit.session_state.employees.at[res_idx, "اسم الموظف"] = r_name
                str_lit.session_state.employees.at[res_idx, "الوظيفة"] = r_job
                str_lit.session_state.employees.at[res_idx, "الراتب الأساسي"] = float(r_salary)
                str_lit.session_state.employees.at[res_idx, "حالة الموظف"] = r_status
                str_lit.session_state.employees.at[res_idx, "تاريخ نهاية العقد"] = r_contract_end.strftime("%Y-%m-%d")
                auto_save_data()
                str_lit.success(f"✅ تم تحديث بيانات الموظف ({r_name}) وحالته الآن: ({r_status})!")
                str_lit.rerun()
        str_lit.markdown('</div>', unsafe_allow_html=True)

elif choice == "تعديل أو حذف موظف":
    str_lit.subheader("✏️ تعديل كافة حقول بيانات موظف (نشط / استقالة / إيقاف) أو حذفه")
    if not df_all_employees.empty:
        emp_names_edit = df_all_employees["اسم الموظف"].tolist()
        selected_emp_edit = str_lit.selectbox("اختر الموظف للتعديل الشامل أو الحذف", emp_names_edit)
        
        emp_row_data = df_all_employees[df_all_employees["اسم الموظف"] == selected_emp_edit].iloc[0]
        emp_idx = df_all_employees[df_all_employees["اسم الموظف"] == selected_emp_edit].index[0]

        str_lit.markdown('<div class="entry-form-area">', unsafe_allow_html=True)
        with str_lit.form("edit_all_emp_form"):
            e_name = str_lit.text_input("اسم الموظف الرباعي", value=str(emp_row_data["اسم الموظف"]))
            col_ed1, col_ed2 = str_lit.columns(2)
            with col_ed1:
                e_job = str_lit.text_input("الوظيفة", value=str(emp_row_data["الوظيفة"]))
                e_dept = str_lit.text_input("القسم", value=str(emp_row_data["القسم"]))
                branches_list = ["المركز الرئيسي", "فرع الإسكندرية", "فرع الشرم"]
                current_b_idx = branches_list.index(emp_row_data["الفرع"]) if emp_row_data["الفرع"] in branches_list else 0
                e_branch = str_lit.selectbox("الفرع التابع", branches_list, index=current_b_idx)
                e_salary = str_lit.number_input("الراتب الأساسي (ج.م)", min_value=0.0, value=float(emp_row_data["الراتب الأساسي"]))
            with col_ed2:
                emp_status_opts = ["نشط", "استقالة", "إيقاف"]
                curr_emp_st = emp_row_data.get("حالة الموظف", "نشط")
                e_status = str_lit.selectbox("حالة الموظف", emp_status_opts, index=emp_status_opts.index(curr_emp_st) if curr_emp_st in emp_status_opts else 0)
                
                roles_list = ["مستخدم عادي", "اعتماد الطلبات", "مدير الفرع"]
                current_r_idx = roles_list.index(emp_row_data["صلاحية الموظف"]) if emp_row_data["صلاحية الموظف"] in roles_list else 0
                e_role = str_lit.selectbox("صلاحية الموظف بالنظام", roles_list, index=current_r_idx)
                
                docs_list = ["مكتملة", "ناقصة مستندات"]
                current_d_idx = docs_list.index(emp_row_data["مسوغات التعيين"]) if emp_row_data["مسوغات التعيين"] in docs_list else 0
                e_docs = str_lit.selectbox("حالة مسوغات التعيين", docs_list, index=current_d_idx)
                
                try: default_start = datetime.strptime(str(emp_row_data.get("تاريخ بداية العقد", date.today())), "%Y-%m-%d").date()
                except Exception: default_start = date.today()
                try: default_end = datetime.strptime(str(emp_row_data.get("تاريخ نهاية العقد", date.today())), "%Y-%m-%d").date()
                except Exception: default_end = date.today() + timedelta(days=365)

                e_contract_start = str_lit.date_input("تاريخ بداية العقد", value=default_start)
                e_contract_end = str_lit.date_input("تاريخ نهاية العقد", value=default_end)

            col_sub_ed1, col_sub_ed2 = str_lit.columns(2)
            with col_sub_ed1: up_emp_btn = str_lit.form_submit_button("💾 حفظ كافة التعديلات للموظف", use_container_width=True)
            with col_sub_ed2: del_emp_btn = str_lit.form_submit_button("🗑️ حذف هذا الموظف نهائياً", use_container_width=True, type="primary")

            if up_emp_btn:
                str_lit.session_state.employees.at[emp_idx, "اسم الموظف"] = e_name
                str_lit.session_state.employees.at[emp_idx, "الوظيفة"] = e_job
                str_lit.session_state.employees.at[emp_idx, "القسم"] = e_dept
                str_lit.session_state.employees.at[emp_idx, "الفرع"] = e_branch
                str_lit.session_state.employees.at[emp_idx, "حالة الموظف"] = e_status
                str_lit.session_state.employees.at[emp_idx, "صلاحية الموظف"] = e_role
                str_lit.session_state.employees.at[emp_idx, "الراتب الأساسي"] = float(e_salary)
                str_lit.session_state.employees.at[emp_idx, "مسوغات التعيين"] = e_docs
                str_lit.session_state.employees.at[emp_idx, "تاريخ بداية العقد"] = e_contract_start.strftime("%Y-%m-%d")
                str_lit.session_state.employees.at[emp_idx, "تاريخ نهاية العقد"] = e_contract_end.strftime("%Y-%m-%d")
                auto_save_data()
                str_lit.success(f"✅ تم تحديث بيانات الموظف وحالته ({e_status}) بنجاح تام!")
                str_lit.rerun()

            if del_emp_btn:
                str_lit.session_state.employees = str_lit.session_state.employees.drop(emp_idx).reset_index(drop=True)
                auto_save_data()
                str_lit.warning("🗑️ تم حذف الموظف بنجاح!")
                str_lit.rerun()
        str_lit.markdown('</div>', unsafe_allow_html=True)

elif choice == "رفع نموذج بيانات الموظفين":
    str_lit.subheader("📤 رفع نموذج بيانات الموظفين المعبأ (CSV)")
    uploaded_template = str_lit.file_uploader("اختر ملف النموذج المعبأ (.csv)", type=["csv"])
    if uploaded_template is not None:
        try:
            df_imported = pd.read_csv(uploaded_template)
            if "حالة الموظف" not in df_imported.columns:
                df_imported["حالة الموظف"] = "نشط"
            render_printable_table(df_imported, "معاينة الملف المستورد")
            if str_lit.button("📥 اعتماد ودمج هذه البيانات في قاعدة الموظفين", use_container_width=True):
                str_lit.session_state.employees = pd.concat([str_lit.session_state.employees, df_imported], ignore_index=True)
                auto_save_data()
                str_lit.success("✅ تم استيراد ودمج بيانات الموظفين بنجاح تام!")
                str_lit.rerun()
        except Exception as e:
            str_lit.error(f"❌ خطأ أثناء قراءة الملف: {e}")

elif choice == "كشف الرواتب والمستحقات الشامل":
    str_lit.subheader("💰 كشف الرواتب والمستحقات الشامل للموظفين النشطين")
    if not df_active_employees.empty:
        df_sal = df_active_employees[["كود الموظف", "اسم الموظف", "الوظيفة", "القسم", "الفرع", "الراتب الأساسي"]].copy()
        df_sal["بدلات وحوافز"] = 0.0
        df_sal["خصومات وإذونات"] = 0.0
        df_sal["الصافي المستحق"] = df_sal["الراتب الأساسي"]
        render_printable_table(df_sal, "كشف الرواتب والمستحقات")
    else:
        str_lit.info("لا توجد بيانات رواتب للموظفين النشطين.")

elif choice == "إضافة مستخدم جديد":
    str_lit.subheader("🛡️ إضافة مستخدم جديد للنظام")
    str_lit.markdown('<div class="entry-form-area">', unsafe_allow_html=True)
    with str_lit.form("add_user_form_full"):
        u_name_in = str_lit.text_input("اسم المستخدم (Username)")
        u_full_in = str_lit.text_input("الاسم الكامل للمستخدم")
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

elif choice == "إدارة المستخدمين والصلاحيات والسجل":
    render_printable_table(str_lit.session_state.users, "سجل مستخدمي النظام")

elif choice == "تعديل أو حذف مستخدم":
    str_lit.subheader("✏️ تعديل بيانات مستخدم أو حذفه")
    if not str_lit.session_state.users.empty:
        user_usernames = str_lit.session_state.users["اسم المستخدم"].tolist()
        sel_usr = str_lit.selectbox("اختر اسم المستخدم للتعديل", user_usernames)
        usr_idx = str_lit.session_state.users[str_lit.session_state.users["اسم المستخدم"] == sel_usr].index[0]
        usr_row = str_lit.session_state.users.loc[usr_idx]

        str_lit.markdown('<div class="entry-form-area">', unsafe_allow_html=True)
        with str_lit.form("edit_all_user_form"):
            new_u_full = str_lit.text_input("الاسم الكامل", value=str(usr_row["الاسم الكامل"]))
            new_u_status = str_lit.selectbox("الحالة", ["نشط", "إيقاف"], index=0 if usr_row.get("الحالة") == "نشط" else 1)
            new_u_pattern = str_lit.text_input("الرسم السري", value=str(usr_row["الرسم السري"]))

            col_us1, col_us2 = str_lit.columns(2)
            with col_us1: up_u_btn = str_lit.form_submit_button("💾 حفظ التعديلات", use_container_width=True)
            with col_us2: del_u_btn = str_lit.form_submit_button("🗑️ حذف المستخدم", use_container_width=True)

            if up_u_btn:
                str_lit.session_state.users.at[usr_idx, "الاسم الكامل"] = new_u_full
                str_lit.session_state.users.at[usr_idx, "الحالة"] = new_u_status
                str_lit.session_state.users.at[usr_idx, "الرسم السري"] = new_u_pattern
                auto_save_data()
                str_lit.success("✅ تم تحديث بيانات المستخدم بنجاح!")
                str_lit.rerun()

            if del_u_btn:
                if sel_usr == "admin":
                    str_lit.error("❌ لا يمكن حذف الحساب الإداري الرئيسي (admin)!")
                else:
                    str_lit.session_state.users = str_lit.session_state.users.drop(usr_idx).reset_index(drop=True)
                    auto_save_data()
                    str_lit.warning("🗑️ تم حذف المستخدم بنجاح!")
                    str_lit.rerun()
        str_lit.markdown('</div>', unsafe_allow_html=True)

elif choice == "طباعة التقارير العامة":
    str_lit.subheader("🖨️ طباعة التقارير العامة والشاملة")
    report_type = str_lit.selectbox("اختر نوع التقرير", ["تقرير الموظفين النشطين", "تقرير الموظفين المستقيلين والموقوفين", "تقرير الحضور والانصراف", "تقرير طلبات الإجازات", "تقرير المعاملات المالية"])
    
    if report_type == "تقرير الموظفين النشطين":
        render_printable_table(df_active_employees, "تقرير الموظفين النشطين")
    elif report_type == "تقرير الموظفين المستقيلين والموقوفين":
        render_printable_table(df_resigned_employees, "تقرير الموظفين المستقيلين والموقوفين")
    elif report_type == "تقرير الحضور والانصراف":
        render_printable_table(df_attendance, "تقرير الحضور والانصراف")
    elif report_type == "تقرير طلبات الإجازات":
        render_printable_table(df_requests, "تقرير طلبات الإجازات")
    elif report_type == "تقرير المعاملات المالية":
        render_printable_table(df_fin, "تقرير المعاملات المالية")

elif choice == "إعدادات الشركة وبياناتها الشاملة":
    str_lit.subheader("⚙️ إعدادات وبيانات الشركة الرسمية ورفع الشعار")
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

        uploaded_logo = str_lit.file_uploader("اختر شعار الشركة", type=["png", "jpg", "jpeg", "ico"])
        current_logo_val = info.get("logo", "")
        if uploaded_logo is not None:
            bytes_data = uploaded_logo.getvalue()
            b64_encoded = base64.b64encode(bytes_data).decode()
            ext = uploaded_logo.name.split('.')[-1]
            current_logo_val = f"data:image/{ext};base64,{b64_encoded}"

        if str_lit.form_submit_button("💾 حفظ تحديثات إعدادات الشركة", use_container_width=True):
            str_lit.session_state.company_info = {
                "name": c_name_in,
                "address": c_addr_in,
                "cr": c_cr_in,
                "tax": c_tax_in,
                "contact": c_contact_in,
                "email": c_email_in,
                "license": c_lic_in,
                "logo": current_logo_val
            }
            auto_save_data()
            str_lit.success("✅ تم تحديث وحفظ إعدادات الشركة بنجاح!")
            str_lit.rerun()
    str_lit.markdown('</div>', unsafe_allow_html=True)

elif choice == "تحميل النماذج (Templates)":
    str_lit.subheader("📥 تحميل نماذج الإدخال الجاهزة")
    t_df = pd.DataFrame(columns=["كود الموظف", "اسم الموظف", "الوظيفة", "القسم", "الفرع", "صلاحية الموظف", "حالة الموظف", "الراتب الأساسي", "مسوغات التعيين", "تاريخ بداية العقد", "تاريخ نهاية العقد", "رصيد سنوي (إجمالي)", "رصيد أسبوعي (إجمالي)", "رصيد رسمي (إجمالي)", "إجازات مرضية (أيام)"])
    csv_data_bytes = t_df.to_csv(index=False).encode('utf-8-sig')
    str_lit.download_button(label="📥 تحميل نموذج بيانات الموظفين (CSV)", data=csv_data_bytes, file_name="Employees_Template.csv", mime="text/csv", use_container_width=True)

elif choice == "نسخة احتياطية واستعادة":
    str_lit.subheader("💾 النسخ الاحتياطي واستعادة البيانات")
    col_bk1, col_bk2 = str_lit.columns(2)
    with col_bk1:
        full_export_data = {
            "employees": str_lit.session_state.employees.to_dict(orient='records'),
            "requests": str_lit.session_state.requests.to_dict(orient='records'),
            "attendance": str_lit.session_state.attendance.to_dict(orient='records'),
            "financial_transactions": str_lit.session_state.financial_transactions.to_dict(orient='records'),
            "users": str_lit.session_state.users.to_dict(orient='records'),
            "company_info": str_lit.session_state.company_info
        }
        json_str = json.dumps(full_export_data, ensure_ascii=False, indent=4)
        str_lit.download_button(label="📥 تحميل النسخة الاحتياطية (JSON)", data=json_str.encode('utf-8-sig'), file_name=f"ERP_Backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json", mime="application/json", use_container_width=True)
    with col_bk2:
        uploaded_backup = str_lit.file_uploader("رفع ملف النسخة الاحتياطية (.json)", type=["json"])
        if uploaded_backup is not None and str_lit.button("🔄 استعادة البيانات الآن", use_container_width=True):
            try:
                imported_data = json.load(uploaded_backup)
                if "employees" in imported_data: str_lit.session_state.employees = pd.DataFrame(imported_data["employees"])
                if "requests" in imported_data: str_lit.session_state.requests = pd.DataFrame(imported_data["requests"])
                if "attendance" in imported_data: str_lit.session_state.attendance = pd.DataFrame(imported_data["attendance"])
                if "financial_transactions" in imported_data: str_lit.session_state.financial_transactions = pd.DataFrame(imported_data["financial_transactions"])
                if "users" in imported_data: str_lit.session_state.users = pd.DataFrame(imported_data["users"])
                if "company_info" in imported_data: str_lit.session_state.company_info = imported_data["company_info"]
                auto_save_data()
                str_lit.success("✅ تمت استعادة البيانات بنجاح!")
                str_lit.rerun()
            except Exception as e:
                str_lit.error(f"❌ خطأ: {e}")

elif choice == "مسح البيانات":
    str_lit.subheader("⚠️ مسح وتصفير بيانات المنظومة")
    if str_lit.button("🚨 تأكيد مسح كافة البيانات", type="primary"):
        str_lit.session_state.employees = pd.DataFrame(columns=[
            "كود الموظف", "اسم الموظف", "الوظيفة", "القسم", "الفرع", "صلاحية الموظف", "حالة الموظف",
            "الراتب الأساسي", "مسوغات التعيين", "ملف المستندات", "تاريخ بداية العقد", "تاريخ نهاية العقد",
            "رصيد سنوي (إجمالي)", "رصيد أسبوعي (إجمالي)", "رصيد رسمي (إجمالي)", "إجازات مرضية (أيام)"
        ])
        str_lit.session_state.requests = pd.DataFrame(columns=["رقم الطلب", "كود الموظف", "اسم الموظف", "الوظيفة", "الفرع", "نوع الإجازة", "من تاريخ", "إلى تاريخ", "عدد الأيام", "السبب", "الحالة"])
        str_lit.session_state.attendance = pd.DataFrame(columns=["التاريخ", "كود الموظف", "اسم الموظف", "الوظيفة", "الفرع", "بداية العمل الرسمية", "نهاية العمل الرسمية", "وقت الحضور الفعلي", "وقت الانصراف الفعلي", "فترة السماح (دقيقة)", "الحالة", "التأخير (دقيقة)", "إضافي (دقيقة)"])
        str_lit.session_state.financial_transactions = pd.DataFrame(columns=["التاريخ", "كود الموظف", "اسم الموظف", "الفرع", "النوع", "المبلغ / القيمة", "البيان / السبب", "الحالة"])
        auto_save_data()
        str_lit.success("✅ تم تصفير البيانات بنجاح!")
        str_lit.rerun()

str_lit.markdown("<hr style='border: 0.5px solid #E2E8F0; margin: 20px 0;'>", unsafe_allow_html=True)
str_lit.markdown("<p style='text-align: center; color: #64748B; font-size: 11px;'>جميع الحقوق محفوظة © النظام المتكامل لإدارة الموارد البشرية (ERP)</p>", unsafe_allow_html=True)