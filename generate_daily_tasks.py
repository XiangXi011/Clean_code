import pymysql
import os
import sys
from datetime import datetime
from dotenv import load_dotenv
import traceback

def get_all_points():
    """从之前填充的主数据中获取所有点位信息"""
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
    # 【重要修改】将SQL语句中的 %Y 和 %m 转义为 %%Y 和 %%m
    # 这样 pymysql 在格式化时会将其正确处理为字面上的 '%' 字符
    query = """
        SELECT furnace_id, name 
        FROM furnaces 
        WHERE last_measured IS NULL OR DATE_FORMAT(last_measured, '%%Y-%%m') != DATE_FORMAT(CURDATE(), '%%Y-%%m')
        ORDER BY last_measured ASC, furnace_id ASC
        LIMIT %s
    """
    cursor.execute(query, (limit,))
    furnaces = cursor.fetchall()
    # 将 (id, name) 元组转换为点位名称
    return [f[1] for f in furnaces]

def main():
    # --- 日期和计划定义部分 (无需修改) ---
    today = datetime.now()
    day_of_week = today.weekday() # weekday() 返回 0 (周一) 到 6 (周日)
    today_str = today.strftime('%Y-%m-%d')
    
    weekly_plan = {
        0: (['层流棚'], 7),          # 周一
        1: (['加硬机'], 8),          # 周二
        2: (['大环境'], 8),          # 周三
        3: (['层流棚'], 7),          # 周四
        4: (['加硬机', '大环境'], 0), # 周五
        5: (['大环境'], 14),         # 周六
        6: ([], 0),                  # 周日 (无任务)
    }
    
    # 修正：根据今天的日期来决定星期几，而不是硬编码
    # 您运行代码时是周五晚上，但脚本判断的是周六的任务
    # today = datetime.now() 
    # 为了测试周六的情况，我们可以手动设置日期
    # from datetime import date
    # today = date(2025, 9, 27)
    
    day_name = today.strftime('%A')

    if day_of_week not in weekly_plan or (not weekly_plan[day_of_week][0] and not weekly_plan[day_of_week][1]):
        print(f"今天是 {day_name}，没有计划的测量任务。")
        return

    # --- 数据库连接和操作部分 (已修改) ---
    conn = None
    try:
        # 加载.env文件
        load_dotenv()
        print("✅ .env 文件已加载")
        
        # 从环境变量读取配置
        DB_HOST = os.getenv("DB_HOST")
        DB_PORT = int(os.getenv("DB_PORT", "3306"))
        DB_USER = os.getenv("DB_USER")
        DB_PASSWORD = os.getenv("DB_PASSWORD")
        DB_NAME = os.getenv("DB_NAME")
        
        # 建立数据库连接 (使用 pymysql)
        print("📌 正在连接数据库...")
        conn = pymysql.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            port=DB_PORT,
            charset="utf8mb4"
        )
        cursor = conn.cursor()
        print("✅ 数据库连接成功!")

        # 检查今天是否已经生成过任务，避免重复
        cursor.execute("SELECT COUNT(*) FROM daily_tasks WHERE measure_date = %s", (today_str,))
        count = cursor.fetchone()[0]
        if count > 0:
            print(f"{today_str} 的任务已经存在，无需重复生成。")
            return
            
        print(f"今天是 {day_name}，正在为 {today_str} 生成测量任务...")

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
            # 异常捕获已改为 pymysql.Error
            try:
                cursor.executemany(sql, tasks_to_insert)
                conn.commit()
                print(f"\n成功！总共为 {today_str} 创建了 {cursor.rowcount} 条任务。")
            except pymysql.Error as err:
                print(f"数据库插入失败: {err}")
                conn.rollback()
        else:
            print("今天没有需要生成的任务。")

    except pymysql.Error as err:
        print(f"数据库处理时发生错误: {err}")
        traceback.print_exc()
        sys.exit(1)
    except Exception as e:
        print(f"发生未知错误: {e}")
        traceback.print_exc()
        sys.exit(1)
    finally:
        # 确保数据库连接最后被关闭
        if conn:
            conn.close()
            print("🔒 数据库连接已关闭。")

if __name__ == '__main__':
    main()