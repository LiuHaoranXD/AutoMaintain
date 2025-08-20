#!/usr/bin/env python3
"""
启动 AutoMaintain
"""
import os
import sys
import subprocess
from pathlib import Path

def main():
    project_path = Path(__file__).parent
    os.chdir(project_path)

    # 初始化数据库
    print("🔧 初始化数据库...")
    from app.db_init import init_db
    init_db()
    print("✅ 数据库初始化完成")

    # 启动 Streamlit
    print("🚀 启动 AutoMaintain...")
    subprocess.run([
        sys.executable, "-m", "streamlit", "run",
        "app/main.py", "--server.port", "8501"
    ])

if __name__ == "__main__":
    main()
