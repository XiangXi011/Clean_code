from flask import Blueprint, jsonify, request
from db import query_db, commit_db
import datetime
import traceback

tasks_bp = Blueprint('tasks_bp', __name__, url_prefix='/api/tasks')

@tasks_bp.route('/pending', methods=['GET'])
def get_pending_tasks():
    """获取所有状态为'待测量'的今日任务"""
    try:
        # 这个查询现在只获取非固化炉的待办任务
        query_str = """
            SELECT task_id, point_name, location_type, status 
            FROM daily_tasks 
            WHERE status = '待测量' AND DATE(measure_date) = CURDATE() AND location_type != '固化炉'
            ORDER BY location_type, point_name
        """
        tasks = query_db(query_str)
        # 为前端统一数据结构
        for task in tasks:
            task['type'] = task['location_type']
            task['name'] = task['point_name']
        return jsonify(tasks)
    except Exception as e:
        print(f"--- PENDING TASKS ERROR --- \n{traceback.format_exc()} \n--- END ERROR ---")
        return jsonify({"error": f"获取待办任务失败: {e}"}), 500

@tasks_bp.route('/summary', methods=['GET'])
def get_task_summary():
    """获取今日任务的摘要信息，所有计数逻辑基于 daily_tasks 表"""
    try:
        # 获取今天所有的日常任务
        all_today_tasks = query_db(
            "SELECT * FROM daily_tasks WHERE DATE(measure_date) = CURDATE()"
        )

        # 分离固化炉任务和其他任务
        furnace_tasks_today = [task for task in all_today_tasks if task['location_type'] == '固化炉']
        other_tasks_pending = [task for task in all_today_tasks if task['location_type'] != '固化炉' and task['status'] == '待测量']
        
        # 为前端统一数据结构
        for task in other_tasks_pending:
            task['type'] = task['location_type']
            task['name'] = task['point_name']

        # 计算固化炉摘要
        furnace_summary = {
            "total": len(furnace_tasks_today),
            "completed": sum(1 for task in furnace_tasks_today if task['status'] == '已完成')
        }

        return jsonify({
            "furnace_summary": furnace_summary,
            "other_tasks": other_tasks_pending
        })
    except Exception as e:
        print(f"--- TASK SUMMARY ERROR --- \n{traceback.format_exc()} \n--- END ERROR ---")
        return jsonify({"error": f"获取任务摘要失败: {e}"}), 500

