from flask import Blueprint, jsonify
from db import query_db
from datetime import datetime

dashboard_bp = Blueprint('dashboard_bp', __name__, url_prefix='/api/dashboard')

@dashboard_bp.route('/', methods=['GET'])
def get_dashboard_data():
    """获取看板所需的所有统计数据"""
    today_str = datetime.now().strftime('%Y-%m-%d')
    
    try:
        # 1. 今日任务进度
        daily_total_res = query_db("SELECT COUNT(*) as total FROM daily_tasks WHERE measure_date = %s", (today_str,), one=True)
        daily_completed_res = query_db("SELECT COUNT(*) as completed FROM daily_tasks WHERE measure_date = %s AND status = '已完成'", (today_str,), one=True)
        daily_total = daily_total_res['total'] if daily_total_res else 0
        daily_completed = daily_completed_res['completed'] if daily_completed_res else 0
        
        # 2. 本月固化炉进度
        furnace_total_res = query_db("SELECT COUNT(*) as total FROM furnaces", one=True)
        # 修复: 将 % 替换为 %% 以避免与 Python 的字符串格式化冲突
        furnace_completed_res = query_db("SELECT COUNT(*) as completed FROM furnaces WHERE DATE_FORMAT(last_measured, '%%Y-%%m') = DATE_FORMAT(CURDATE(), '%%Y-%%m')", one=True)
        furnace_total = furnace_total_res['total'] if furnace_total_res else 0
        furnace_completed = furnace_completed_res['completed'] if furnace_completed_res else 0
        
        # 3. 今日完成分类
        category_summary_res = query_db("""
            SELECT location_type, COUNT(*) as count
            FROM daily_tasks
            WHERE measure_date = %s AND status = '已完成'
            GROUP BY location_type
        """, (today_str,))
        
        category_summary = {item['location_type']: item['count'] for item in category_summary_res} if category_summary_res else {}
        # 确保所有类别都存在
        for cat in ['大环境', '层流棚', '加硬机']:
            if cat not in category_summary:
                category_summary[cat] = 0

        dashboard_data = {
            "dailyTotal": daily_total,
            "dailyCompleted": daily_completed,
            "dailyPercentage": (daily_completed / daily_total * 100) if daily_total > 0 else 0,
            "furnaceTotal": furnace_total,
            "furnaceCompleted": furnace_completed,
            "furnacePercentage": (furnace_completed / furnace_total * 100) if furnace_total > 0 else 0,
            "categorySummary": category_summary
        }

        return jsonify(dashboard_data)
    except Exception as e:
        # 打印详细错误到后端控制台，方便调试
        print(f"Error fetching dashboard data: {e}")
        return jsonify({"error": f"获取仪表盘数据失败: {e}"}), 500

