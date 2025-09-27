import os
from dotenv import load_dotenv

# 确保在定义Config类之前加载环境变量
load_dotenv()

class Config:
    """Flask 配置变量"""
    # 数据库配置
    MYSQL_HOST = os.getenv('MYSQL_HOST', 'rm-wz9ytqkb3283476046o.mysql.rds.aliyuncs.com')
    MYSQL_USER = os.getenv('MYSQL_USER', 'Clean_user')
    MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', 'Aabb78785')
    MYSQL_DB = os.getenv('MYSQL_DB', 'cleanliness_db')

