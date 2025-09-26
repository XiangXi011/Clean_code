from flask import Blueprint, jsonify, request
from db import query_db, execute_db
from datetime import datetime

tasks_bp = Blueprint('tasks_bp', __name__, url_prefix='/api/tasks')

# 修复: 将路由从'/'修改为'/pending'以匹配前端的API请求
@tasks_bp.route('/pending', methods=['GET'])
def get_today_tasks():
    """获取今天所有待测量的计划任务"""
    try:
        today_str = datetime.now().strftime('%Y-%m-%d')
        tasks = query_db(
            "SELECT * FROM daily_tasks WHERE measure_date = %s AND status = '待测量'", 
            (today_str,)
        )
        return jsonify(tasks)
    except Exception as e:
        print(f"Error fetching today's tasks: {e}")
        return jsonify({"error": f"获取今日任务失败: {e}"}), 500

@tasks_bp.route('/<int:task_id>/record', methods=['POST'])
def record_task_result(task_id):
    """为一个计划任务记录测量结果"""
    data = request.get_json()
    if not data or 'value_03' not in data or 'value_05' not in data or 'value_50' not in data:
        return jsonify({"error": "缺少测量值"}), 400

    try:
        # 1. 在 results 表中插入新纪录
        execute_db(
            "INSERT INTO results (task_id, measure_time, value_03, value_05, value_50) VALUES (%s, %s, %s, %s, %s)",
            (task_id, datetime.now(), data['value_03'], data['value_05'], data['value_50'])
        )
        
        # 2. 更新 daily_tasks 表中的状态
        execute_db(
            "UPDATE daily_tasks SET status = '已完成' WHERE task_id = %s",
            (task_id,)
        )
        
        return jsonify({"success": True, "message": "记录成功"}), 201
    except Exception as e:
        print(f"Error recording task {task_id}: {e}")
        return jsonify({"error": str(e)}), 500
