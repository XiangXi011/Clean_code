from flask import Blueprint, request, jsonify
from db import get_db
import datetime
import traceback

results_bp = Blueprint('results_bp', __name__)

@results_bp.route("/api/results/add", methods=['POST'])
def add_result():
    """接收前端发送的测量数据并将其存入数据库"""
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'error': '请求体中没有提供JSON数据'}), 400

    task_id = data.get('task_id')
    furnace_id = data.get('furnace_id')
    
    # 验证测量值是否存在且可以转换为浮点数
    try:
        value_03 = float(data['value_03'])
        value_05 = float(data['value_05'])
        value_50 = float(data['value_50'])
    except (ValueError, TypeError, KeyError) as e:
        return jsonify({'success': False, 'error': f'无效或缺失的测量值: {e}'}), 400
    
    if not task_id and not furnace_id:
        return jsonify({'success': False, 'error': '必须提供 task_id 或 furnace_id'}), 400

    db = None
    try:
        db = get_db()
        cursor = db.cursor()
        
        current_time = datetime.datetime.now()
        
        # 插入新结果
        insert_query = """
            INSERT INTO results (task_id, furnace_id, measure_time, value_03, value_05, value_50)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        cursor.execute(insert_query, (task_id, furnace_id, current_time, value_03, value_05, value_50))

        # 如果是日常任务，则更新任务状态
        if task_id:
            update_task_query = "UPDATE daily_tasks SET status = '已完成' WHERE task_id = %s"
            cursor.execute(update_task_query, (task_id,))

        # 如果是固化炉任务，则更新固化炉的最后测量时间
        if furnace_id:
            update_furnace_query = "UPDATE furnaces SET last_measured = %s WHERE furnace_id = %s"
            cursor.execute(update_furnace_query, (current_time, furnace_id))

        db.commit()
        return jsonify({'success': True, 'message': '数据添加成功'})
    except Exception as e:
        if db:
            db.rollback()
        # 打印详细的错误堆栈以便调试
        traceback.print_exc()
        return jsonify({'success': False, 'error': f'数据库操作失败: {str(e)}'}), 500
