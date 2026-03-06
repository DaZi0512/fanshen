#!/usr/bin/env python3
"""
启动脚本 - 高斯三维重建模型压缩与可视化系统
"""
import os
import sys

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from app import app, init_db

    print("正在初始化数据库...")
    init_db()

    print("启动应用...")
    app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=False)

except ImportError as e:
    print(f"导入错误: {e}")
    print("请确保已安装依赖：")
    print("  pip install -r requirements.txt")
except Exception as e:
    print(f"启动失败: {e}")
    import traceback
    traceback.print_exc()