import streamlit as st
from datetime import datetime
import sqlite3
from app.utils import get_db_path
from app.ai_agent import classify_issue, recommend_solutions
from app.admin_dashboard import show_admin_dashboard
from app.uploader import show_uploader
from app.utils import get_chroma_client


# 初始化 session_state
if "language" not in st.session_state:
    st.session_state.language = "en"  # 默认英语

# 翻译字典
translations = {
    "en": {
        "title": "Automated Maintenance Request Manager",
        "tenant_request": "Tenant Request Form",
        "admin_dashboard": "Admin Dashboard",
        "knowledge_base": "Knowledge Base",
        "submit_request": "Submit a Request",
        "tenant_name": "Tenant Name",
        "email": "Email",
        "desc": "Describe the issue",
        "submit": "Submit",
        "success": "Request submitted! Category={category}, Priority={priority}",
        "possible_solutions": "Possible solutions:",
    },
    "zh": {
        "title": "自动化报修管理系统",
        "tenant_request": "租户报修表单",
        "admin_dashboard": "管理员控制台",
        "knowledge_base": "知识库",
        "submit_request": "提交报修",
        "tenant_name": "租户姓名",
        "email": "邮箱",
        "desc": "问题描述",
        "submit": "提交",
        "success": "报修已提交！类别={category}, 优先级={priority}",
        "possible_solutions": "可能的解决方案：",
    }
}

# 语言切换按钮
col1, col2 = st.columns(2)
if col1.button("English"):
    st.session_state.language = "en"
if col2.button("中文"):
    st.session_state.language = "zh"

def main():
    lang = st.session_state.language
    st.title(translations[lang]["title"])

    page = st.sidebar.radio(
        "Navigate",
        [translations[lang]["tenant_request"], translations[lang]["admin_dashboard"], translations[lang]["knowledge_base"]]
    )

    if page == translations[lang]["tenant_request"]:
        st.subheader(translations[lang]["submit_request"])
        tenant = st.text_input(translations[lang]["tenant_name"])
        email = st.text_input(translations[lang]["email"])
        desc = st.text_area(translations[lang]["desc"])
        if st.button(translations[lang]["submit"]):
            category, priority = classify_issue(desc)
            conn = sqlite3.connect(get_db_path())
            c = conn.cursor()
            c.execute("INSERT INTO tenants(first_name,email,created_at) VALUES(?,?,?)", (tenant, email, datetime.now().isoformat()))
            tid = c.lastrowid
            c.execute("""INSERT INTO maintenance_requests(tenant_id,category,description,priority,status,created_at)
                      VALUES(?,?,?,?,?,?)""", (tid, category, desc, priority, "pending", datetime.now().isoformat()))
            conn.commit()
            conn.close()
            st.success(translations[lang]["success"].format(category=category, priority=priority))

            collection = get_chroma_client()
            recs = recommend_solutions(desc, collection)
            if recs:
                st.write(translations[lang]["possible_solutions"])
                for r in recs:
                    st.write(f"- {r['title']}: {r['snippet']}")

    elif page == translations[lang]["admin_dashboard"]:
        show_admin_dashboard()
    elif page == translations[lang]["knowledge_base"]:
        show_uploader()

if __name__=="__main__":
    main()
