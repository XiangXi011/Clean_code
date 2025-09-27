from flask import Flask, send_from_directory, url_for
from flask_cors import CORS
from routes.dashboard import dashboard_bp
from routes.tasks import tasks_bp
from routes.furnaces import furnaces_bp
from routes.history import history_bp
from routes.results import results_bp
from db import init_app
import os
import time

app = Flask(__name__, static_folder='static')
CORS(app)

# 初始化数据库
init_app(app)

# 注册蓝图
app.register_blueprint(dashboard_bp)
app.register_blueprint(tasks_bp)
app.register_blueprint(furnaces_bp)
app.register_blueprint(history_bp)
app.register_blueprint(results_bp)

# 为静态文件URL添加时间戳，防止浏览器缓存
@app.context_processor
def override_url_for():
    """
    为静态文件URL添加一个时间戳查询参数，以实现缓存抑制。
    """
    return dict(url_for=dated_url_for)

def dated_url_for(endpoint, **values):
    if endpoint == 'static':
        filename = values.get('filename', None)
        if filename:
            file_path = os.path.join(app.root_path,
                                     app.static_folder, filename)
            if os.path.exists(file_path):
                values['q'] = int(os.stat(file_path).st_mtime)
    return url_for(endpoint, **values)


@app.route('/')
def serve_index():
    """服务于前端主页"""
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    """服务于其他静态文件"""
    return send_from_directory(app.static_folder, path)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    # 确保在开发环境中启用调试模式
    debug_mode = os.environ.get("FLASK_ENV") == "development"
    app.run(debug=debug_mode, host='0.0.0.0', port=port)

