from flask import Blueprint, jsonify, request
from db import query_db
import datetime
import traceback

history_bp = Blueprint('history_bp', __name__)

@history_bp.route("/api/history", methods=['GET'])
def get_history():
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')
    if not start_date_str or not end_date_str:
        return jsonify({"error": "必须提供开始和结束日期"}), 400
    try:
        query = """
            SELECT r.result_id, r.measure_time, r.value_03, r.value_05, r.value_50,
                   COALESCE(dt.point_name, f.name, '未知点位') AS point_name,
                   COALESCE(dt.location_type, '固化炉') AS location_type
            FROM results r
            LEFT JOIN daily_tasks dt ON r.task_id = dt.task_id
            LEFT JOIN furnaces f ON r.furnace_id = f.furnace_id
            WHERE DATE(r.measure_time) BETWEEN %s AND %s
            ORDER BY r.measure_time DESC;
        """
        results = query_db(query, (start_date_str, end_date_str))
        for row in results:
            if isinstance(row['measure_time'], datetime.datetime):
                row['measure_time'] = row['measure_time'].strftime('%Y-%m-%d %H:%M:%S')
        return jsonify(results)
    except Exception as e:
        error_message = f"获取历史记录失败: {str(e)}"
        print(f"--- HISTORY ERROR --- \n{traceback.format_exc()} \n--- END ERROR ---")
        return jsonify({"error": error_message}), 500