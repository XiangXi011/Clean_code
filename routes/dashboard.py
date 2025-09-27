from flask import Blueprint, jsonify
from db import query_db

dashboard_bp = Blueprint('dashboard_bp', __name__, url_prefix='/api/dashboard')

@dashboard_bp.route('/', methods=['GET'])
def get_dashboard_data():
    """获取看板数据，包括今日任务进度和本月固化炉测量进度"""
    try:
        # 获取今日任务进度 (包括所有类型的任务)
        daily_stats_query = query_db(
            """
            SELECT 
                COUNT(*) as total, 
                SUM(IF(status = '已完成', 1, 0)) as completed 
            FROM daily_tasks 
            WHERE DATE(measure_date) = CURDATE()
            """,
            one=True
        )
        daily_stats = {
            'total': daily_stats_query.get('total', 0) if daily_stats_query else 0,
            'completed': int(daily_stats_query.get('completed', 0) or 0) if daily_stats_query else 0
        }
        daily_stats['percentage'] = (daily_stats['completed'] / daily_stats['total'] * 100) if daily_stats['total'] > 0 else 0

        # 获取本月固化炉测量进度
        total_furnaces = query_db("SELECT COUNT(*) as total FROM furnaces", one=True)
        completed_furnaces = query_db(
            """
            SELECT COUNT(DISTINCT furnace_id) as completed 
            FROM results 
            WHERE furnace_id IS NOT NULL AND DATE_FORMAT(measure_time, '%%Y-%%m') = DATE_FORMAT(CURDATE(), '%%Y-%%m')
            """,
            one=True
        )

        furnace_stats = {
            'total': total_furnaces.get('total', 0) if total_furnaces else 0,
            'completed': completed_furnaces.get('completed', 0) if completed_furnaces else 0
        }
        furnace_stats['percentage'] = (furnace_stats['completed'] / furnace_stats['total'] * 100) if furnace_stats['total'] > 0 else 0
        
        return jsonify({'daily': daily_stats, 'furnace': furnace_stats})

    except Exception as e:
        print(f"Error fetching dashboard data: {e}")
        return jsonify({
            'daily': {'total': 0, 'completed': 0, 'percentage': 0},
            'furnace': {'total': 0, 'completed': 0, 'percentage': 0},
            'error': str(e)
        }), 500
