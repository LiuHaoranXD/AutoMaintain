import os
import subprocess
import time
from app.db_init import init_db

# 设置环境变量
os.environ["AUTOMAINTAIN_DB_PATH"] = "./automaintain.db"
os.environ["CHROMA_DB_DIR"] = "./chroma_db"
os.environ["OPENAI_API_KEY"] = "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"  
os.environ["SMTP_USER"] = "haoran.liuaz@gmail.com" 
os.environ["SMTP_PASS"] = "byay nnar hrcz rtfn"  
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
subprocess.run(["streamlit", "run", "app/main.py", "--server.port", "8501", "--server.address", "0.0.0.0"])