import streamlit as str_lit
import pandas as pd
from datetime import datetime, date, time, timedelta
import json
import os
import io
import base64
import uuid

str_lit.set_page_config(
    page_title="سيستم الموارد البشرية المتكامل - إعداد أ/ إبراهيم محمد علي",
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
        "name": "سيستم الموارد البشرية المتكامل"
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

# دالة الجداول الموحدة (محاذاة سنتر تامة للتواريخ والأرقام والنصوص)
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
        border-bottom: 2px solid #0284C7;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
    }}
    
    .main-content-spacer {{
        margin-top: 150px !important;
    }}
    
    /* تصميم الروابط والبطاقات الملونة على طراز إبراهيم محمد علي */
    .dashboard-title-box {{
        background: linear-gradient(135deg, #2C1810, #3E2723);
        color: white;
        padding: 15px;
        border-radius: 12px;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.15);
        margin-bottom: 15px;
        border: 2px solid #5D4037;
    }}
    .dashboard-title-box h2 {{
        color: #FFD54F !important;
        font-size: 22px !important;
        margin: 0 0 5px 0 !important;
    }}
    .dashboard-title-box p {{
        color: #E0E0E0 !important;
        font-size: 14px !important;
        margin: 0 !important;
    }}
    
    .kpi-card-box {{
        background: {card_bg};
        border: 1px solid #E2E8F0;
        padding: 12px;
        border-radius: 10px;
        text-align: center;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
        margin-bottom: 8px;
    }}
    .kpi-card-title {{
        font-size: 11px;
        color: #64748B;
        font-weight: bold;
        margin-bottom: 4px;
    }}
    .kpi-card-val {{
        font-size: 18px;
        color: {card_value_color};
        font-weight: bold;
    }}
    </style>
""", unsafe_allow_html=True)

if 'is_authenticated' not in str_lit.session_state: str_lit.session_state.is_authenticated = False
if 'current_logged_user' not in str_lit.session_state: str_lit.session_state.current_logged_user = ""
if 'current_user_dept' not in str_lit.session_state: str_lit.session_state.current_user_dept = ""
if 'current_user_branch' not in str_lit.session_state: str_lit.session_state.current_user_branch = ""
if 'current_user_role' not in str_lit.session_state: str_lit.session_state.current_user_role = ""
if 'active_main_section' not in str_lit.session_state: str_lit.session_state.active_main_section = "الرئيسية"

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
        <div style="max-width: 480px; margin: 20px auto; background: {card_bg}; padding: 30px; border-radius: 16px; box-shadow: 0 10px 30px rgba(0,0,0,0.08); text-align: center; border: 1px solid #E2E8F0;">
            <h2 style="color: #0284C7; margin-bottom: 6px; font-size: 20px;">تسجيل الدخول - سيستم الموارد البشرية</h2>
            <p style="font-size: 14px; font-weight: bold; margin-bottom: 4px;">إعداد أ/ إبراهيم محمد علي</p>
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

# الشريط العلوي الثابت مع زر الفلتر المنسدل
str_lit.markdown('<div class="sticky-top-wrapper">', unsafe_allow_html=True)
col_top_h1, col_top_h2, col_top_h3 = str_lit.columns([3, 2, 1])
with col_top_h1:
    str_lit.markdown("### 🏢 سيستم الموارد البشرية المتكامل")
    str_lit.markdown("<p style='font-size: 11px; color: #64748B; margin: 0;'>إعداد أ/ إبراهيم محمد علي</p>", unsafe_allow_html=True)

with col_top_h2:
    logged_username = str_lit.session_state.current_logged_user
    user_branch = str_lit.session_state.current_user_branch
    str_lit.markdown(f"<div style='font-size: 11px; background: rgba(2,132,199,0.1); padding: 4px 8px; border-radius: 6px;'>👤 <b>{logged_username}</b> | 📍 <b>{user_branch}</b></div>", unsafe_allow_html=True)

with col_top_h3:
    if str_lit.button("⏹️ خروج", use_container_width=True):
        str_lit.session_state.is_authenticated = False
        str_lit.session_state.current_logged_user = ""
        str_lit.rerun()

str_lit.markdown('</div>', unsafe_allow_html=True)
str_lit.markdown('<div class="main-content-spacer"></div>', unsafe_allow_html=True)

# -------------------------------------------------------------------------
# زر تصفية البيانات المنسدل (Popover Filter Button)
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

# -------------------------------------------------------------------------
# شبكة البطاقات الرئيسية الـ 9 مثل الصورة تماماً
# -------------------------------------------------------------------------
str_lit.markdown("""
    <div class="dashboard-title-box">
        <h2>سيستم الموارد البشرية المتكامل</h2>
        <p>أعداد أ/ إبراهيم محمد علي</p>
    </div>
