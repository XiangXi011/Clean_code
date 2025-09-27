import pymysql
import os
import sys
from dotenv import load_dotenv
import datetime
import traceback

# 点位主数据，每日任务从此生成
LOCATIONS = {
    "层流棚": [
        "AR Line1: 17#", "AR Line1: 18#", "AR Line1: 20#", "AR Line1: 19#", "AR Line1: 4#", "AR Line1: 3#",
        "AR Line2: 7#", "AR Line2: 8#", "AR Line2: 9#", "AR Line2: 10#", "AR Line2: 14#", "AR Line2: 37#",
        "AR Line5: 22#", "AR Line5: 23#", "AR Line5: 24#", "AR Line5: 25#", "AR Line5: 26#", "AR Line5: 27#", "AR Line5: 28#",
        "AR Line6: 35#", "AR Line6: 34#", "AR Line6: 33#", "AR Line6: 32#", "AR Line6: 31#", "AR Line6: 30#", "AR Line6: 42#",
        "AR Line7: 46#", "AR Line7: 47#", "AR Line7: 48#", "AR Line7: 49#", "AR Line7: 50#", "AR Line7: 51#", "AR Line7: 45#", "AR Line7: 44#", "AR Line7: 43#", "AR Line7: 36#", "AR Line7: 29#", "AR Line7: 21#", "AR Line7: 6#", "AR Line7: 5#"
    ],
    "加硬机": [
        "1#加硬机: 点位1", "1#加硬机: 点位2", "1#加硬机: 点位3", "1#加硬机: 点位4", "1#加硬机: 点位5",
        "2#加硬机: 点位1", "2#加硬机: 点位2", "2#加硬机: 点位3", "2#加硬机: 点位4", "2#加硬机: 点位5",
        "3#加硬机: 点位1", "3#加硬机: 点位2", "3#加硬机: 点位3", "3#加硬机: 点位4", "3#加硬机: 点位5",
        "5#加硬机: 点位1", "5#加硬机: 点位2", "5#加硬机: 点位3", "5#加硬机: 点位4", "5#加硬机: 点位5",
        "6#加硬机: 点位1", "6#加硬机: 点位2", "6#加硬机: 点位3", "6#加硬机: 点位4", "6#加硬机: 点位5",
        "7#加硬机: 点位1", "7#加硬机: 点位2", "7#加硬机: 点位3", "7#加硬机: 点位4", "7#加硬机: 点位5"
    ],
    "大环境": [
        "AR Line1: 点位1", "AR Line1: 点位2", "AR Line1: 点位3", "AR Line1: 点位4", "AR Line1: 点位5",
        "AR Line2: 点位1", "AR Line2: 点位2", "AR Line2: 点位3", "AR Line2: 点位4", "AR Line2: 点位5",
        "AR Line5: 点位1", "AR Line5: 点位2", "AR Line5: 点位3", "AR Line5: 点位4", "AR Line5: 点位5",
        "AR Line6: 点位1", "AR Line6: 点位2", "AR Line6: 点位3", "AR Line6: 点位4", "AR Line6: 点位5",
        "AR Line7: 点位1", "AR Line7: 点位2", "AR Line7: 点位3", "AR Line7: 点位4", "AR Line7: 点位5"
    ]
}

# 每周每日的任务计划
# 0:周一, 1:周二, ..., 6:周日
WEEKLY_PLAN = {
    0: {"types": ["层流棚"], "furnace_count": 7},
    1: {"types": ["加硬机"], "furnace_count": 8},
    2: {"types": ["大环境"], "furnace_count": 8},
    3: {"types": ["层流棚"], "furnace_count": 7},
    4: {"types": ["加硬机", "大环境"], "furnace_count": 0},
    5: {"types": ["大环境"], "furnace_count": 14},
    6: {"types": [], "furnace_count": 0}, # 周日休息
}

def main():
    """
    主函数，用于连接数据库并为当天生成计划任务。
    这个脚本现在只生成非固化炉的日常任务。
    """
    conn = None
    try:
        # --- 配置和数据库连接 (已修改) ---
        load_dotenv()
        DB_HOST = os.getenv("DB_HOST")
        DB_PORT = int(os.getenv("DB_PORT", "3306"))
        DB_USER = os.getenv("DB_USER")
        DB_PASSWORD = os.getenv("DB_PASSWORD")
        DB_NAME = os.getenv("DB_NAME")

        conn = pymysql.connect(
            host=DB_HOST, user=DB_USER, password=DB_PASSWORD,
            database=DB_NAME, port=DB_PORT, charset="utf8mb4"
        )
        cursor = conn.cursor()
        print("✅ 数据库连接成功!")

        # --- 核心业务逻辑 (基本无变化) ---
        today = datetime.date.today()
        today_str = today.strftime('%Y-%m-%d')
        weekday = today.weekday()

        # 1. 检查当天任务是否已存在 (只检查非固化炉任务)
        cursor.execute("SELECT COUNT(*) FROM daily_tasks WHERE measure_date = %s AND location_type != '固化炉'", (today_str,))
        if cursor.fetchone()[0] > 0:
            print(f"ℹ️ {today_str} 的常规任务已经存在，无需重复生成。")
            return

        # 2. 获取当天的计划
        plan = WEEKLY_PLAN.get(weekday)
        if not plan or not plan.get("types"):
            print(f"ℹ️ 今天是 {today.strftime('%A')}，没有计划的常规任务。")
            return
        
        print(f"今天是 {today.strftime('%A')}，正在为您生成 {', '.join(plan['types'])} 任务...")

        tasks_to_insert = []
        
        # 3. 生成常规点位任务
        for location_type in plan.get("types", []):
            if location_type in LOCATIONS:
                for point_name in LOCATIONS[location_type]:
                    tasks_to_insert.append((today_str, location_type, point_name))
        
        # 4. 批量插入任务
        if tasks_to_insert:
            insert_query = "INSERT INTO daily_tasks (measure_date, location_type, point_name) VALUES (%s, %s, %s)"
            cursor.executemany(insert_query, tasks_to_insert)
            conn.commit()
            print(f"✅ 成功为 {today_str} 生成了 {cursor.rowcount} 条新的常规任务。")
        else:
            print("ℹ️ 今天没有需要生成的常规任务。")

    except pymysql.Error as err: # <-- 修改点
        print(f"❌ 数据库操作失败: {err}")
        if conn:
            conn.rollback() # 如果出错，进行回滚
        traceback.print_exc()
        sys.exit(1)
        
    except Exception as e:
        print(f"❌ 发生未知错误: {e}")
        if conn:
            conn.rollback()
        traceback.print_exc()
        sys.exit(1)

    finally:
        if conn: # <-- 修改点
            cursor.close()
            conn.close()
            print("🔌 数据库连接已关闭。")

if __name__ == "__main__":
    main()