# -*- coding: utf-8 -*-
"""
这个脚本的唯一目的就是找出 Python 导入 'config' 时，
实际加载的是哪个文件。
"""
import sys

print("--- 正在诊断 'config' 模块的来源 ---")
print(f"Python 解释器路径: {sys.executable}")
print("Python 会在以下路径中搜索模块 (sys.path):")
# 打印出当前目录，它应该是第一位的
print(f"  - 当前目录: {sys.path[0]}") 
print("  - ... 以及其他系统和库路径")

print("\n--- 尝试导入 'config' 模块... ---")

try:
    # 我们只导入模块本身，不导入里面的类
    import config
    
    print("\n✅ 成功导入 'config' 模块。")
    print(f"🔥 找到的文件路径是: {config.__file__}")
    print("\n💡 请检查上面的路径。如果它不是 'D:\\project code\\backend\\config.py'，那么你就找到了问题的根源！")

except ImportError:
    print("\n❌ 导入失败! 在所有搜索路径中都找不到 'config.py'。")
    print("   这不太可能发生，但如果出现，请确认 'config.py' 文件确实存在。")
except Exception as e:
    print(f"\n❌ 发生错误: {e}")