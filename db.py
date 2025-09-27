import pymysql
from flask import current_app, g
from config import Config

def get_db():
    """获取数据库连接"""
    if 'db' not in g:
        g.db = pymysql.connect(
            host=Config.MYSQL_HOST,
            user=Config.MYSQL_USER,
            password=Config.MYSQL_PASSWORD,
            database=Config.MYSQL_DB,
            cursorclass=pymysql.cursors.DictCursor
        )
    return g.db

def close_db(e=None):
    """关闭数据库连接"""
    db = g.pop('db', None)
    if db is not None:
        db.close()

def query_db(query, args=(), one=False):
    """执行数据库查询 (SELECT)"""
    db = get_db()
    cursor = db.cursor()
    cursor.execute(query, args)
    rv = cursor.fetchall()
    cursor.close()
    return (rv[0] if rv else None) if one else rv

def commit_db(query, args=()):
    """执行数据库操作 (INSERT, UPDATE, DELETE)并提交"""
    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute(query, args)
        db.commit()
        return cursor.lastrowid or cursor.rowcount
    except Exception as e:
        db.rollback()
        print(f"Database execution failed: {e}")
        raise e
    finally:
        cursor.close()

def init_app(app):
    """初始化应用，注册数据库关闭函数"""
    app.teardown_appcontext(close_db)

