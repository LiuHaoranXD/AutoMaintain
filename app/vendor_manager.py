import streamlit as st
import sqlite3
import pandas as pd
from utils import get_db_path, validate_email, get_db_connection
from datetime import datetime

def show_vendor_manager():
    st.header("👥 Vendor Management")
    st.info("Manage service providers and their specializations")

    try:
        conn = get_db_connection()

        # Display existing vendors
        vendors_df = pd.read_sql("SELECT * FROM vendors ORDER BY created_at DESC", conn)

        if not vendors_df.empty:
            st.subheader("📋 Current Vendors")

            # 显示供应商表格
            display_df = vendors_df[['company_name', 'contact_person', 'email', 'specialization', 'hourly_rate', 'rating']].copy()
            display_df['hourly_rate'] = display_df['hourly_rate'].apply(lambda x: f"${x:.2f}" if pd.notna(x) else "N/A")
            display_df['rating'] = display_df['rating'].apply(lambda x: f"{x:.1f}/5.0" if pd.notna(x) else "N/A")

            st.dataframe(display_df, use_container_width=True)

            # 供应商绩效统计
            try:
                performance_df = pd.read_sql("""
                    SELECT v.company_name, v.specialization,
                           COUNT(r.request_id) as total_requests,
                           SUM(CASE WHEN r.status = 'Resolved' THEN 1 ELSE 0 END) as resolved_requests,
                           AVG(r.estimated_cost) as avg_cost,
                           v.rating
                    FROM vendors v
                    LEFT JOIN maintenance_requests r ON v.vendor_id = r.assigned_vendor_id
                    GROUP BY v.vendor_id, v.company_name, v.specialization, v.rating
                    ORDER BY total_requests DESC
                """, conn)

                if not performance_df.empty and performance_df['total_requests'].sum() > 0:
                    st.subheader("📊 Vendor Performance")
                    performance_df['success_rate'] = (performance_df['resolved_requests'] / performance_df['total_requests'] * 100).fillna(0).round(1)
                    performance_df['avg_cost'] = performance_df['avg_cost'].fillna(0).round(2)

                    display_perf = performance_df[['company_name', 'specialization', 'total_requests', 'success_rate', 'avg_cost', 'rating']].copy()
                    display_perf.columns = ['Company', 'Specialization', 'Total Jobs', 'Success Rate (%)', 'Avg Cost ($)', 'Rating']
                    st.dataframe(display_perf, use_container_width=True)
            except Exception as e:
                st.warning(f"Could not load vendor performance: {str(e)}")
        else:
            st.info("📭 No vendors found in database")

        # Add new vendor form
        st.subheader("➕ Add New Vendor")
        with st.form("vendor_form"):
            col1, col2 = st.columns(2)
            with col1:
                company_name = st.text_input("Company Name *", placeholder="ABC Plumbing")
                contact_person = st.text_input("Contact Person", placeholder="John Doe")
                email = st.text_input("Email", placeholder="contact@abcplumbing.com")

            with col2:
                phone = st.text_input("Phone", placeholder="555-0123")
                specialization = st.selectbox("Specialization",
                    ["Plumbing", "Electrical", "HVAC", "Structural", "Appliance", "General"])
                hourly_rate = st.number_input("Hourly Rate ($)", min_value=0.0, value=75.0, step=5.0)

            rating = st.slider("Initial Rating", min_value=1.0, max_value=5.0, value=4.0, step=0.1)

            submitted = st.form_submit_button("🚀 Add Vendor", use_container_width=True)

            if submitted:
                if not company_name:
                    st.error("❌ Company name is required")
                elif email and not validate_email(email):
                    st.error("❌ Please enter a valid email address")
                else:
                    try:
                        c = conn.cursor()

                        # 检查是否已存在同名公司
                        c.execute("SELECT COUNT(*) FROM vendors WHERE company_name = ?", (company_name,))
                        if c.fetchone()[0] > 0:
                            st.error(f"❌ Company '{company_name}' already exists")
                        else:
                            c.execute(
                                "INSERT INTO vendors (company_name, contact_person, email, phone, specialization, hourly_rate, rating, created_at) VALUES (?,?,?,?,?,?,?,?)",
                                (company_name, contact_person, email, phone, specialization, hourly_rate, rating, datetime.now().isoformat())
                            )
                            conn.commit()
                            st.success(f"✅ Added vendor: {company_name}")
                            st.rerun()
                    except sqlite3.Error as e:
                        st.error(f"❌ Database error: {str(e)}")

        conn.close()
    except Exception as e:
        st.error(f"❌ Error in vendor management: {str(e)}")