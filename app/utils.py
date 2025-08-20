import os
import logging
import re
import sqlite3
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AutoMaintain")

def validate_email(email: str) -> bool:
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def format_datetime(dt_str):
    """格式化时间戳为更友好的格式"""
    try:
        return datetime.fromisoformat(dt_str).strftime("%Y-%m-%d %H:%M")
    except:
        return dt_str

def get_db_path():
    return os.getenv("AUTOMAINTAIN_DB_PATH", "./automaintain.db")

def get_chroma_client():
    """返回 Chroma 向量数据库 client"""
    dir_path = os.getenv("CHROMA_DB_DIR", "./chroma_db")
    os.makedirs(dir_path, exist_ok=True)

    import chromadb
    from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
    embedding_fn = SentenceTransformerEmbeddingFunction("all-MiniLM-L6-v2")
    client = chromadb.PersistentClient(path=dir_path)
    return client.get_or_create_collection("maintenance_knowledge", embedding_function=embedding_fn)
