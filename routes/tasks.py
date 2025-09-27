from flask import Blueprint, jsonify
from db import query_db
import traceback

tasks_bp = Blueprint('tasks_bp', __name__, url_prefix='/api/tasks')

@tasks_bp.route('/pending', methods=['GET'])
def get_pending_tasks():
    """获取所有待办的日常任务，按类型和点位排序"""
    try:
        query_str = """
            SELECT task_id, point_name, location_type, status 
            FROM daily_tasks 
            WHERE status = '待测量' AND DATE(measure_date) = CURDATE()
            ORDER BY location_type, point_name;
        """
        tasks = query_db(query_str)
        # 将数据库字段映射为前端期望的字段
        formatted_tasks = [
            {'task_id': t['task_id'], 'point_name': t['point_name'], 'type': t['location_type'], 'is_completed': False}
            for t in tasks
        ]
        return jsonify(formatted_tasks)
    except Exception as e:
        print(f"--- PENDING TASKS ERROR --- \n{traceback.format_exc()} \n--- END ERROR ---")
        return jsonify({"error": f"获取待办任务失败: {e}"}), 500

@tasks_bp.route('/summary', methods=['GET'])
def get_tasks_summary():
    """获取今日计划的摘要信息，包括固化炉统计和常规任务列表"""
    try:
        # 1. 获取所有今日待办任务
        pending_query = """
            SELECT task_id, point_name, location_type
            FROM daily_tasks 
            WHERE status = '待测量' AND DATE(measure_date) = CURDATE();
        """
        pending_tasks = query_db(pending_query)

        # 2. 获取今日已完成的任务 (从 results 表反查)
        completed_query = """
            SELECT dt.task_id, dt.point_name, dt.location_type
            FROM results r
            JOIN daily_tasks dt ON r.task_id = dt.task_id
            WHERE DATE(r.measure_time) = CURDATE();
        """
        completed_tasks_today = query_db(completed_query)
        completed_task_ids = {t['task_id'] for t in completed_tasks_today}

        # 分类任务
        pending_furnace_tasks = [t for t in pending_tasks if t['location_type'] == '固化炉']
        completed_furnace_tasks_today = [t for t in completed_tasks_today if t['location_type'] == '固化炉']
        
        # 筛选出未完成的常规任务
        other_pending_tasks = [
            t for t in pending_tasks 
            if t['location_type'] != '固化炉' and t['task_id'] not in completed_task_ids
        ]

        # 格式化常规任务列表
        formatted_other_tasks = [
            {'task_id': t['task_id'], 'point_name': t['point_name'], 'type': t['location_type'], 'is_completed': False}
            for t in other_pending_tasks
        ]

        # 构建摘要
        summary = {
            "furnace_summary": {
                "total": len(pending_furnace_tasks) + len(completed_furnace_tasks_today),
                "completed": len(completed_furnace_tasks_today)
            },
            "other_tasks": formatted_other_tasks
        }
        
        return jsonify(summary)
    except Exception as e:
        print(f"--- TASKS SUMMARY ERROR --- \n{traceback.format_exc()} \n--- END ERROR ---")
        return jsonify({"error": f"获取任务摘要失败: {e}"}), 500

