import mysql.connector
from mysql.connector import Error
from datetime import date
import os
from dotenv import load_dotenv

# 加载环境变量
basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

# --- 从您的文件中提取的数据 ---
FURNACE_NAMES = [
    'A02', 'A06', 'A07', 'A10', 'A11', 'A12', 'A13', 'A14', 'A15', 'A16', 'A18', 'A21', 'A22', 'A24', 'A25', 'A27', 'A29',
    'B01', 'B02', 'B03', 'B04', 'B05', 'B06', 'B07', 'B08', 'B09', 'B10', 'B11', 'B12', 'B13', 'B14', 'B15', 'B16', 'B17', 'B18', 'B19', 'B20', 'B21', 'B22', 'B23', 'B24',
    'C01', 'C02', 'C03', 'C04', 'C05', 'C06', 'C07', 'C08', 'C09', 'C10', 'C11', 'C12', 'C13', 'C14', 'C15', 'C16', 'C17', 'C18', 'C19', 'C20', 'C21', 'C22', 'C23', 'C24', 'C25', 'C26', 'C27', 'C28', 'C29', 'C30', 'C31', 'C32', 'C33', 'C34', 'C35', 'C36',
    'D01', 'D02', 'D03', 'D04', 'D05', 'D06', 'D07', 'D08', 'D09', 'D10', 'D11', 'D12', 'D13', 'D14', 'D15', 'D16', 'D17', 'D18', 'D19', 'D20', 'D21', 'D22', 'D23', 'D24', 'D25', 'D26', 'D27', 'D28', 'D29', 'D30', 'D31', 'D32', 'D33', 'D34', 'D35', 'D36', 'D37', 'D38', 'D39', 'D40', 'D41', 'D42', 'D43', 'D44', 'D45', 'D46', 'D47', 'D48', 'D49', 'D50', 'D51', 'D52', 'D53', 'D54', 'D55', 'D56', 'D57', 'D58', 'D59', 'D60', 'D61', 'D62', 'D63', 'D64', 'D65', 'D66', 'D67', 'D68', 'D69', 'D70', 'D71', 'D72', 'D73', 'D74', 'D75', 'D76', 'D77', 'D78', 'D79', 'D80', 'D81', 'D82', 'D83', 'D84', 'D85', 'D86', 'D87', 'D88', 'D89', 'D90', 'D91', 'D92', 'D93', 'D94', 'D95', 'D96', 'D97', 'D98', 'D99'
]

