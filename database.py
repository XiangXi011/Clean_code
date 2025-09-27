import mysql.connector
from flask import g, current_app
from config import Config
import sys
import traceback

def get_db():
    """获取数据库连接"""
    if 'db' not in g:
        try:
            g.db = mysql.connector.connect(
                host=Config.MYSQL_HOST,
                user=Config.MYSQL_USER,
                password=Config.MYSQL_PASSWORD,
                database=Config.MYSQL_DB,
                # 增加超时设置
                connect_timeout=10
            )
        except mysql.connector.Error as err:
            print(f"数据库连接失败: {err}", file=sys.stderr)
            traceback.print_exc()
            # 在无法连接时返回 None 或抛出异常
            return None
    return g.db

def close_db(e=None):
    """关闭数据库连接"""
    db = g.pop('db', None)
    if db is not in None:
        db.close()

def query_db(query, args=(), one=False, commit=False):
    """执行数据库查询的辅助函数"""
    db = get_db()
    # 确保数据库连接成功
    if db is None:
        raise ConnectionError("无法连接到数据库")
        
    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute(query, args)
        if commit:
            db.commit()
            return cursor.lastrowid  # 对于INSERT, 返回ID很有用
        
        rv = cursor.fetchall()
        return (rv[0] if rv else None) if one else rv
    except mysql.connector.Error as err:
        print(f"数据库查询失败: {err}", file=sys.stderr)
        print(f"查询语句: {query} \n参数: {args}", file=sys.stderr)
        db.rollback() # 如果出错则回滚
        raise  # 重新抛出异常，以便上层可以捕获
    finally:
        cursor.close()

def init_app(app):
    """在Flask应用实例上注册数据库关闭函数"""
    app.teardown_appcontext(close_db)
