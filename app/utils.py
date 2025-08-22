import os
import smtplib
import logging
import re  # 添加正则表达式支持
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
try:
    from email_validator import validate_email as ve, EmailNotValidError
except ImportError:
    def ve(email):
        return {"email": email}
    class EmailNotValidError(Exception):
        pass
import chromadb
import sqlite3
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AutoMaintainUtils")

def get_db_path():
    return os.getenv("AUTOMAINTAIN_DB_PATH", "./automaintain.db")

def validate_email(email):
    """验证邮箱地址格式"""
    if not email or not isinstance(email, str):
        return False
    
    # 使用正则表达式进行更精确的验证
    try:
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, email):
            return False
        
        # 分割本地部分和域名部分
        local_part, domain = email.split('@', 1)
        
        # 检查本地部分和域名的长度
        if len(local_part) > 64 or len(domain) > 255:
            return False
            
        # 检查域名是否包含点
        if '.' not in domain:
            return False
            
        return True
    except Exception:
        # 如果正则表达式检查失败，使用简单的检查作为后备
        return "@" in email and "." in email.split("@")[-1]

def send_email(to_addr, subject, body):
    """发送邮件函数 - 这是最终的版本，移除了重复定义"""
    if not to_addr or not validate_email(to_addr):
        logger.warning(f"Invalid email address: {to_addr}")
        return False

    user = os.getenv("SMTP_USER")
    pwd = os.getenv("SMTP_PASS")
    server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    port = int(os.getenv("SMTP_PORT", 587))

    if not user or not pwd:
        logger.warning("SMTP credentials not configured")
        return False

    try:
        msg = MIMEMultipart()
        msg["Subject"] = subject
        msg["From"] = user
        msg["To"] = to_addr
        msg.attach(MIMEText(body, 'plain'))

        logger.info(f"Attempting to connect to SMTP server: {server}:{port}")
        
        # 增加超时设置和调试信息
        with smtplib.SMTP(server, port, timeout=30) as s:
            s.set_debuglevel(1)  # 启用调试输出
            s.ehlo()
            s.starttls()
            s.ehlo()
            logger.info("Attempting to login...")
            s.login(user, pwd)
            logger.info("Login successful, sending message...")
            s.send_message(msg)

        logger.info(f"Email sent to {to_addr}")
        return True
    except smtplib.SMTPAuthenticationError as e:
        logger.error(f"SMTP Authentication Error: {str(e)}")
        logger.error("Please check your username and password (app password for Gmail)")
        return False
    except smtplib.SMTPException as e:
        logger.error(f"SMTP Error: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Email failed: {str(e)}")
        return False

def get_chroma_client():
    dir_path = os.getenv("CHROMA_DB_DIR", "./chroma_db")
    os.makedirs(dir_path, exist_ok=True)

    try:
        client = chromadb.PersistentClient(path=dir_path)
        collection = client.get_or_create_collection(
            name="maintenance_knowledge",
            metadata={"hnsw:space": "cosine"}
        )
        return collection
    except Exception as e:
        logger.error(f"ChromaDB error: {str(e)}")
        # 创建内存版本作为后备
        client = chromadb.Client()
        return client.create_collection("fallback_knowledge")

def search_web(query):
    """简单的网络搜索模拟功能"""
    try:
        search_results = [
            {
                "title": f"Maintenance Guide for {query}",
                "snippet": f"Professional solution for {query} related issues. Contact certified technicians.",
                "url": f"https://example.com/maintenance/{query.replace(' ', '-')}"
            },
            {
                "title": f"DIY {query} Repair",
                "snippet": f"Step-by-step guide to fix {query} problems safely.",
                "url": f"https://example.com/diy/{query.replace(' ', '-')}"
            }
        ]
        return search_results[:3]
    except Exception as e:
        logger.error(f"Web search failed: {str(e)}")
        return []

def get_db_connection():
    """获取数据库连接"""
    try:
        db_path = get_db_path()
        conn = sqlite3.connect(db_path, timeout=15)
        conn.row_factory = sqlite3.Row
        return conn
    except Exception as e:
        logger.error(f"Database connection failed: {str(e)}")
        raise

def log_interaction(tenant_id, question, ai_response, tools_used):
    """记录用户交互"""
    try:
        conn = get_db_connection()
        c = conn.cursor()

        c.execute('''
            CREATE TABLE IF NOT EXISTS interactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tenant_id INTEGER,
                question TEXT,
                ai_response TEXT,
                tools_used TEXT,
                created_at TEXT,
                FOREIGN KEY (tenant_id) REFERENCES tenants(tenant_id)
            )
        ''')

        c.execute(
            "INSERT INTO interactions (tenant_id, question, ai_response, tools_used, created_at) VALUES (?,?,?,?,?)",
            (tenant_id, question, ai_response, tools_used, datetime.now().isoformat())
        )
        conn.commit()
        conn.close()
    except Exception as e:
        logger.error(f"Failed to log interaction: {str(e)}")

def parse_datetime(datetime_str):
    """解析日期时间字符串，支持多种格式"""
    if not datetime_str:
        return None
        
    try:
        # 尝试解析 ISO 8601 格式
        return datetime.fromisoformat(datetime_str.replace('Z', '+00:00'))
    except ValueError:
        try:
            # 尝试解析其他常见格式
            return datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            try:
                # 尝试解析日期部分
                return datetime.strptime(datetime_str, "%Y-%m-%d")
            except ValueError:
                logger.error(f"无法解析日期时间字符串: {datetime_str}")
                return None

def format_datetime(dt, format_str="%Y-%m-%d %H:%M:%S"):
    """格式化日期时间为字符串"""
    if not dt:
        return ""
    return dt.strftime(format_str)