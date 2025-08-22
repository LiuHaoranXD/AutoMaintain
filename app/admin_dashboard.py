import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils import get_db_connection, send_email
import sqlite3
from datetime import datetime, timedelta

def show_admin_dashboard():
    st.header("📊 Admin Dashboard")
    st.info("Comprehensive overview of maintenance requests and system performance")

    try:
        conn = get_db_connection()

        # Key Metrics
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            total_requests = pd.read_sql("SELECT COUNT(*) as count FROM maintenance_requests", conn).iloc[0]['count']
            st.metric("Total Requests", total_requests)

        with col2:
            pending_requests = pd.read_sql("SELECT COUNT(*) as count FROM maintenance_requests WHERE status='Pending'", conn).iloc[0]['count']
            st.metric("Pending Requests", pending_requests)

        with col3:
            avg_cost = pd.read_sql("SELECT AVG(estimated_cost) as avg FROM maintenance_requests WHERE estimated_cost IS NOT NULL", conn).iloc[0]['avg']
            st.metric("Avg Cost", f"${avg_cost:.2f}" if avg_cost else "$0")

        with col4:
            total_tenants = pd.read_sql("SELECT COUNT(*) as count FROM tenants", conn).iloc[0]['count']
            st.metric("Total Tenants", total_tenants)

        # Request Management
        st.subheader("🎫 Request Management")

        # Filters
        col1, col2, col3 = st.columns(3)
        with col1:
            status_filter = st.selectbox("Filter by Status", ["All", "Pending", "In Progress", "Resolved", "Rejected"])
        with col2:
            category_filter = st.selectbox("Filter by Category", ["All", "Plumbing", "Electrical", "HVAC", "Structural", "Appliance", "Other"])
        with col3:
            priority_filter = st.selectbox("Filter by Priority", ["All", "High", "Medium", "Low"])

        # Build query - Fix: Use request_id instead of id
        query = '''
        SELECT r.request_id, r.created_at, r.category, r.priority, r.status, r.urgency,
               r.description, r.estimated_cost, t.first_name, t.last_name, t.unit_number,
               v.company_name as vendor_name
        FROM maintenance_requests r
        LEFT JOIN tenants t ON r.tenant_id = t.tenant_id
        LEFT JOIN vendors v ON r.assigned_vendor_id = v.vendor_id
        WHERE 1=1
        '''

        params = []
        if status_filter != "All":
            query += " AND r.status = ?"
            params.append(status_filter)
        if category_filter != "All":
            query += " AND r.category = ?"
            params.append(category_filter)
        if priority_filter != "All":
            query += " AND r.priority = ?"
            params.append(priority_filter)

        query += " ORDER BY r.created_at DESC"

        requests_df = pd.read_sql(query, conn, params=params)

        if not requests_df.empty:
            # Display requests
            for _, request in requests_df.iterrows():
                with st.expander(f"Request #{request['request_id']} - {request['category']} ({request['status']})"):
                    col1, col2 = st.columns([2, 1])
                    with col1:
                        st.write(f"**Tenant:** {request['first_name']} {request['last_name']} - {request['unit_number']}")
                        st.write(f"**Description:** {request['description']}")
                        st.write(f"**Created:** {request['created_at']}")
                        if request['vendor_name']:
                            st.write(f"**Assigned Vendor:** {request['vendor_name']}")

                    with col2:
                        st.write(f"**Priority:** {request['priority']}")
                        st.write(f"**Urgency:** {request['urgency']}")
                        if request['estimated_cost']:
                            st.write(f"**Est. Cost:** ${request['estimated_cost']:.2f}")

                        # Status update
                        new_status = st.selectbox(
                            "Update Status",
                            ["Pending", "In Progress", "Resolved", "Rejected"],
                            index=["Pending", "In Progress", "Resolved", "Rejected"].index(request['status']),
                            key=f"status_{request['request_id']}"
                        )

                        if st.button("Update", key=f"update_{request['request_id']}"):
                            try:
                                c = conn.cursor()
                                c.execute(
                                    "UPDATE maintenance_requests SET status=? WHERE request_id=?",
                                    (new_status, request['request_id'])
                                )
                                conn.commit()
                                st.success("Status updated!")
                                st.rerun()  # Fix: Use st.rerun() instead of st.experimental_rerun()
                            except Exception as e:
                                st.error(f"Update failed: {str(e)}")
        else:
            st.info("No requests found matching the current filters.")

        # Analytics
        st.subheader("📈 Analytics")

        # Request status distribution
        status_df = pd.read_sql("SELECT status, COUNT(*) as count FROM maintenance_requests GROUP BY status", conn)
        if not status_df.empty:
            fig1 = px.pie(status_df, values='count', names='status', title='Request Status Distribution')
            st.plotly_chart(fig1, use_container_width=True)

        # Category breakdown
        category_df = pd.read_sql("SELECT category, COUNT(*) as count FROM maintenance_requests GROUP BY category", conn)
        if not category_df.empty:
            fig2 = px.bar(category_df, x='category', y='count', title='Requests by Category')
            st.plotly_chart(fig2, use_container_width=True)

        # Monthly trends
        try:
            monthly_df = pd.read_sql('''
                SELECT strftime('%Y-%m', created_at) as month, COUNT(*) as count
                FROM maintenance_requests
                WHERE created_at >= date('now', '-12 months')
                GROUP BY strftime('%Y-%m', created_at)
                ORDER BY month
            ''', conn)
            if not monthly_df.empty:
                fig3 = px.line(monthly_df, x='month', y='count', title='Monthly Request Trends')
                st.plotly_chart(fig3, use_container_width=True)
        except Exception as e:
            st.warning(f"Could not load monthly trends: {str(e)}")

        # Cost analysis
        try:
            cost_df = pd.read_sql('''
                SELECT category, AVG(estimated_cost) as avg_cost, COUNT(*) as count
                FROM maintenance_requests
                WHERE estimated_cost IS NOT NULL
                GROUP BY category
                HAVING count >= 3
                ORDER BY avg_cost DESC
            ''', conn)
            if not cost_df.empty:
                fig4 = px.bar(cost_df, x='category', y='avg_cost', title='Average Cost by Category')
                st.plotly_chart(fig4, use_container_width=True)
        except Exception as e:
            st.warning(f"Could not load cost analysis: {str(e)}")

        conn.close()

    except Exception as e:
        st.error(f"❌ Error loading dashboard: {str(e)}")

def show_tenant_management():
    st.subheader("👥 Tenant Management")

    try:
        conn = get_db_connection()
        tenants_df = pd.read_sql("SELECT * FROM tenants ORDER BY created_at DESC", conn)

        if not tenants_df.empty:
            st.dataframe(tenants_df, use_container_width=True)
        else:
            st.info("No tenants found.")

        conn.close()
    except Exception as e:
        st.error(f"Error loading tenants: {str(e)}")