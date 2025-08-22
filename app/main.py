import streamlit as st
import os
import sqlite3
from db_init import init_db
from utils import get_db_connection
from tenant_form import show_tenant_form
from admin_dashboard import show_admin_dashboard, show_tenant_management
from vendor_manager import show_vendor_manager
from uploader import show_uploader
from calendar_integration import show_calendar_view
from ai_agent import ensure_ai_ready

# 设置页面配置
st.set_page_config(
    page_title="AutoMaintain - Maintenance Management System",
    page_icon="🔧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 初始化数据库
if not os.path.exists("./automaintain.db"):
    init_db()

# 设置环境变量
os.environ["AUTOMAINTAIN_DB_PATH"] = "./automaintain.db"
os.environ["CHROMA_DB_DIR"] = "./chroma_db"

# 检查AI是否就绪
ai_ready = ensure_ai_ready()

# 侧边栏导航
st.sidebar.title("🔧 AutoMaintain")
st.sidebar.markdown("---")

# 用户选择界面
app_mode = st.sidebar.selectbox(
    "Select Interface",
    ["Tenant Request Form", "Admin Dashboard", "Vendor Management", "Knowledge Base", "Calendar View"]
)

st.sidebar.markdown("---")
st.sidebar.info("AutoMaintain System v1.0")

# 显示选定的界面
if app_mode == "Tenant Request Form":
    show_tenant_form()
elif app_mode == "Admin Dashboard":
    show_admin_dashboard()
    show_tenant_management()
elif app_mode == "Vendor Management":
    show_vendor_manager()
elif app_mode == "Knowledge Base":
    show_uploader()
elif app_mode == "Calendar View":
    show_calendar_view()