import streamlit as st
import sqlite3
import pandas as pd
from app.utils import get_db_path, format_datetime

def show_admin_dashboard():
    st.title("📊 Admin Dashboard")

    conn = sqlite3.connect(get_db_path())
    df = pd.read_sql("SELECT * FROM maintenance_requests", conn)

    if df.empty:
        st.info("No requests yet.")
        return

    st.metric("Total Requests", len(df))
    st.metric("Pending", len(df[df['status']=="pending"]))
    st.metric("Completed", len(df[df['status']=="completed"]))

    st.subheader("All Requests")
    df['created_at'] = df['created_at'].apply(format_datetime)
    st.dataframe(df)
