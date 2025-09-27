from flask import Blueprint, jsonify, request
from db import query_db
import datetime
import traceback

furnaces_bp = Blueprint('furnaces_bp', __name__)

@furnaces_bp.route("/api/furnaces/all_status", methods=['GET'])
def get_all_furnaces_status():
    """
    获取所有固化炉的列表，并标记本月是否已测量。
    """
    try:
        # 使用 CASE 语句直接在SQL中判断本月是否测量过
        query = """
            SELECT
                furnace_id,
                name,
                last_measured,
                CASE
                    WHEN DATE_FORMAT(last_measured, '%Y-%m') = DATE_FORMAT(CURDATE(), '%Y-%m')
                    THEN 1
                    ELSE 0
                END AS measured_this_month
            FROM furnaces
            ORDER BY name;
        """
        results = query_db(query, args=None)   # 或 args=()
        # 格式化日期以便JSON序列化
        for row in results:
            if isinstance(row['last_measured'], datetime.date):
                row['last_measured'] = row['last_measured'].strftime('%Y-%m-%d')
        
        return jsonify(results)
    except Exception as e:
        error_message = f"获取所有固化炉状态失败: {str(e)}"
        print(f"--- FURNACES ALL STATUS ERROR --- \n{traceback.format_exc()} \n--- END ERROR ---")
        return jsonify({"error": error_message}), 500


@furnaces_bp.route("/api/furnaces/<int:furnace_id>/record", methods=['POST'])
def record_furnace_result(furnace_id):
    """记录一个固化炉的测量结果 (这个接口与之前相同)"""
    data = request.get_json()
    if not data or 'value_03' not in data or 'value_05' not in data or 'value_50' not in data:
        return jsonify({"error": "请求数据不完整"}), 400
    try:
        update_query = "UPDATE furnaces SET last_measured = CURDATE() WHERE furnace_id = %s"
        query_db(update_query, (furnace_id,), commit=True)

        insert_query = """
            INSERT INTO results (furnace_id, measure_time, value_03, value_05, value_50, operator)
            VALUES (%s, NOW(), %s, %s, %s, %s)
        """
        params = (
            furnace_id,
            data['value_03'], data['value_05'], data['value_50'],
            data.get('operator', 'default_user')
        )
        query_db(insert_query, params, commit=True)
        
        return jsonify({"message": f"成功记录固化炉 {furnace_id} 的测量结果"}), 201
    except Exception as e:
        error_message = f"记录固化炉结果失败: {str(e)}"
        print(f"--- FURNACE RECORD ERROR --- \n{traceback.format_exc()} \n--- END ERROR ---")
        return jsonify({"error": error_message}), 500

