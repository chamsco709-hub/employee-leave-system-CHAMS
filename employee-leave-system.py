import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import altair as alt
from datetime import datetime, date, time, timedelta
import io
import base64
import json
import os

# ضبط إعدادات الصفحة وتفعيل الواجهة الواسعة والأنيقة
st.set_page_config(
    page_title="النظام المتكامل لإدارة الموارد البشرية والشؤون الإدارية",
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

# 🎨 واجهة مستخدم CSS احترافية وعصرية بالكامل (Clean Enterprise UI)
st.markdown("""
    <style>
    header[data-testid="stHeader"] { visibility: hidden; height: 0px; }
    [data-testid="stSidebar"] { display: none !important; width: 0px !important; }
    
    html, body, [class*="css"], .stMarkdown, div, span, p, h1, h2, h3, h4, h5, h6, label {
        font-family: 'Segoe UI', 'Arial', sans-serif !important;
        direction: rtl !important;
        text-align: right !important;
        color: #1E293B !important;
    }
    
    .block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 4rem !important;