DAILY_PLAN_POINTS = [
    # 大环境
    ("大环境", "AR Line1: 点位1"), ("大环境", "AR Line1: 点位2"), ("大环境", "AR Line1: 点位3"), ("大环境", "AR Line1: 点位4"), ("大环境", "AR Line1: 点位5"),
    ("大环境", "AR Line2: 点位1"), ("大环境", "AR Line2: 点位2"), ("大环境", "AR Line2: 点位3"), ("大环境", "AR Line2: 点位4"), ("大环境", "AR Line2: 点位5"),
    ("大环境", "AR Line5: 点位1"), ("大环境", "AR Line5: 点位2"), ("大环境", "AR Line5: 点位3"), ("大环境", "AR Line5: 点位4"), ("大环境", "AR Line5: 点位5"),
    ("大环境", "AR Line6: 点位1"), ("大环境", "AR Line6: 点位2"), ("大环境", "AR Line6: 点位3"), ("大环境", "AR Line6: 点位4"), ("大环境", "AR Line6: 点位5"),
    ("大环境", "AR Line7: 点位1"), ("大环境", "AR Line7: 点位2"), ("大环境", "AR Line7: 点位3"), ("大环境", "AR Line7: 点位4"), ("大环境", "AR Line7: 点位5"),
    # 层流棚
    ("层流棚", "AR Line1: 17#"), ("层流棚", "AR Line1: 18#"), ("层流棚", "AR Line1: 20#"), ("层流棚", "AR Line1: 19#"), ("层流棚", "AR Line1: 4#"), ("层流棚", "AR Line1: 3#"),
    ("层流棚", "AR Line2: 7#"), ("层流棚", "AR Line2: 8#"), ("层流棚", "AR Line2: 9#"), ("层流棚", "AR Line2: 10#"), ("层流棚", "AR Line2: 14#"), ("层流棚", "AR Line2: 37#"),
    ("层流棚", "AR Line5: 22#"), ("层流棚", "AR Line5: 23#"), ("层流棚", "AR Line5: 24#"), ("层流棚", "AR Line5: 25#"), ("层流棚", "AR Line5: 26#"), ("层流棚", "AR Line5: 27#"), ("层流棚", "AR Line5: 28#"),
    ("层流棚", "AR Line6: 35#"), ("层流棚", "AR Line6: 34#"), ("层流棚", "AR Line6: 33#"), ("层流棚", "AR Line6: 32#"), ("层流棚", "AR Line6: 31#"), ("层流棚", "AR Line6: 30#"), ("层流棚", "AR Line6: 42#"),
    ("层流棚", "AR Line7: 46#"), ("层流棚", "AR Line7: 47#"), ("层流棚", "AR Line7: 48#"), ("层流棚", "AR Line7: 49#"), ("层流棚", "AR Line7: 50#"), ("层流棚", "AR Line7: 51#"), ("层流棚", "AR Line7: 45#"), ("层流棚", "AR Line7: 44#"), ("层流棚", "AR Line7: 43#"), ("层流棚", "AR Line7: 36#"), ("层流棚", "AR Line7: 29#"), ("层流棚", "AR Line7: 21#"), ("层流棚", "AR Line7: 6#"), ("层流棚", "AR Line7: 5#"),
    # 加硬机
    ("加硬机", "1#加硬机: 点位1"), ("加硬机", "1#加硬机: 点位2"), ("加硬机", "1#加硬机: 点位3"), ("加硬机", "1#加硬机: 点位4"), ("加硬机", "1#加硬机: 点位5"),
    ("加硬机", "2#加硬机: 点位1"), ("加硬机", "2#加硬机: 点位2"), ("加硬机", "2#加硬机: 点位3"), ("加硬机", "2#加硬机: 点位4"), ("加硬机", "2#加硬机: 点位5"),
    ("加硬机", "3#加硬机: 点位1"), ("加硬机", "3#加硬机: 点位2"), ("加硬机", "3#加硬机: 点位3"), ("加硬机", "3#加硬机: 点位4"), ("加硬机", "3#加硬机: 点位5"),
    ("加硬机", "5#加硬机: 点位1"), ("加硬机", "5#加硬机: 点位2"), ("加硬机", "5#加硬机: 点位3"), ("加硬机", "5#加硬机: 点位4"), ("加硬机", "5#加硬机: 点位5"),
    ("加硬机", "6#加硬机: 点位1"), ("加硬机", "6#加硬机: 点位2"), ("加硬机", "6#加硬机: 点位3"), ("加硬机", "6#加硬机: 点位4"), ("加硬机", "6#加硬机: 点位5"),
    ("加硬机", "7#加硬机: 点位1"), ("加硬机", "7#加硬机: 点位2"), ("加硬机", "7#加硬机: 点位3"), ("加硬机", "7#加硬机: 点位4"), ("加硬机", "7#加硬机: 点位5"),
]

def get_db_connection():
    """建立数据库连接"""
    try:
        connection = mysql.connector.connect(
            host=os.getenv('DB_HOST'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            database=os.getenv('DB_NAME')
        )
        return connection
    except Error as e:
        print(f"数据库连接失败: {e}")
        return None

def seed_data():
    conn = get_db_connection()
    if conn is None:
        return
    
    cursor = conn.cursor()
    
    try:
        # 1. 填充固化炉
        print("正在填充 'furnaces' 表...")
        furnace_sql = "INSERT IGNORE INTO furnaces (name) VALUES (%s)"
        furnace_data = [(name,) for name in FURNACE_NAMES]
        cursor.executemany(furnace_sql, furnace_data)
        conn.commit()
        print(f"完成! {cursor.rowcount} 条新记录被插入。")
        
        # 2. 为今天创建每日计划
        print("\n正在为今天创建 'daily_tasks'...")
        today_str = date.today().strftime('%Y-%m-%d')
        
        # 检查今天是否已有任务，避免重复
        cursor.execute("SELECT COUNT(*) FROM daily_tasks WHERE measure_date = %s", (today_str,))
        if cursor.fetchone()[0] > 0:
            print("今天的任务已经存在，跳过创建。")
        else:
            task_sql = "INSERT INTO daily_tasks (measure_date, location_type, point_name) VALUES (%s, %s, %s)"
            task_data = [(today_str, loc_type, point_name) for loc_type, point_name in DAILY_PLAN_POINTS]
            cursor.executemany(task_sql, task_data)
            conn.commit()
            print(f"完成! 为今天创建了 {cursor.rowcount} 条任务。")

    except Error as e:
        print(f"数据填充时发生错误: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()
        print("\n数据库连接已关闭。")

if __name__ == '__main__':
    seed_data()


