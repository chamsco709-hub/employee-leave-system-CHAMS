import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import altair as alt
from datetime import datetime, date, time, timedelta
import io
import base64
import json
import os

# ضبط اعدادات الصفحة وتفعيل الواجهة الواسعة والانيقة
st.set_page_config(
    page_title="النظام المتكامل لادارة الموارد البشرية والشؤون الادارية",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ملف الترخيص الخاص بهذه النسخة
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
        "name": "شركة الشمس لادارة المنشآت السياحية"
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
# دوال الحفظ والاستعادة التلقائية للبيانات
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
        minute = st.selectbox("دقيقة", list(range(0, 60)), index=default_minute, key=f"{key_prefix}_m")
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
            <button onclick="window.parent.print();" style="
                background: linear-gradient(135deg, #4F46E5 0%, #2563EB 100%);
                color: white;
                padding: 10px 22px;
                border: none;
                border-radius: 10px;
                font-size: 13px;
                font-weight: bold;
                cursor: pointer;
                box-shadow: 0 4px 12px rgba(37, 99, 235, 0.2);
                font-family: 'Segoe UI', Tahoma, sans-serif;
                transition: all 0.3s ease;
            ">
                🖨️ طباعة السجل الحالي بشكل نظيف
            </button>
        </div>
    """, height=50)

# واجهة مستخدم CSS احترافية وعصرية بالكامل
style_css = (
    "<style>"
    "header[data-testid='stHeader'] { visibility: hidden; height: 0px; }"
    "[data-testid='stSidebar'] { display: none !important; width: 0px !important; }"
    "html, body, [class*='css'], .stMarkdown, div, span, p, h1, h2, h3, h4, h5, h6, label {"
    "font-family: 'Segoe UI', 'Arial', sans-serif !important; direction: rtl !important; text-align: right !important; color: #1E293B !important;}"

".block-container { padding-top: 1.5rem !important; padding-bottom: 4rem !important; padding-left: 2rem !important; padding-right: 2rem !important; max-width: 100% !important; background-color: #F8FAFC !important; min-height: 100vh; }"
"div[data-testid='stDateInput'] input, input, textarea, select { background-color: #FFFFFF !important; color: #0F172A !important; font-weight: 500 !important; border-radius: 10px !important; border: 1px solid #CBD5E1 !important; padding: 10px 14px !important; box-shadow: 0 1px 2px rgba(0,0,0,0.02) !important; }"
"label p, .stRadio label, .stSelectbox label, .stTextInput label, .stNumberInput label, .stDateInput label { color: #475569 !important; font-weight: 600 !important; font-size: 13.5px !important; margin-bottom: 6px !important; }"
".glass-header { background: #FFFFFF; border: 1px solid #E2E8F0; padding: 24px 30px; border-radius: 16px; margin-bottom: 24px !important; width: 100%; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); box-sizing: border-box; }"
".header-top-system { text-align: center !important; width: 100%; margin-bottom: 12px; border-bottom: 1px solid #F1F5F9; padding-bottom: 12px; }"
".header-top-system h2 { font-size: 18px !important; font-weight: 700 !important; color: #4F46E5 !important; margin: 0 !important; }"
".header-bottom-content { display: flex; justify-content: space-between; align-items: center; width: 100%; }"
".header-right-info { text-align: right !important; flex: 3.5; }"
".header-left-logo { flex: 1.2; text-align: left !important; display: flex; justify-content: flex-end; align-items: center; }"
".comp-name-txt { font-size: 19px !important; font-weight: 700 !important; margin-bottom: 6px !important; color: #0F172A !important; }"
".comp-info-txt { font-size: 13px !important; margin: 4px 0 !important; color: #64748B !important; line-height: 1.6; }"
".glass-card { background: #FFFFFF; border: 1px solid #E2E8F0; border-right: 5px solid #4F46E5; padding: 20px; border-radius: 12px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.03); text-align: right !important; margin-bottom: 15px; transition: all 0.2s; }"
".glass-card:hover { transform: translateY(-2px); box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05); }"
".glass-card-title { font-size: 13px; color: #64748B; font-weight: 600; margin-bottom: 8px; }"
".glass-card-value { font-size: 26px; color: #0F172A; font-weight: 700; }"
".section-header { font-size: 16px !important; font-weight: 700 !important; color: #4F46E5 !important; border-bottom: 2px solid #E2E8F0; padding-bottom: 8px; margin-top: 24px !important; margin-bottom: 18px !important; }"
"table.custom-table { width: 100%; border-collapse: separate; border-spacing: 0; margin-top: 12px !important; margin-bottom: 24px !important; background-color: #FFFFFF; border-radius: 10px; overflow: hidden; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.02); border: 1px solid #E2E8F0; }"
"table.custom-table th, table.custom-table td { border-bottom: 1px solid #F1F5F9; border-left: 1px solid #F8FAFC; padding: 14px 16px; text-align: right !important; font-size: 13px; }"
"table.custom-table th { background-color: #F8FAFC !important; font-weight: 600; color: #334155 !important; border-bottom: 2px solid #E2E8F0; }"
".entry-form-area { background: #FFFFFF; padding: 24px; border-radius: 14px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.02); border: 1px solid #E2E8F0; margin-bottom: 24px; }"
".stButton button { background-color: #4F46E5 !important; color: white !important; border-radius: 8px !important; border: none !important; padding: 8px 16px !important; font-weight: 600 !important; }"
""
)
st.markdown(style_css, unsafe_allow_html=True)
if 'is_authenticated' not in st.session_state: st.session_state.is_authenticated = False
if 'current_logged_user' not in st.session_state: st.session_state.current_logged_user = ""
if 'current_user_dept' not in st.session_state: st.session_state.current_user_dept = ""
if 'current_user_branch' not in st.session_state: st.session_state.current_user_branch = ""
if 'current_user_role' not in st.session_state: st.session_state.current_user_role = ""
def render_printable_table(df):
if df.empty:
st.info("لا توجد بيانات متاحة للعرض.")
return
html = f'{df.to_html(classes="custom-table", index=False, escape=False)}'
st.markdown(html, unsafe_allow_html=True)
def render_company_header():
info = st.session_state.company_info
logo_html = '🏢 شعار الشركة'
if info.get("logo") is not None:
try:
logo_html = f'<img src="data:image/png;base64,{info.get("logo")}" alt="Logo" style="max-height: 80px; max-width: 160px; object-fit: contain; background: white; border-radius: 8px; padding: 4px; border: 1px solid #E2E8F0;" />'
except Exception:
pass
st.markdown(
f"""


✨ النظام المتكامل لإدارة الموارد البشرية والشؤون الإدارية  |  شركة: {info.get("name", "")}



{info.get("name", "")}
📍 {info.get("address", "")}  |  📋 سجل تجاري: {info.get("cr", "")}  |  🧾 رقم ضريبي: {info.get("tax", "")}  |  🔑 ترخيص: {info.get("license", "")}
📞 {info.get("contact", "")}


{logo_html}



""",
unsafe_allow_html=True
)
if not st.session_state.is_authenticated:
st.markdown(
f"""

🔐 تسجيل الدخول للنظام
{company_display_name}
رخصة التشغيل: {company_license}

""",
unsafe_allow_html=True
)
col_l1, col_l2, col_l3 = st.columns([1, 1.8, 1])
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

عرض هيدر الشركة أولاً

render_company_header()

بطاقات المؤشرات الأربعة مباشرة تحت الهيدر

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
st.markdown(f'👥 إجمالي موظفي الشركة{total_emps}', unsafe_allow_html=True)
with col2:
st.markdown(f'⏳ الطلبات المعلقة{pending_count}', unsafe_allow_html=True)
with col3:
st.markdown(f'✅ الطلبات المقبولة{accepted_count}', unsafe_allow_html=True)
with col4:
total_payroll_est = float(view_employees["الراتب الأساسي"].sum()) if not view_employees.empty and "الراتب الأساسي" in view_employees.columns else 0.0
st.markdown(f'💰 إجمالي الرواتب الأساسية{total_payroll_est:,.0f} ج.م', unsafe_allow_html=True)

تبويبات أفقية للتنقل السريع بين الأقسام الرئيسية

st.markdown("
", unsafe_allow_html=True)
main_menu = st.radio(
"🧭 التنقل السريع بين الأقسام الرئيسية:",
[
"🏠 الشاشة الرئيسية",
"🔍 صندوق البحث الشامل",
"⏱️ الحضور والانصراف",
"💰 المعاملات المالية",
"📝 طلبات الإجازات",
"👥 شؤون الموظفين",
"⚙️ الأدوات والنظام"
],
horizontal=True,
label_visibility="collapsed"
)
st.markdown("", unsafe_allow_html=True)

تحديد الإجراء الفرعي لكل قسم رئيسي

if main_menu == "🏠 الشاشة الرئيسية":
choice = "لوحة المؤشرات والتحكم"
elif main_menu == "🔍 صندوق البحث الشامل":
choice = "محرك البحث المتطور والفلترة"
elif main_menu == "⏱️ الحضور والانصراف":
choice = st.selectbox("حدد الإجراء المطلوب في الحضور والانصراف:", ["تسجيل حضور وانصراف", "سجل الحضور والانصراف", "تعديل أو حذف حركة حضور"])
elif main_menu == "💰 المعاملات المالية":
choice = st.selectbox("حدد الإجراء المطلوب في المعاملات المالية:", ["تسجيل معاملة مالية", "سجل المعاملات المالية", "تعديل أو حذف معاملة مالية"])
elif main_menu == "📝 طلبات الإجازات":
choice = st.selectbox("حدد الإجراء المطلوب في الإجازات:", ["تسجيل طلب إجازة جديد", "سجل طلبات قيد الانتظار", "سجل الطلبات المقبولة", "سجل الطلبات المرفوضة", "تعديل أو حذف طلب إجازة"])
elif main_menu == "👥 شؤون الموظفين":
choice = st.selectbox("حدد الإجراء المطلوب في شؤون الموظفين:", ["إضافة موظف جديد", "سجل الموظفين والأرصدة", "تعديل أو حذف موظف"])
elif main_menu == "⚙️ الأدوات والنظام":
choice = st.selectbox("حدد الإجراء المطلوب في الأدوات والنظام:", ["إدارة المستخدمين والصلاحيات", "كشف الرواتب والمستحقات", "طباعة التقارير", "إعدادات الشركة", "تصدير وتحميل Excel", "نسخة احتياطية واستعادة", "مسح البيانات"])

صندوق البحث المتطور والشامل

if main_menu == "🔍 صندوق البحث الشامل" or choice == "محرك البحث المتطور والفلترة":
st.markdown(f'🔍 صندوق البحث المتطور والشامل في قواعد بيانات الشركة', unsafe_allow_html=True)
st.markdown('', unsafe_allow_html=True)
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
st.markdown('', unsafe_allow_html=True)
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

الشاشة الرئيسية

elif choice == "لوحة المؤشرات والتحكم" or choice == "الشاشة الرئيسية":
if not pending_requests.empty:
st.markdown(f'⏳ اتخاذ القرار بشأن الطلبات المعلقة ({pending_count} طلب)', unsafe_allow_html=True)
render_printable_table(pending_requests)
st.markdown('', unsafe_allow_html=True)
col_dec1, col_dec2, col_dec3 = st.columns(3)
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
st.markdown('', unsafe_allow_html=True)
st.markdown(f'📊 الرسم البياني التحليلي لإحصائيات وأرصدة الموظفين', unsafe_allow_html=True)
st.markdown('', unsafe_allow_html=True)
col_f_type, col_f_val, col_p_btn = st.columns(3)
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


🖨️ طباعة المخطط


""", height=45)
st.markdown('', unsafe_allow_html=True)
if not filtered_chart_emps.empty:
st.markdown(f'📌 {chart_subtitle}', unsafe_allow_html=True)
chart_df_melted = filtered_chart_emps.melt(
id_vars=["اسم الموظف"],
value_vars=["رصيد سنوي (إجمالي)", "سنوي مستهلك", "سنوي متبقي"],
var_name="نوع الرصيد",
value_name="عدد الأيام"
)
c1 = alt.Chart(chart_df_melted).mark_bar(color='#4F46E5').encode(
x=alt.X('اسم الموظف:N', title='الموظف', axis=alt.Axis(labelAngle=0, labelColor='#1E293B', titleColor='#4F46E5')),
y=alt.Y('عدد الأيام:Q', title='عدد الأيام', axis=alt.Axis(labelColor='#1E293B', titleColor='#4F46E5')),
color=alt.Color('نوع الرصيد:N', legend=alt.Legend(
orient='bottom',
direction='horizontal',
title='نوع الرصيد:',
titleColor='#4F46E5',
labelColor='#1E293B',
titleAnchor='middle'
)),
tooltip=['اسم الموظف', 'نوع الرصيد', 'عدد الأيام']
).properties(
height=360,
background='transparent'
).configure_view(
fill=None,
stroke=None
)
st.altair_chart(c1, use_container_width=True)
else:
st.info("لا توجد بيانات متاحة للمخطط حسب الفلتر المختار.")
st.markdown(f'📋 أرصدة إجازات موظفي الشركة: {company_display_name}', unsafe_allow_html=True)
render_printable_table(view_employees)
elif choice == "تسجيل حضور وانصراف":
st.subheader("⏱️ 1. تسجيل حركة حضور / انصراف جديدة")
emp_names = st.session_state.employees["اسم الموظف"].tolist()
if not emp_names:
st.warning("لا توجد موظفون متاحون.")
else:
st.markdown('', unsafe_allow_html=True)
with st.form("attendance_record_form"):
col_f1, col_f2, col_f3 = st.columns(3)
with col_f1:
selected_emp = st.selectbox("اختر الموظف", emp_names)
emp_data = st.session_state.employees[st.session_state.employees["اسم الموظف"] == selected_emp].iloc[0]
with col_f2:
att_date = st.date_input("تاريخ اليوم", value=date.today())
with col_f3:
att_status = st.selectbox("حالة اليوم", ["حضور", "إجازة أسبوعية", "إجازة سنوية", "إجازة مرضية", "غياب", "إجازة رسمية", "مأمورية"])
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
morning_delay, early_leave, overtime_after, early_arrival, late_departure = 0, 0, 0, 0, 0
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
new_att = {
"التاريخ": str(att_date), "كود الموظف": emp_code, "اسم الموظف": selected_emp, "الفرع": emp_branch,
"بداية العمل الرسمية": t_official_start_str, "نهاية العمل الرسمية": t_official_end_str,
"وقت الحضور الفعلي": t_in_str, "وقت الانصراف الفعلي": t_out_str, "الحالة": att_status,
"التأخير الصباحي (دقيقة)": morning_delay, "انصراف مبكر (دقيقة)": early_leave,
"إضافي بعد العمل (دقيقة)": overtime_after, "حضور مبكر (دقيقة)": early_arrival,
"خروج متأخر (دقيقة)": late_departure, "دقائق التأخير": morning_delay
}
st.session_state.attendance = pd.concat([st.session_state.attendance, pd.DataFrame([new_att])], ignore_index=True)
auto_save_data()
st.success("تم تسجيل حركة الحضور والانصراف بنجاح!")
st.rerun()
st.markdown('', unsafe_allow_html=True)
elif choice == "سجل الحضور والانصراف":
col_t1, col_t2 = st.columns(2)
with col_t1: st.subheader("⏱️ 2. سجل الحضور والانصراف العام")
with col_t2: render_print_button()
render_printable_table(st.session_state.attendance)
elif choice == "تعديل أو حذف حركة حضور":
st.subheader("⏱️ 3. تعديل أو حذف حركة تسجيل حضور وانصراف")
if st.session_state.attendance.empty:
st.info("لا توجد حركات حضور مسجلة حالياً.")
else:
att_records = [f"الموظف: {row['اسم الموظف']} | التاريخ: {row['التاريخ']} | الحالة: {row['الحالة']}" for _, row in st.session_state.attendance.iterrows()]
selected_att_label = st.selectbox("اختر الحركة المراد تعديلها أو حذفها:", att_records)
selected_att_idx = att_records.index(selected_att_label)
row_to_edit = st.session_state.attendance.loc[selected_att_idx]
st.markdown('', unsafe_allow_html=True)
with st.form("edit_attendance_full_form"):
st.markdown(f"تعديل تفاصيل حركة الحضور للموظف: {row_to_edit['اسم الموظف']} (بتاريخ {row_to_edit['التاريخ']})")
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
st.markdown('', unsafe_allow_html=True)
elif choice == "تسجيل معاملة مالية":
st.subheader("💰 1. إضافة معاملة مالية جديدة")
emp_names = st.session_state.employees["اسم الموظف"].tolist()
if not emp_names:
st.warning("لا توجد موظفون مسجلون.")
else:
st.markdown('', unsafe_allow_html=True)
with st.form("financial_transaction_form"):
col_m1, col_m2, col_m3 = st.columns(3)
with col_m1: selected_emp_f = st.selectbox("اختر الموظف للمعاملة", emp_names)
with col_m2: trans_type = st.selectbox("نوع المعاملة", ["سلفة", "جزاء (خصم)", "مكافأة (إضافي)", "بدلات (إضافي مستحق)", "إضافي (ساعات عمل إضافية)"])
with col_m3: trans_date = st.date_input("تاريخ المعاملة المالية", value=date.today())
col_m4, col_m5 = st.columns(2)
with col_m4: amount = st.number_input("المبلغ / القيمة (جنيه)", min_value=0.0, value=100.0, step=50.0)
with col_m5: reason = st.text_input("البيان / السبب التفصيلي للمعاملة")
if st.form_submit_button("💾 حفظ المعاملة المالية وتحديث الحسابات", use_container_width=True):
emp_data = st.session_state.employees[st.session_state.employees["اسم الموظف"] == selected_emp_f].iloc[0]
new_trans = {
"التاريخ": str(trans_date), "كود الموظف": emp_data["كود الموظف"], "اسم الموظف": selected_emp_f,
"الفرع": emp_data["الفرع"], "النوع": trans_type, "المبلغ / القيمة": amount, "البيان / السبب": reason
}
st.session_state.financial_transactions = pd.concat([st.session_state.financial_transactions, pd.DataFrame([new_trans])], ignore_index=True)
auto_save_data()
st.success("تم تسجيل المعاملة المالية بنجاح!")
st.rerun()
st.markdown('', unsafe_allow_html=True)
elif choice == "سجل المعاملات المالية":
col_t1, col_t2 = st.columns(2)
with col_t1: st.subheader("💰 2. سجل المعاملات المالية والسلف العام")
with col_t2: render_print_button()
render_printable_table(st.session_state.financial_transactions)
elif choice == "تعديل أو حذف معاملة مالية":
st.subheader("💰 3. تعديل أو حذف معاملة مالية")
if st.session_state.financial_transactions.empty:
st.info("لا توجد معاملات مالية مسجلة.")
else:
fin_records = [f"الموظف: {row['اسم الموظف']} | النوع: {row['النوع']} | المبلغ: {row['المبلغ / القيمة']} | التاريخ: {row['التاريخ']}" for _, row in st.session_state.financial_transactions.iterrows()]
selected_fin_label = st.selectbox("اختر المعاملة المراد تعديلها أو حذفها:", fin_records)
selected_fin_idx = fin_records.index(selected_fin_label)
fin_to_edit = st.session_state.financial_transactions.loc[selected_fin_idx]
st.markdown('', unsafe_allow_html=True)
with st.form("edit_fin_form"):
st.markdown(f"تعديل المعاملة المالية للموظف: {fin_to_edit['اسم الموظف']}")
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
st.markdown('', unsafe_allow_html=True)
elif choice == "تسجيل طلب إجازة جديد":
st.subheader(f"📝 1. تقديم طلب إجازة جديد - {company_display_name}")
emp_list = st.session_state.employees["اسم الموظف"].dropna().astype(str).tolist()
if not emp_list:
st.warning("لا توجد موظفون متاحون.")
else:
st.markdown('', unsafe_allow_html=True)
with st.form("leave_form"):
emp_name = st.selectbox("اسم الموظف", emp_list)
leave_type = st.selectbox("نوع الإجازة", ["إجازة سنوية (Annual)", "إجازة أسبوعية / عارضة", "إجازة مرضية (Sick Leave)", "إجازة رسمية", "بدون أجر"])
col_d1, col_d2 = st.columns(2)
with col_d1: start_date = st.date_input("من تاريخ")
with col_d2: end_date = st.date_input("إلى تاريخ")
reason = st.text_area("سبب الإجازة / ملاحظات إضافية")
if st.form_submit_button("إرسال طلب الإجازة للمراجعة", use_container_width=True):
days = (end_date - start_date).days + 1
if days <= 0:
st.error("خطأ: تاريخ النهاية يجب أن يكون بعد تاريخ البداية!")
else:
emp_row = st.session_state.employees[st.session_state.employees["اسم الموظف"] == emp_name].iloc[0]
new_req = {
"رقم الطلب": int(st.session_state.requests["رقم الطلب"].max() + 1) if not st.session_state.requests.empty else 101,
"كود الموظف": emp_row["كود الموظف"], "اسم الموظف": emp_name, "الوظيفة": emp_row["الوظيفة"], "الفرع": emp_row["الفرع"],
"نوع الإجازة": leave_type, "من تاريخ": str(start_date), "إلى تاريخ": str(end_date), "عدد الأيام": days, "السبب": reason, "الحالة": "قيد الانتظار"
}
st.session_state.requests = pd.concat([st.session_state.requests, pd.DataFrame([new_req])], ignore_index=True)
auto_save_data()
st.success("تم تقديم طلب الإجازة بنجاح!")
st.rerun()
st.markdown('', unsafe_allow_html=True)
elif choice == "سجل طلبات قيد الانتظار":
col_t1, col_t2 = st.columns(2)
with col_t1: st.subheader("⏳ 2. سجل طلبات الإجازات قيد الانتظار")
with col_t2: render_print_button()
render_printable_table(st.session_state.requests[st.session_state.requests["الحالة"] == "قيد الانتظار"] if not st.session_state.requests.empty else pd.DataFrame())
elif choice == "سجل الطلبات المقبولة":
col_t1, col_t2 = st.columns(2)
with col_t1: st.subheader("✅ 3. سجل طلبات الإجازات المقبولة")
with col_t2: render_print_button()
render_printable_table(st.session_state.requests[st.session_state.requests["الحالة"] == "مقبول"] if not st.session_state.requests.empty else pd.DataFrame())
elif choice == "سجل الطلبات المرفوضة":
col_t1, col_t2 = st.columns(2)
with col_t1: st.subheader("🗑️ 4. سجل طلبات الإجازات المرفوضة")
with col_t2: render_print_button()
render_printable_table(st.session_state.requests[st.session_state.requests["الحالة"] == "مرفوض"] if not st.session_state.requests.empty else pd.DataFrame())
elif choice == "تعديل أو حذف طلب إجازة":
st.subheader("📝 5. تعديل أو حذف طلب إجازة")
if st.session_state.requests.empty:
st.info("لا توجد طلبات إجازات مسجلة.")
else:
req_records = [f"طلب رقم #{row['رقم الطلب']} - الموظف: {row['اسم الموظف']} ({row['نوع الإجازة']}) - الحالة: {row['الحالة']}" for _, row in st.session_state.requests.iterrows()]
selected_req_label = st.selectbox("اختر الطلب المراد تعديله أو حذفه:", req_records)
selected_req_idx = req_records.index(selected_req_label)
req_to_edit = st.session_state.requests.loc[selected_req_idx]
st.markdown('', unsafe_allow_html=True)
with st.form("edit_req_form"):
st.markdown(f"تعديل طلب الإجازة رقم #{req_to_edit['رقم الطلب']} للموظف: {req_to_edit['اسم الموظف']}")
ed_req_emp = st.text_input("اسم الموظف", value=str(req_to
_edit["اسم الموظف"]))
ed_req_branch = st.text_input("الفرع", value=str(req_to_edit["الفرع"]))
ed_req_type = st.text_input("نوع الإجازة", value=str(req_to_edit["نوع الإجازة"]))
status_list = ["قيد الانتظار", "مقبول", "مرفوض"]
current_st_idx = status_list.index(req_to_edit["الحالة"]) if req_to_edit["الحالة"] in status_list else 0
ed_req_status = st.selectbox("حالة الطلب", status_list, index=current_st_idx)
ed_req_from = st.text_input("من تاريخ", value=str(req_to_edit["من تاريخ"]))
ed_req_to = st.text_input("إلى تاريخ", value=str(req_to_edit["إلى تاريخ"]))
ed_req_days = st.number_input("عدد الأيام", min_value=1, value=int(req_to_edit["عدد الأيام"]))
ed_req_reason = st.text_area("سبب الإجازة", value=str(req_to_edit.get("السبب", "")))
