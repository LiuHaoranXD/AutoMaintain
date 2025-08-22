import streamlit as st
import pandas as pd
from utils import get_db_connection, parse_datetime, format_datetime
import plotly.express as px
from datetime import datetime, timedelta
import calendar

def show_calendar_view():
    st.header("📅 Calendar Integration")
    st.info("View and manage scheduled maintenance appointments")

    try:
        conn = get_db_connection()

        # 修复: 使用 request_id 而不是 id
        scheduled_df = pd.read_sql('''
            SELECT r.request_id, r.scheduled_date, r.category, r.priority, r.status,
                   r.description, t.first_name, t.last_name, t.unit_number,
                   v.company_name as vendor_name
            FROM maintenance_requests r
            LEFT JOIN tenants t ON r.tenant_id = t.tenant_id
            LEFT JOIN vendors v ON r.assigned_vendor_id = v.vendor_id
            WHERE r.scheduled_date IS NOT NULL
            ORDER BY r.scheduled_date
        ''', conn)

        if not scheduled_df.empty:
            # 修复: 使用通用日期时间解析
            scheduled_df['scheduled_date'] = scheduled_df['scheduled_date'].apply(parse_datetime)
            scheduled_df = scheduled_df.dropna(subset=['scheduled_date'])  # 移除无法解析的日期
            
            scheduled_df['date'] = scheduled_df['scheduled_date'].dt.date

            # 其余代码保持不变...

            # Calendar view options
            view_option = st.selectbox("Calendar View", ["Weekly", "Monthly", "List View"])

            if view_option == "List View":
                st.subheader("📋 Upcoming Appointments")
                today = datetime.now().date()
                upcoming = scheduled_df[scheduled_df['date'] >= today].head(20)

                for _, appt in upcoming.iterrows():
                    with st.container():
                        col1, col2, col3 = st.columns([2, 1, 1])
                        with col1:
                            st.write(f"**{appt['scheduled_date'].strftime('%Y-%m-%d %H:%M')}**")
                            st.write(f"{appt['first_name']} {appt['last_name']} - {appt['unit_number']}")
                            st.write(f"*{appt['category']} - {appt['description'][:50]}...*")
                        with col2:
                            st.write(f"Priority: {appt['priority']}")
                            st.write(f"Status: {appt['status']}")
                        with col3:
                            if appt['vendor_name']:
                                st.write(f"Vendor: {appt['vendor_name']}")
                        st.markdown("---")

            elif view_option == "Weekly":
                st.subheader("📅 Weekly Schedule")
                today = datetime.now().date()
                start_of_week = today - timedelta(days=today.weekday())
                end_of_week = start_of_week + timedelta(days=6)

                week_data = scheduled_df[
                    (scheduled_df['date'] >= start_of_week) &
                    (scheduled_df['date'] <= end_of_week)
                ]

                if not week_data.empty:
                    for i in range(7):
                        day = start_of_week + timedelta(days=i)
                        day_name = calendar.day_name[day.weekday()]
                        day_data = week_data[week_data['date'] == day]

                        st.write(f"**{day_name}, {day.strftime('%m-%d')}**")
                        if not day_data.empty:
                            for _, appt in day_data.iterrows():
                                st.write(f"  • {appt['scheduled_date'].strftime('%H:%M')} - {appt['first_name']} {appt['last_name']} ({appt['category']})")
                        else:
                            st.write("  *No appointments*")
                        st.write("")
                else:
                    st.info("No appointments scheduled for this week")

            elif view_option == "Monthly":
                st.subheader("📊 Monthly Overview")
                scheduled_df['month'] = scheduled_df['scheduled_date'].dt.to_period('M')
                monthly_counts = scheduled_df.groupby('month').size().reset_index(name='count')
                monthly_counts['month_str'] = monthly_counts['month'].astype(str)

                fig = px.bar(monthly_counts, x='month_str', y='count',
                           title='Scheduled Appointments by Month')
                st.plotly_chart(fig, use_container_width=True)

        else:
            st.info("No scheduled appointments found")

        # Schedule new appointment
        st.subheader("📅 Schedule New Appointment")

        pending_df = pd.read_sql('''
            SELECT r.request_id, r.category, r.description,
                   t.first_name, t.last_name, t.unit_number
            FROM maintenance_requests r
            LEFT JOIN tenants t ON r.tenant_id = t.tenant_id
            WHERE r.status = 'Pending' AND r.scheduled_date IS NULL
        ''', conn)

        if not pending_df.empty:
            with st.form("schedule_form"):
                request_options = []
                for _, req in pending_df.iterrows():
                    request_options.append(f"#{req['request_id']} - {req['first_name']} {req['last_name']} - {req['category']}")

                selected_request = st.selectbox("Select Request to Schedule", request_options)

                col1, col2 = st.columns(2)
                with col1:
                    schedule_date = st.date_input("Appointment Date", min_value=datetime.now().date())
                with col2:
                    schedule_time = st.time_input("Appointment Time")

                if st.form_submit_button("📅 Schedule Appointment"):
                    request_id = int(selected_request.split('#')[1].split(' ')[0])
                    scheduled_datetime = datetime.combine(schedule_date, schedule_time)

                    try:
                        c = conn.cursor()
                        c.execute(
                            "UPDATE maintenance_requests SET scheduled_date = ?, status = 'In Progress' WHERE request_id = ?",
                            (scheduled_datetime.isoformat(), request_id)
                        )
                        conn.commit()
                        st.success("✅ Appointment scheduled successfully!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Failed to schedule appointment: {str(e)}")
        else:
            st.info("No pending requests available for scheduling")

        conn.close()

    except Exception as e:
        st.error(f"❌ Error loading calendar: {str(e)}")