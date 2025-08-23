import os
import subprocess
import time
from app.db_init import init_db

os.environ["AUTOMAINTAIN_DB_PATH"] = "./automaintain.db"
os.environ["CHROMA_DB_DIR"] = "./chroma_db"
os.environ["GEMINI_API_KEY"] = ""  
os.environ["SMTP_USER"] = "" 
os.environ["SMTP_PASS"] = ""  
os.environ["SMTP_SERVER"] = "smtp.gmail.com"  
os.environ["SMTP_PORT"] = "587"  

# 初始化数据库
print("Initializing database...")
init_db()

# 创建必要的目录
os.makedirs("./attachments", exist_ok=True)
os.makedirs("./chroma_db", exist_ok=True)

print("🚀 Launching AutoMaintain system...")

# 启动Streamlit应用
subprocess.run(["streamlit", "run", "app/main.py", "--server.port", "8501", "--server.address", "localhost"])
