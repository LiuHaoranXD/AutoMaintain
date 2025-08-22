import streamlit as st
import sqlite3
import time
from datetime import datetime
from utils import validate_email, send_email, get_db_path, get_db_connection
from ai_agent import classify_issue, recommend_solutions, estimate_cost, generate_ai_response
import os

def show_tenant_form():
    st.header("📝 Tenant Maintenance Request")
    st.info("Complete this form to submit a maintenance request. AI will automatically classify and provide recommendations.")

    # FAQ 部分
    with st.expander("❓ Frequently Asked Questions", expanded=False):
        faq_question = st.selectbox(
            "Select a common question:",
            [
                "How do I reset a tripped circuit breaker?",
                "What should I do if my sink is clogged?",
                "How to change my air filter?",
                "My toilet keeps running, what's the fix?",
                "How do I report an emergency?",
                "When will my request be addressed?"
            ]
        )
        if st.button("Get Answer"):
            tenant_id = st.session_state.get('current_tenant_id', 1)
            response = generate_ai_response(tenant_id, faq_question)
            st.info(response)

    # 主要表单
    with st.form("tenant_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Your Name *", placeholder="John Smith", help="Required field")
        with col2:
            email = st.text_input("Email Address", placeholder="john@example.com", help="Required for status updates")

        col3, col4 = st.columns(2)
        with col3:
            unit = st.text_input("Unit Number *", placeholder="Apt 3B")
        with col4:
            phone = st.text_input("Phone Number", placeholder="555-0123")

        category = st.selectbox(
            "Issue Category (AI will auto-detect if not specified)",
            ["(Let AI determine)", "Plumbing", "Electrical", "HVAC", "Structural", "Appliance", "Other"]
        )

        urgency = st.selectbox(
            "Urgency Level",
            ["Normal", "Urgent", "Emergency"],
            help="Emergency: immediate safety concern, Urgent: major inconvenience, Normal: can wait"
        )

        description = st.text_area(
            "Describe the Issue in Detail *",
            placeholder="Please provide specific details: What is the problem? When did it start? What have you tried? Any safety concerns?",
            height=150,
            help="More details help us provide better solutions"
        )

        attach = st.file_uploader(
            "Attach Photos/Files (optional)",
            type=["png", "jpg", "jpeg", "pdf", "mp4", "mov"],
            accept_multiple_files=True,
            help="Photos help us understand the issue better"
        )

        col5, col6 = st.columns(2)
        with col5:
            preferred_time = st.selectbox(
                "Preferred Service Time",
                ["Any time", "Morning (8AM-12PM)", "Afternoon (12PM-5PM)", "Evening (5PM-8PM)"]
            )
        with col6:
            notify_methods = st.multiselect(
                "How would you like updates?",
                ["Email", "Phone", "Text Message"],
                default=["Email"] if email else []
            )

        submitted = st.form_submit_button("🚀 Submit Request", use_container_width=True)

    if submitted:
        if not name or not description or not unit:
            st.error("❌ Please fill in all required fields (Name, Unit Number, and Description).")
            return

        if email and not validate_email(email):
            st.error("❌ Please enter a valid email address.")
            return

        status_container = st.container()
        progress_bar = st.progress(0)
        with status_container:
            st.info("🤖 AI is analyzing your request...")
            progress_bar.progress(20)

        try:
            time.sleep(1)
            ai_category, priority = classify_issue(description)
            progress_bar.progress(40)
            final_category = ai_category if category == "(Let AI determine)" else category
            st.success(f"✓ Issue classified as: **{final_category}** | Priority: **{priority}**")

            st.info("💰 Estimating costs...")
            estimated_cost = estimate_cost(description, final_category)
            progress_bar.progress(60)
            if estimated_cost:
                st.success(f"💲 Estimated cost: **${estimated_cost:.2f}**")

            st.info("💾 Saving to database...")
            try:
                conn = get_db_connection()
                c = conn.cursor()
                tenant_id = None
                if email:
                    c.execute("SELECT tenant_id FROM tenants WHERE email=?", (email,))
                    row = c.fetchone()
                    if row:
                        tenant_id = row[0]
                if not tenant_id:
                    c.execute(
                        "INSERT INTO tenants (first_name, email, phone, unit_number, created_at) VALUES (?,?,?,?,?)",
                        (name, email, phone, unit, datetime.now().isoformat())
                    )
                    tenant_id = c.lastrowid

                c.execute(
                    '''INSERT INTO maintenance_requests
                    (tenant_id, category, description, priority, status, urgency, created_at, estimated_cost, notes)
                    VALUES (?,?,?,?,?,?,?,?,?)''',
                    (tenant_id, final_category, description, priority, 'Pending', urgency,
                     datetime.now().isoformat(), estimated_cost, f"Preferred time: {preferred_time}")
                )
                request_id = c.lastrowid

                if attach:
                    attachment_paths = []
                    for i, file in enumerate(attach):
                        attach_dir = f"./attachments/{request_id}"
                        os.makedirs(attach_dir, exist_ok=True)
                        attach_path = f"{attach_dir}/{i}_{file.name}"
                        with open(attach_path, "wb") as f:
                            f.write(file.getbuffer())
                        attachment_paths.append(attach_path)
                    c.execute(
                        "UPDATE maintenance_requests SET attachment_path=? WHERE request_id=?",
                        (";".join(attachment_paths), request_id)
                    )

                conn.commit()
                conn.close()
                progress_bar.progress(80)
                st.session_state.current_tenant_id = tenant_id
            except sqlite3.Error as e:
                st.error(f"❌ Database error: {str(e)}")
                return

            st.info("🔍 Getting AI recommendations...")
            try:
                recommendations = recommend_solutions(description, final_category, top_k=3)
                progress_bar.progress(90)

                if recommendations:
                    st.subheader("💡 AI Recommendations")
                    for i, rec in enumerate(recommendations, 1):
                        with st.expander(f"Solution {i}: {rec['title']}", expanded=i==1):
                            st.write(f"**Solution:** {rec['snippet']}")
                            if rec.get('cost'):
                                st.write(f"**Estimated Cost:** {rec['cost']}")
                            if rec.get('time'):
                                st.write(f"**Estimated Time:** {rec['time']}")
                            if rec.get('difficulty'):
                                st.write(f"**Difficulty:** {rec['difficulty']}")
            except Exception as e:
                st.warning(f"⚠️ AI recommendations failed: {str(e)}")

            if email and "Email" in notify_methods:
                st.info("📧 Sending confirmation email...")
                try:
                    email_body = f'''Hello {name},

We've received your maintenance request (ID: {request_id}):

🏠 Unit: {unit}
📋 Category: {final_category}
⚡ Priority: {priority}
🚨 Urgency: {urgency}
💰 Estimated Cost: ${estimated_cost if estimated_cost else 'TBD'}

📝 Description:
{description}

⏰ Preferred Service Time: {preferred_time}

Our maintenance team will review your request and contact you within 24 hours.

For urgent issues, please call our emergency line.

Thank you,
AutoMaintain Team'''
                    send_email(email, f"AutoMaintain: Request #{request_id} Received", email_body)
                except Exception as e:
                    st.warning(f"⚠️ Email notification failed: {str(e)}")

            progress_bar.progress(100)
            st.balloons()
            st.success("✅ **Request submitted successfully!**")
            st.info(f"Your request ID is: **{request_id}**")
        except Exception as e:
            st.error(f"❌ An error occurred while processing your request: {str(e)}")
            st.info("Please try again or contact our office directly.")
            