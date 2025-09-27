import pymysql
from flask import g
from config import Config
import sys
import traceback

def get_db():
    """获取数据库连接 (使用 PyMySQL)"""
    if 'db' not in g:
        try:
            g.db = pymysql.connect(
                host=Config.MYSQL_HOST,
                user=Config.MYSQL_USER,
                password=Config.MYSQL_PASSWORD,
                database=Config.MYSQL_DB,
                connect_timeout=10,
                cursorclass=pymysql.cursors.DictCursor  # 使查询结果返回字典
            )
        except pymysql.Error as err:
            print(f"数据库连接失败: {err}", file=sys.stderr)
            traceback.print_exc()
            return None
    return g.db

def close_db(e=None):
    """关闭数据库连接"""
    db = g.pop('db', None)
    if db is not None:
        db.close()

def query_db(query, args=(), one=False, commit=False):
    """执行数据库查询的辅助函数"""
    db = get_db()
    if db is None:
        raise ConnectionError("无法连接到数据库")
        
    cursor = db.cursor()
    try:
        cursor.execute(query, args)
        if commit:
            db.commit()
            return cursor.lastrowid
        
        rv = cursor.fetchall()
        return (rv[0] if rv else None) if one else rv
    except pymysql.Error as err:
        print(f"数据库查询失败: {err}", file=sys.stderr)
        print(f"查询语句: {query} \n参数: {args}", file=sys.stderr)
        db.rollback()
        raise
    finally:
        cursor.close()

def init_app(app):
    """在Flask应用实例上注册数据库关闭函数"""
    app.teardown_appcontext(close_db)

