from flask import Blueprint, request, jsonify
from db import query_db, commit_db
import datetime
import traceback

results_bp = Blueprint('results_bp', __name__, url_prefix='/api/results')

@results_bp.route("/add", methods=['POST'])
def add_result():
    data = request.get_json()
    task_id = data.get('task_id')
    furnace_id = data.get('furnace_id')
    value_03 = data.get('value_03')
    value_05 = data.get('value_05')
    value_50 = data.get('value_50')

    if not (task_id or furnace_id):
        return jsonify({"success": False, "error": "任务ID或固化炉ID必须提供一个"}), 400
    if value_03 is None or value_05 is None or value_50 is None:
        return jsonify({"success": False, "error": "所有测量值均不能为空"}), 400

    try:
        # 插入新结果
        insert_query = """
            INSERT INTO results (task_id, furnace_id, measure_time, value_03, value_05, value_50)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        current_time = datetime.datetime.now()
        commit_db(insert_query, (task_id, furnace_id, current_time, value_03, value_05, value_50))

        # 如果是日常任务，更新任务状态
        if task_id:
            update_task_query = "UPDATE daily_tasks SET status = '已完成' WHERE task_id = %s"
            commit_db(update_task_query, (task_id,))
        
        # 如果是固化炉任务，更新固化炉的最后测量时间
        if furnace_id:
            update_furnace_query = "UPDATE furnaces SET last_measured = %s WHERE furnace_id = %s"
            commit_db(update_furnace_query, (current_time, furnace_id))

        return jsonify({"success": True, "message": "结果记录成功"})
    except Exception as e:
        print(f"--- ADD RESULT ERROR --- \n{traceback.format_exc()} \n--- END ERROR ---")
        return jsonify({"success": False, "error": f"数据库操作失败: {e}"}), 500

@results_bp.route("/<int:result_id>", methods=['DELETE'])
def delete_result(result_id):
    """根据ID删除一条测量记录"""
    try:
        # 在删除前，先检查记录是否存在
        check_query = "SELECT task_id, furnace_id FROM results WHERE result_id = %s"
        result = query_db(check_query, (result_id,), one=True)

        if not result:
            return jsonify({"success": False, "error": "记录未找到"}), 404

        # 执行删除操作
        delete_query = "DELETE FROM results WHERE result_id = %s"
        commit_db(delete_query, (result_id,))

        # 注意：这里我们简化处理，不自动将关联的 daily_tasks 状态重置为“待测量”
        # 因为这可能不是期望的行为（例如，可能只是想删除一条错误的重复记录）
        
        return jsonify({"success": True, "message": "记录已删除"})
    except Exception as e:
        print(f"--- DELETE RESULT ERROR --- \n{traceback.format_exc()} \n--- END ERROR ---")
        return jsonify({"success": False, "error": f"数据库操作失败: {e}"}), 500

