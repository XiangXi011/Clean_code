from flask import Blueprint, jsonify, request
from db import query_db, execute_db
from datetime import datetime, timedelta

furnaces_bp = Blueprint('furnaces_bp', __name__, url_prefix='/api/furnaces')

@furnaces_bp.route('/pending', methods=['GET'])
def get_pending_furnaces():
    """获取所有待测量的固化炉列表"""
    try:
        # 查询今天及今天之前所有待测量的固化炉
        today_str = datetime.now().strftime('%Y-%m-%d')
        # 这个查询现在应该可以正常工作，因为数据库中已经有了 next_measure_date 列
        furnaces = query_db(
            "SELECT * FROM furnaces WHERE next_measure_date <= %s", 
            (today_str,)
        )
        return jsonify(furnaces)
    except Exception as e:
        # 打印详细错误到后端控制台，方便调试
        print(f"Error fetching pending furnaces: {e}")
        return jsonify({"error": f"获取待测固化炉列表失败: {e}"}), 500

@furnaces_bp.route('/<int:furnace_id>/measure', methods=['POST'])
def measure_furnace(furnace_id):
    """记录固化炉的测量数据并更新下次测量日期"""
    data = request.get_json()
    if not data or 'value_03' not in data or 'value_05' not in data or 'value_50' not in data:
        return jsonify({"error": "缺少测量值"}), 400

    try:
        now = datetime.now()
        # 假设测量周期为30天
        next_measure_date = now + timedelta(days=30)
        
        # 1. 在 results 表中插入新纪录
        # 注意: 假设 results 表中有一个 furnace_id 列来关联固化炉
        execute_db(
            "INSERT INTO results (furnace_id, measure_time, value_03, value_05, value_50) VALUES (%s, %s, %s, %s, %s)",
            (furnace_id, now, data['value_03'], data['value_05'], data['value_50'])
        )
        
        # 2. 更新 furnaces 表中的最后测量日期和下次测量日期
        execute_db(
            "UPDATE furnaces SET last_measured = %s, next_measure_date = %s WHERE furnace_id = %s",
            (now.strftime('%Y-%m-%d'), next_measure_date.strftime('%Y-%m-%d'), furnace_id)
        )
        
        return jsonify({"success": True, "message": "记录成功"}), 201
    except Exception as e:
        # 打印详细错误到后端控制台
        print(f"Error measuring furnace {furnace_id}: {e}")
        return jsonify({"error": str(e)}), 500

