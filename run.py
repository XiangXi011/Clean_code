from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
import os

# 导入配置和数据库初始化函数
from config import Config
from db import init_app as db_init_app

# 导入各个模块的蓝图
from routes.tasks import tasks_bp
from routes.furnaces import furnaces_bp
from routes.dashboard import dashboard_bp
from routes.history import history_bp # <-- 新增导入

def create_app():
    """应用工厂函数"""
    app = Flask(__name__, static_folder='static')
    app.config.from_object(Config)

    # 初始化CORS
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # 初始化数据库
    db_init_app(app)

    # 注册蓝图
    app.register_blueprint(tasks_bp)
    app.register_blueprint(furnaces_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(history_bp) # <-- 注册新的历史记录蓝图

    # --- 前后端一体化路由 ---
    # 提供前端主页面
    @app.route('/')
    def serve_index():
        return send_from_directory(app.static_folder, 'index.html')

    # 处理前端资源（如果需要）
    @app.route('/<path:path>')
    def serve_static(path):
        # 避免与API路由冲突
        if path.startswith('api/'):
            return jsonify({"error": "Not found"}), 404
        return send_from_directory(app.static_folder, path)
        
    return app

if __name__ == '__main__':
    # 这个模式仅用于旧的直接运行方式，现在我们使用 `flask run`
    app = create_app()
    app.run(debug=True)