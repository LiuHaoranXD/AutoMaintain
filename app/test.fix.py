# test_email.py
import os
from utils import send_email

# 设置环境变量
os.environ["SMTP_USER"] = "haoran.liuaz@gmail.com" 
os.environ["SMTP_PASS"] = "byay nnar hrcz rtfn"  
os.environ["SMTP_SERVER"] = "smtp.gmail.com"
os.environ["SMTP_PORT"] = "587"

# 测试发送邮件
result = send_email(
    "liuhaoran0808@e.newera.edu.my",
    "Test Email from AutoMaintain",
    "This is a test email to verify the email functionality."
)

print(f"Email sent: {result}")