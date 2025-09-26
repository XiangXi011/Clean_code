import mysql.connector
from datetime import datetime
from config import Config
import sys

def get_db_connection():
    """获取数据库连接"""
    try:
        conn = mysql.connector.connect(
            host=Config.DB_HOST,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            database=Config.DB_NAME,
            port=Config.DB_PORT
        )
        return conn
    except mysql.connector.Error as err:
        print(f"数据库连接失败: {err}")
        sys.exit(1)

def get_all_points():
    """从之前填充的主数据中获取所有点位信息"""
    # 这里我们硬编码点位信息，因为它们是固定的
    # 在更复杂的系统中，这些也可以从数据库的"master data"表中读取
    points = {
        '大环境': [
            f"AR Line{line}: 点位{p}" for line in [1, 2, 5, 6, 7] for p in range(1, 6)
        ],
        '层流棚': [
            'AR Line1: 17#', 'AR Line1: 18#', 'AR Line1: 20#', 'AR Line1: 19#', 'AR Line1: 4#', 'AR Line1: 3#',
            'AR Line2: 7#', 'AR Line2: 8#', 'AR Line2: 9#', 'AR Line2: 10#', 'AR Line2: 14#', 'AR Line2: 37#',
            'AR Line5: 22#', 'AR Line5: 23#', 'AR Line5: 24#', 'AR Line5: 25#', 'AR Line5: 26#', 'AR Line5: 27#', 'AR Line5: 28#',
            'AR Line6: 35#', 'AR Line6: 34#', 'AR Line6: 33#', 'AR Line6: 32#', 'AR Line6: 31#', 'AR Line6: 30#', 'AR Line6: 42#',
            'AR Line7: 46#', 'AR Line7: 47#', 'AR Line7: 48#', 'AR Line7: 49#', 'AR Line7: 50#', 'AR Line7: 51#', 'AR Line7: 45#', 'AR Line7: 44#', 'AR Line7: 43#', 'AR Line7: 36#', 'AR Line7: 29#', 'AR Line7: 21#', 'AR Line7: 6#', 'AR Line7: 5#'
        ],
        '加硬机': [
            f"{j}#加硬机: 点位{p}" for j in [1, 2, 3, 5, 6, 7] for p in range(1, 6)
        ]
    }
    return points

def get_pending_furnaces(cursor, limit):
    """获取最需要测量的N个固化炉"""
    query = """
        SELECT furnace_id, name 
        FROM furnaces 
        WHERE last_measured IS NULL OR DATE_FORMAT(last_measured, '%Y-%m') != DATE_FORMAT(CURDATE(), '%Y-%m')
        ORDER BY last_measured ASC, furnace_id ASC
        LIMIT %s
    """
    cursor.execute(query, (limit,))
    furnaces = cursor.fetchall()
    # 将 (id, name) 元组转换为点位名称
    return [f[1] for f in furnaces]

def main():
    today = datetime.now()
    # weekday() 返回 0 (周一) 到 6 (周日)
    day_of_week = today.weekday()
    today_str = today.strftime('%Y-%m-%d')
    
    # 定义每周计划
    # 格式: (点位任务类型列表, 固化炉任务数量)
    weekly_plan = {
        0: (['层流棚'], 7),          # 周一
        1: (['加硬机'], 8),          # 周二
        2: (['大环境'], 8),          # 周三
        3: (['层流棚'], 7),          # 周四
        4: (['加硬机', '大环境'], 0), # 周五
        5: (['大环境'], 14),         # 周六
        6: ([], 0),                 # 周日 (无任务)
    }

    if day_of_week not in weekly_plan or not weekly_plan[day_of_week][0] and not weekly_plan[day_of_week][1]:
        print(f"今天是 {today.strftime('%A')}，没有计划的测量任务。")
        return

    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 检查今天是否已经生成过任务，避免重复
    cursor.execute("SELECT COUNT(*) FROM daily_tasks WHERE measure_date = %s", (today_str,))
    if cursor.fetchone()[0] > 0:
        print(f"{today_str} 的任务已经存在，无需重复生成。")
        cursor.close()
        conn.close()
        return
        
    print(f"今天是 {today.strftime('%A')}，正在为 {today_str} 生成测量任务...")

    all_points = get_all_points()
    tasks_to_insert = []
    
    task_types_today, furnace_count_today = weekly_plan[day_of_week]
    
    # 1. 生成点位任务
    for task_type in task_types_today:
        if task_type in all_points:
            for point_name in all_points[task_type]:
                tasks_to_insert.append((today_str, task_type, point_name))
            print(f"- 已生成 {len(all_points[task_type])} 个 '{task_type}' 任务。")
            
    # 2. 生成固化炉任务
    if furnace_count_today > 0:
        furnace_points = get_pending_furnaces(cursor, furnace_count_today)
        for point_name in furnace_points:
            tasks_to_insert.append((today_str, '固化炉', point_name))
        print(f"- 已生成 {len(furnace_points)} 个 '固化炉' 任务。")

    # 3. 批量插入数据库
    if tasks_to_insert:
        sql = "INSERT INTO daily_tasks (measure_date, location_type, point_name) VALUES (%s, %s, %s)"
        try:
            cursor.executemany(sql, tasks_to_insert)
            conn.commit()
            print(f"\n成功！总共为 {today_str} 创建了 {cursor.rowcount} 条任务。")
        except mysql.connector.Error as err:
            print(f"数据库插入失败: {err}")
            conn.rollback()
    else:
        print("今天没有需要生成的任务。")

    cursor.close()
    conn.close()

if __name__ == '__main__':
    main()
