# -*- coding: utf-8 -*-

print("--- A. 开始执行 check_config.py 文件 ---")

try:
    print("--- B. 准备从 config 模块导入 Config 类 ---")
    
    # 这一行是关键
    from config import Config
    
    print("--- C. 成功从 config 模块导入 Config 类 ---")
    
    app_config = Config()
    
    print("\n✅ 成功! 配置导入成功。")
    print(f"   - DEBUG 模式: {app_config.DEBUG}")

except ImportError as e:
    print(f"\n❌ 失败! 导入时出错: {e}")
    print("\n💡 错误分析:")
    print("   如果终端只显示了 'A' 和 'B'，然后就报错，说明 Python 找到了 config.py 文件，")
    print("   但在文件内部执行时，没能成功定义 'Config' 类，或者在定义完成前就出了问题。")
    print("   这通常是由于 'config.py' 内部又尝试导入了其他模块，从而引发了循环导入。")

except Exception as e:
    print(f"\n🔥 发生了一个意料之外的错误: {e}")