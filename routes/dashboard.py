from flask import Blueprint, jsonify
from db import query_db

dashboard_bp = Blueprint('dashboard_bp', __name__, url_prefix='/api/dashboard')

@dashboard_bp.route('/', methods=['GET'])
def get_dashboard_data():
    """获取看板数据，包括今日任务进度和本月固化炉测量进度"""
    try:
        # 获取今日任务进度 - 修复了列名错误 (task_date -> measure_date)
        daily_stats_query = query_db(
            "SELECT COUNT(*) as total, SUM(IF(status = '已完成', 1, 0)) as completed FROM daily_tasks WHERE DATE(measure_date) = CURDATE()",
            one=True
        )
        # 如果查询结果为空，则提供默认值
        if not daily_stats_query or daily_stats_query.get('total') is None:
            daily_stats = {'total': 0, 'completed': 0}
        else:
            daily_stats = {
                'total': daily_stats_query.get('total', 0),
                'completed': int(daily_stats_query.get('completed', 0) or 0)
            }
        
        daily_stats['percentage'] = (daily_stats['completed'] / daily_stats['total'] * 100) if daily_stats['total'] > 0 else 0

        # 获取本月固化炉测量进度 - 使用 IF 替换 CASE 并转义 % 符号
        furnace_stats_query = query_db(
            "SELECT COUNT(*) as total, SUM(IF(last_measured IS NOT NULL AND DATE_FORMAT(last_measured, '%%Y-%%m') = DATE_FORMAT(CURDATE(), '%%Y-%%m'), 1, 0)) as completed FROM furnaces",
            one=True
        )
        # 如果查询结果为空，则提供默认值
        if not furnace_stats_query or furnace_stats_query.get('total') is None:
            furnace_stats = {'total': 0, 'completed': 0}
        else:
            furnace_stats = {
                'total': furnace_stats_query.get('total', 0),
                'completed': int(furnace_stats_query.get('completed', 0) or 0)
            }

        furnace_stats['percentage'] = (furnace_stats['completed'] / furnace_stats['total'] * 100) if furnace_stats['total'] > 0 else 0
        
        return jsonify({'daily': daily_stats, 'furnace': furnace_stats})

    except Exception as e:
        print(f"Error fetching dashboard data: {e}")
        # 即使发生异常，也返回一个默认的结构体，防止前端崩溃
        return jsonify({
            'daily': {'total': 0, 'completed': 0, 'percentage': 0},
            'furnace': {'total': 0, 'completed': 0, 'percentage': 0},
            'error': str(e)
        }), 500