""", unsafe_allow_html=True)

# الصف الأول من البطاقات
r1_c1, r1_c2, r1_c3 = str_lit.columns(3)
with r1_c1:
    if str_lit.button("🔴 الغياب", use_container_width=True):
        str_lit.session_state.active_section = "سجل الحضور والانصراف"
        str_lit.rerun()
with r1_c2:
    if str_lit.button("🟢 الحضور والانصراف", use_container_width=True):
        str_lit.session_state.active_section = "تسجيل حضور وانصراف"
        str_lit.rerun()
with r1_c3:
    if str_lit.button("🔵 بيانات الموظفين", use_container_width=True):
        str_lit.session_state.active_section = "سجل الموظفين والأرصدة الشاملة"
        str_lit.rerun()

# الصف الثاني من البطاقات
r2_c1, r2_c2, r2_c3 = str_lit.columns(3)
with r2_c1:
    if str_lit.button("🔘 السلف", use_container_width=True):
        str_lit.session_state.active_section = "تسجيل معاملة مالية"
        str_lit.rerun()
with r2_c2:
    if str_lit.button("🟠 الرواتب والحسابات", use_container_width=True):
        str_lit.session_state.active_section = "كشف الرواتب والمستحقات الشامل"
        str_lit.rerun()
with r2_c3:
    if str_lit.button("🟣 الإجازات", use_container_width=True):
        str_lit.session_state.active_section = "تسجيل طلب إجازة"
        str_lit.rerun()

# الصف الثالث من البطاقات
r3_c1, r3_c2, r3_c3 = str_lit.columns(3)
with r3_c1:
    if str_lit.button("🟩 برمجة النظام", use_container_width=True):
        str_lit.session_state.active_section = "اعدادات الشركة وبياناتها الشاملة"
        str_lit.rerun()
with r3_c2:
    if str_lit.button("🟦 دشبورد التحليلات", use_container_width=True):
        str_lit.session_state.active_section = "لوحة التحكم والمؤشرات"
        str_lit.rerun()
with r3_c3:
    if str_lit.button("🟫 عقود الموظفين", use_container_width=True):
        str_lit.session_state.active_section = "سجل الموظفين والأرصدة الشاملة"
        str_lit.rerun()

str_lit.markdown("<br>", unsafe_allow_html=True)

# -------------------------------------------------------------------------
# بطاقات الـ KPI الإحصائية السفلية (مثل الصورة)
# -------------------------------------------------------------------------
total_emps_kpi = len(filtered_employees)
total_att_kpi = len(filtered_attendance)
total_abs_kpi = len(filtered_attendance[filtered_attendance["الحالة"] == "غياب"]) if not filtered_attendance.empty else 0
total_req_kpi = len(filtered_requests) if not filtered_requests.empty else 0
total_sal_kpi = float(filtered_employees["الراتب الأساسي"].sum()) if not filtered_employees.empty else 0.0
total_adv_kpi = 14000.0 # قيمة افتراضية أو محسوبة
total_contracts_end = 8

kpi_c1, kpi_c2, kpi_c3, kpi_c4 = str_lit.columns(4)
with kpi_c1:
    str_lit.markdown(f'<div class="kpi-card-box"><div class="kpi-card-title">عدد أيام الإجازات</div><div class="kpi-card-val">{total_req_kpi}</div><div style="font-size:9px; color:#64748B;">KPI 📈</div></div>', unsafe_allow_html=True)
with kpi_c2:
    str_lit.markdown(f'<div class="kpi-card-box"><div class="kpi-card-title">عدد أيام الغياب</div><div class="kpi-card-val">{total_abs_kpi}</div><div style="font-size:9px; color:#64748B;">KPI 📉</div></div>', unsafe_allow_html=True)
with kpi_c3:
    str_lit.markdown(f'<div class="kpi-card-box"><div class="kpi-card-title">الموظفون المتواجدون حالياً</div><div class="kpi-card-val">{total_att_kpi}</div><div style="font-size:9px; color:#10B981;">KPI 📈</div></div>', unsafe_allow_html=True)
with kpi_c4:
    str_lit.markdown(f'<div class="kpi-card-box"><div class="kpi-card-title">إجمالي الموظفين</div><div class="kpi-card-val">{total_emps_kpi}</div><div style="font-size:9px; color:#64748B;">KPI 📉</div></div>', unsafe_allow_html=True)

kpi_c5, kpi_c6, kpi_c7, kpi_c8 = str_lit.columns(4)
with kpi_c5:
    str_lit.markdown(f'<div class="kpi-card-box"><div class="kpi-card-title">متوسط الرواتب</div><div class="kpi-card-val">{(total_sal_kpi/total_emps_kpi if total_emps_kpi>0 else 0):,.0f}</div><div style="font-size:9px; color:#10B981;">KPI 📈</div></div>', unsafe_allow_html=True)
with kpi_c6:
    str_lit.markdown(f'<div class="kpi-card-box"><div class="kpi-card-title">انتهاء العقود</div><div class="kpi-card-val">{total_contracts_end}</div><div style="font-size:9px; color:#64748B;">KPI 📉</div></div>', unsafe_allow_html=True)
with kpi_c7:
    str_lit.markdown(f'<div class="kpi-card-box"><div class="kpi-card-title">إجمالي سلف الموظفين</div><div class="kpi-card-val">{total_adv_kpi:,.0f}</div><div style="font-size:9px; color:#10B981;">KPI 📈</div></div>', unsafe_allow_html=True)
with kpi_c8:
    str_lit.markdown(f'<div class="kpi-card-box"><div class="kpi-card-title">إجمالي رواتب الموظفين</div><div class="kpi-card-val">{total_sal_kpi:,.0f}</div><div style="font-size:9px; color:#10B981;">KPI 📈</div></div>', unsafe_allow_html=True)

str_lit.markdown("<hr style='border: 0.5px solid #E2E8F0; margin: 15px 0;'>", unsafe_allow_html=True)

# قائمة منسدلة لاختيار العمليات التنفيذية
if 'active_section' not in str_lit.session_state:
    str_lit.session_state.active_section = "لوحة التحكم والمؤشرات"

operations_list = [
    "لوحة التحكم والمؤشرات",
    "سجل الموظفين والأرصدة الشاملة",
    "إضافة موظف جديد",
    "تسجيل حضور وانصراف",
    "سجل الحضور والانصراف",
    "تسجيل طلب إجازة",
    "سجل طلبات قيد الانتظار",
    "سجل الطلبات المقبولة",
    "تسجيل معاملة مالية",
    "سجل المعاملات المالية والأذونات",
    "كشف الرواتب والمستحقات الشامل",
    "اعدادات الشركة وبياناتها الشاملة"
]

current_idx = operations_list.index(str_lit.session_state.active_section) if str_lit.session_state.active_section in operations_list else 0
selected_op = str_lit.selectbox("📑 اختر قسم أو عملية التنفيذ:", operations_list, index=current_idx)
str_lit.session_state.active_section = selected_op

str_lit.markdown("<hr style='border: 0.5px dashed #E2E8F0; margin: 10px 0;'>", unsafe_allow_html=True)

# تنفيذ العمليات بناءً على الاختيار
if selected_op == "لوحة التحكم والمؤشرات":
    str_lit.markdown("### 📊 لوحة التحكم والتحليلات الشاملة")
    render_printable_table(filtered_employees, "ملخص بيانات الموظفين النشطين")

elif selected_op == "سجل الموظفين والأرصدة الشاملة":
    str_lit.markdown("### 👥 سجل الموظفين والأرصدة")
    render_printable_table(filtered_employees, "سجل الموظفين الشامل")

elif selected_op == "إضافة موظف جديد":
    str_lit.markdown("### ➕ إضافة موظف جديد")
    with str_lit.form("new_emp_form_style"):
        emp_c = str_lit.text_input("كود الموظف", value=f"EMP{len(str_lit.session_state.employees)+1:03d}")
        emp_n = str_lit.text_input("اسم الموظف الرباعي")
        emp_j = str_lit.text_input("الوظيفة")
        emp_b = str_lit.selectbox("الفرع", ["المركز الرئيسي", "فرع الإسكندرية", "فرع الشرم"])
        emp_s = str_lit.number_input("الراتب الأساسي", value=5000.0)
        if str_lit.form_submit_button("حفظ الموظف", use_container_width=True):
            new_row = {"كود الموظف": emp_c, "اسم الموظف": emp_n, "الوظيفة": emp_j, "الفرع": emp_b, "الراتب الأساسي": emp_s, "مسوغات التعيين": "مكتملة", "تاريخ بداية العقد": str(date.today()), "تاريخ نهاية العقد": str(date.today()+timedelta(days=365))}
            str_lit.session_state.employees = pd.concat([str_lit.session_state.employees, pd.DataFrame([new_row])], ignore_index=True)
            auto_save_data()
            str_lit.success("تم حفظ الموظف بنجاح!")

elif selected_op == "سجل الحضور والانصراف":
    render_printable_table(filtered_attendance, "سجل الحضور والانصراف")

elif selected_op == "سجل المعاملات المالية والأذونات":
    render_printable_table(filtered_fin, "سجل السلف والمعاملات المالية")

elif selected_op == "كشف الرواتب والمستحقات الشامل":
    if not filtered_employees.empty:
        df_sal = filtered_employees[["كود الموظف", "اسم الموظف", "الوظيفة", "الفرع", "الراتب الأساسي"]].copy()
        df_sal["الصافي المستحق"] = df_sal["الراتب الأساسي"]
        render_printable_table(df_sal, "كشف الرواتب")

elif selected_op == "اعدادات الشركة وبياناتها الشاملة":
    str_lit.markdown("### ⚙️ إعدادات وبرمجة النظام")
    info = str_lit.session_state.company_info
    with str_lit.form("comp_form"):
        c_name = str_lit.text_input("اسم المنظومة / الشركة", value=info.get("name", ""))
        c_lic = str_lit.text_input("رخصة النظام", value=info.get("license", ""))
        if str_lit.form_submit_button("حفظ الإعدادات", use_container_width=True):
            str_lit.session_state.company_info["name"] = c_name
            str_lit.session_state.company_info["license"] = c_lic
            auto_save_data()
            str_lit.success("تم الحفظ بنجاح!")

str_lit.markdown("<hr style='border: 0.5px solid #E2E8F0; margin: 20px 0;'>", unsafe_allow_html=True)
str_lit.markdown("<p style='text-align: center; color: #64748B; font-size: 11px;'>جميع الحقوق محفوظة © سيستم الموارد البشرية المتكامل - إعداد أ/ إبراهيم محمد علي</p>", unsafe_allow_html=True)