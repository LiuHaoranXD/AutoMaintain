import streamlit as st
from utils import get_chroma_client
import tempfile
import os
import pandas as pd

def extract_text_from_pdf(file_path):
    try:
        import PyPDF2
        with open(file_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text
    except Exception as e:
        st.error(f"PDF extraction failed: {str(e)}")
        return ""

def show_uploader():
    st.header("📚 Knowledge Base Manager")
    st.info("Upload documents to enhance the AI's knowledge base")

    try:
        collection = get_chroma_client()
    except Exception as e:
        st.error(f"ChromaDB initialization failed: {str(e)}")
        return

    # Document upload section
    with st.expander("📤 Upload Documents", expanded=True):
        uploaded_files = st.file_uploader(
            "Select knowledge files",
            type=["txt", "pdf", "md"],
            accept_multiple_files=True,
            help="Upload maintenance manuals, procedures, or documentation"
        )

        if uploaded_files:
            default_category = st.selectbox(
                "Document Category for all files",
                ["Plumbing", "Electrical", "HVAC", "Structural", "Appliance", "General", "Other"],
                index=5
            )

            if st.button("🚀 Process Uploads"):
                progress_bar = st.progress(0)
                status_text = st.empty()

                for i, file in enumerate(uploaded_files):
                    try:
                        status_text.info(f"Processing {file.name} ({i+1}/{len(uploaded_files)})")

                        # Save to temp file
                        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.name)[1]) as tmp:
                            tmp.write(file.read())
                            tmp_path = tmp.name

                        # Process based on file type
                        if file.name.lower().endswith(".pdf"):
                            text = extract_text_from_pdf(tmp_path)
                        else:
                            with open(tmp_path, "r", encoding="utf-8", errors="replace") as f:
                                text = f.read()

                        # Clean up temp file
                        os.unlink(tmp_path)

                        if text.strip():
                            # Add to ChromaDB
                            collection.add(
                                documents=[text],
                                metadatas=[{
                                    "filename": file.name,
                                    "category": default_category,
                                    "source": "upload",
                                    "upload_date": str(pd.Timestamp.now())
                                }],
                                ids=[f"doc_{pd.Timestamp.now().timestamp()}_{file.name}"]
                            )
                            st.success(f"✓ Processed {file.name}")
                        else:
                            st.warning(f"⚠️ No text extracted from {file.name}")

                        progress_bar.progress((i + 1) / len(uploaded_files))

                    except Exception as e:
                        st.error(f"Error processing {file.name}: {str(e)}")

                status_text.success("✅ Upload processing complete!")

    # Show current documents
    try:
        count = collection.count()
        st.info(f"📊 Knowledge base contains {count} documents")

        if count > 0:
            with st.expander("🔍 Search Knowledge Base"):
                search_query = st.text_input("Search for solutions:", placeholder="e.g., leaking faucet")
                if search_query and st.button("Search"):
                    results = collection.query(
                        query_texts=[search_query],
                        n_results=min(3, count)
                    )

                    if results['documents']:
                        for i, doc in enumerate(results['documents'][0]):
                            st.write(f"**Result {i+1}:**")
                            st.info(doc[:500] + "..." if len(doc) > 500 else doc)
                    else:
                        st.warning("No matching documents found")

    except Exception as e:
        st.warning(f"Could not get document count: {str(e)}")