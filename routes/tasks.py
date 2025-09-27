from flask import Blueprint, jsonify
from db import query_db
import traceback
import datetime

tasks_bp = Blueprint('tasks_bp', __name__)

# 复制一份每日计划，以便在此处引用
WEEKLY_PLAN = {
    0: {"types": ["层流棚"], "furnace_count": 7},
    1: {"types": ["加硬机"], "furnace_count": 8},
    2: {"types": ["大环境"], "furnace_count": 8},
    3: {"types": ["层流棚"], "furnace_count": 7},
    4: {"types": ["加硬机", "大环境"], "furnace_count": 0},
    5: {"types": ["大环境"], "furnace_count": 14},
    6: {"types": [], "furnace_count": 0},
}

@tasks_bp.route("/api/tasks/pending", methods=['GET'])
def get_pending_tasks():
    try:
        # 1. 获取所有非固化炉的待办任务
        query = "SELECT task_id, location_type, point_name, status FROM daily_tasks WHERE measure_date = CURDATE() AND status = '待测量' ORDER BY location_type, point_name"
        tasks = query_db(query)

        # 2. 计算今天固化炉的计划和完成情况
        today = datetime.date.today()
        weekday = today.weekday()
        plan = WEEKLY_PLAN.get(weekday, {"furnace_count": 0})
        furnace_plan_count = plan.get("furnace_count", 0)

        if furnace_plan_count > 0:
            furnace_completed_query = """
                SELECT COUNT(*) as completed 
                FROM results r
                JOIN furnaces f ON r.furnace_id = f.furnace_id
                WHERE DATE(r.measure_time) = CURDATE()
            """
            completed_result = query_db(furnace_completed_query, one=True)
            furnace_completed_count = completed_result['completed'] if completed_result else 0
            
            # 3. 创建一个摘要任务项并添加到任务列表
            furnace_summary_task = {
                "task_id": "furnace_summary",
                "is_summary": True, # 添加一个特殊标记
                "location_type": "固化炉",
                "point_name": f"今日计划: {furnace_plan_count} 台",
                "status": f"已完成: {furnace_completed_count} 台"
            }
            tasks.append(furnace_summary_task)

        return jsonify(tasks)
    except Exception as e:
        error_message = f"获取今日待办任务失败: {str(e)}"
        print(f"--- TASKS PENDING ERROR --- \n{traceback.format_exc()} \n--- END ERROR ---")
        return jsonify({"error": error_message}), 500

# record_task_result 函数保持不变，因为它只处理带 task_id 的常规任务
@tasks_bp.route("/api/tasks/<int:task_id>/record", methods=['POST'])
def record_task_result(task_id):
    # ... 此函数代码与您提供的版本完全相同，无需修改 ...
    data = request.get_json()
    if not data or 'value_03' not in data or 'value_05' not in data or 'value_50' not in data:
        return jsonify({"error": "请求数据不完整"}), 400
    try:
        update_query = "UPDATE daily_tasks SET status = '已完成' WHERE task_id = %s"
        query_db(update_query, (task_id,), commit=True)
        insert_query = "INSERT INTO results (task_id, measure_time, value_03, value_05, value_50, operator) VALUES (%s, NOW(), %s, %s, %s, %s)"
        params = (task_id, data['value_03'], data['value_05'], data['value_50'], data.get('operator', 'default_user'))
        query_db(insert_query, params, commit=True)
        return jsonify({"message": f"成功记录任务 {task_id} 的测量结果"}), 201
    except Exception as e:
        error_message = f"记录任务结果失败: {str(e)}"
        print(f"--- TASK RECORD ERROR --- \n{traceback.format_exc()} \n--- END ERROR ---")
        return jsonify({"error": error_message}), 500

