from flask import Flask, send_from_directory, url_for
from flask_cors import CORS
from config import Config
from routes.dashboard import dashboard_bp
from routes.tasks import tasks_bp
from routes.furnaces import furnaces_bp
from routes.history import history_bp
from routes.results import results_bp
from db import init_app
import os

app = Flask(__name__, static_folder='static')
app.config.from_object(Config)

# 在开发模式下禁用静态文件缓存
if app.config.get('DEBUG'):
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

CORS(app)

# 注册蓝图
app.register_blueprint(dashboard_bp)
app.register_blueprint(tasks_bp)
app.register_blueprint(furnaces_bp)
app.register_blueprint(history_bp)
app.register_blueprint(results_bp)

# 初始化数据库
init_app(app)

@app.route('/')
def serve_index():
    """为 index.html 提供服务，并确保浏览器不缓存它"""
    response = send_from_directory(app.static_folder, 'index.html')
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

if __name__ == '__main__':
    app.run(debug=True)

