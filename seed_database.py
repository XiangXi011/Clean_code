# 导入 mysql.connector 之前先尝试导入配置，这样可以先捕获配置错误
try:
    from config import Config
except ValueError as e:
    print(f"❌ 配置文件错误: {e}")
    print("   请立即检查您的 .env 文件格式是否正确，确保每个变量都独占一行。")
    exit() # 配置有误，直接退出

import mysql.connector
import traceback

# 这是您所有固化炉的“主列表”。
# 这个脚本的唯一目的，就是将这个列表一次性地导入到您的数据库中。
FURNACES = [
    "A02", "A06", "A07", "A10", "A11", "A12", "A13", "A14", "A15", "A16", "A18", "A21", "A22", "A24", "A25", "A27", "A29",
    "B01", "B02", "B03", "B04", "B05", "B06", "B07", "B08", "B09", "B10", "B11", "B12", "B13", "B14", "B15", "B16", "B17", "B18", "B19", "B20", "B21", "B22", "B23", "B24",
    "C01", "C02", "C03", "C04", "C05", "C06", "C07", "C08", "C09", "C10", "C11", "C12", "C13", "C14", "C15", "C16", "C17", "C18", "C19", "C20", "C21", "C22", "C23", "C24", "C25", "C26", "C27", "C28", "C29", "C30", "C31", "C32", "C33", "C34", "C35", "C36",
    "D01", "D02", "D03", "D04", "D05", "D06", "D07", "D08", "D09", "D10", "D11", "D12", "D13", "D14", "D15", "D16", "D17", "D18", "D19", "D20", "D21", "D22", "D23", "D24", "D25", "D26", "D27", "D28", "D29", "D30", "D31", "D32", "D33", "D34", "D35", "D36", "D37", "D38", "D39", "D40", "D41", "D42", "D43", "D44", "D45", "D46", "D47", "D48", "D49", "D50", "D51", "D52", "D53", "D54", "D55", "D56", "D57", "D58", "D59", "D60", "D61", "D62", "D63", "D64", "D65", "D66", "D67", "D68", "D69", "D70", "D71", "D72", "D73", "D74", "D75", "D76", "D77", "D78", "D79", "D80", "D81", "D82", "D83", "D84", "D85", "D86", "D87", "D88", "D89", "D90", "D91", "D92", "D93", "D94", "D95", "D96", "D97", "D98", "D99"
]

def main():
    """
    主函数，用于连接数据库并填充固化炉主数据。
    这是一个【一次性】的设置脚本，只需成功运行一次即可。
    """
    db_conn = None
    try:
        # 建立数据库连接
        db_conn = mysql.connector.connect(
            host=Config.DB_HOST,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            database=Config.DB_NAME,
            port=Config.DB_PORT
        )
        cursor = db_conn.cursor()
        print("✅ 数据库连接成功!")

        # 填充固化炉主数据
        print("正在填充固化炉主数据...")
        insert_furnace_query = "INSERT IGNORE INTO furnaces (name) VALUES (%s)"
        furnace_data = [(name,) for name in FURNACES]
        cursor.executemany(insert_furnace_query, furnace_data)
        db_conn.commit()
        print(f"✅ 完成! {cursor.rowcount} 条新的固化炉数据被插入。")
        print("   (如果数字为0，说明所有固化炉已存在于数据库中，这也是正常的)")
        
        print("\n🎉 数据库初始数据填充完毕！")

    except mysql.connector.Error as err:
        print(f"❌ 数据库连接或操作失败: {err}")
        print("   请仔细检查您的 .env 文件中的数据库地址、用户名、密码、数据库名是否正确，以及IP白名单是否已配置。")
        traceback.print_exc()
    finally:
        if db_conn and db_conn.is_connected():
            cursor.close()
            db_conn.close()
            print("🔌 数据库连接已关闭。")

if __name__ == "__main__":
    main()