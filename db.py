import pymysql
from flask import current_app, g

def get_db():
    if 'db' not in g:
        g.db = pymysql.connect(
            host=current_app.config['DB_HOST'],
            user=current_app.config['DB_USER'],
            password=current_app.config['DB_PASSWORD'],
            database=current_app.config['DB_NAME'],
            port=current_app.config['DB_PORT'],
            cursorclass=pymysql.cursors.DictCursor  # 确保返回的是字典
        )
    return g.db

def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

def query_db(query, args=(), one=False):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(query, args)
    rv = cursor.fetchall()
    cursor.close()
    # 如果查询结果为空，确保返回 None 或者空列表，而不是引起错误
    return (rv[0] if rv else None) if one else (rv if rv else [])

def execute_db(query, args=()):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(query, args)
    db.commit()
    cursor.close()

def init_app(app):
    app.teardown_appcontext(close_db)