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
        current_time = datetime.datetime.now()
        
        insert_query = """
            INSERT INTO results (task_id, furnace_id, measure_time, value_03, value_05, value_50)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        commit_db(insert_query, (task_id, furnace_id, current_time, value_03, value_05, value_50))

        if task_id:
            update_task_query = "UPDATE daily_tasks SET status = '已完成' WHERE task_id = %s"
            commit_db(update_task_query, (task_id,))
        
        if furnace_id:
            update_furnace_query = "UPDATE furnaces SET last_measured = %s WHERE furnace_id = %s"
            commit_db(update_furnace_query, (current_time, furnace_id))

        return jsonify({"success": True, "message": "结果记录成功"})
    except Exception as e:
        print(f"--- ADD RESULT ERROR --- \n{traceback.format_exc()} \n--- END ERROR ---")
        return jsonify({"success": False, "error": f"数据库操作失败: {e}"}), 500

@results_bp.route("/<int:result_id>", methods=['DELETE'])
def delete_result(result_id):
    """根据ID删除一条测量记录, 并智能回滚关联任务的状态"""
    try:
        # 在删除前，先获取关联的 task_id 和 furnace_id
        check_query = "SELECT task_id, furnace_id FROM results WHERE result_id = %s"
        result_to_delete = query_db(check_query, (result_id,), one=True)

        if not result_to_delete:
            return jsonify({"success": False, "error": "记录未找到"}), 404

        # 执行删除操作
        delete_query = "DELETE FROM results WHERE result_id = %s"
        commit_db(delete_query, (result_id,))

        # Case 1: 如果关联的是日常任务，则重置其状态
        associated_task_id = result_to_delete.get('task_id')
        if associated_task_id:
            reset_task_query = "UPDATE daily_tasks SET status = '待测量' WHERE task_id = %s"
            commit_db(reset_task_query, (associated_task_id,))
            print(f"Task ID {associated_task_id} status has been reset to '待测量'.")
        
        # Case 2: 如果关联的是固化炉，则回滚其 last_measured 时间
        associated_furnace_id = result_to_delete.get('furnace_id')
        if associated_furnace_id:
            # 查找删除后，该固化炉最新的一次测量记录
            latest_measurement_query = """
                SELECT MAX(measure_time) as new_last_measured 
                FROM results 
                WHERE furnace_id = %s
            """
            newest_record = query_db(latest_measurement_query, (associated_furnace_id,), one=True)
            
            new_last_measured = newest_record.get('new_last_measured') if newest_record else None
            
            # 更新 furnaces 表
            update_furnace_query = "UPDATE furnaces SET last_measured = %s WHERE furnace_id = %s"
            commit_db(update_furnace_query, (new_last_measured, associated_furnace_id))

        return jsonify({"success": True, "message": "记录已删除，关联状态已回滚"})
    except Exception as e:
        print(f"--- DELETE RESULT ERROR --- \n{traceback.format_exc()} \n--- END ERROR ---")
        return jsonify({"success": False, "error": f"数据库操作失败: {e}"}), 500

