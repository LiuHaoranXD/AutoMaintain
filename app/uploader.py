import streamlit as st
import tempfile
import os
from datetime import datetime
from app.utils import get_chroma_client

def show_uploader():
    st.header("📚 Knowledge Base")
    collection = get_chroma_client()

    uploaded_files = st.file_uploader("Upload documents", type=["txt","pdf"], accept_multiple_files=True)
    if uploaded_files:
        for file in uploaded_files:
            tmp = tempfile.NamedTemporaryFile(delete=False)
            tmp.write(file.read())
            tmp.close()

            with open(tmp.name, "r", errors="ignore") as f:
                text = f.read()

            collection.add(
                documents=[text],
                metadatas=[{"title": file.name, "source": datetime.now().strftime("%Y-%m-%d")}],
                ids=[f"doc_{datetime.now().timestamp()}"]
            )
            st.success(f"Added {file.name}")
            os.unlink(tmp.name)

    st.write("Current docs:", collection.count())
