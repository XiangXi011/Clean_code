import os
from dotenv import load_dotenv

# 定位到项目根目录的.env文件
basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    """Flask 配置类"""
    # 从环境变量中获取数据库连接信息
    DB_HOST = os.getenv('DB_HOST')
    DB_USER = os.getenv('DB_USER')
    DB_PASSWORD = os.getenv('DB_PASSWORD')
    DB_NAME = os.getenv('DB_NAME')
    # 新增获取端口号，如果.env中没有则默认为3306
    DB_PORT = int(os.getenv('DB_PORT', 3306))

    # 确保所有数据库配置都已设置
    if not all([DB_HOST, DB_USER, DB_PASSWORD, DB_NAME]):
        raise ValueError("数据库配置信息不完整，请检查 .env 文件")