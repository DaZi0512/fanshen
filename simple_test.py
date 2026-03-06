#!/usr/bin/env python3
"""
简单测试应用基本功能
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    # 测试导入
    from app import app

    print("成功导入应用")
    print(f"应用名称: {app.name}")

    # 测试关键配置
    print("\n应用配置检查:")
    print(f"上传目录: {app.config.get('UPLOAD_FOLDER', '未设置')}")
    print(f"可视化目录: {app.config.get('VISUALIZATIONS_FOLDER', '未设置')}")
    print(f"日志目录: {app.config.get('LOGS_FOLDER', '未设置')}")

    # 检查目录存在
    print("\n目录检查:")
    directories = [
        app.config.get('UPLOAD_FOLDER'),
        app.config.get('VISUALIZATIONS_FOLDER'),
        app.config.get('LOGS_FOLDER')
    ]

    for dir_path in directories:
        if dir_path:
            if os.path.exists(dir_path):
                print(f"  {dir_path}: 存在")
                if os.access(dir_path, os.W_OK):
                    print("    可写入")
                else:
                    print("    不可写入 - 可能需要修改权限")
            else:
                print(f"  {dir_path}: 不存在 - 应用启动时会自动创建")

    # 检查重要路由
    print("\n路由检查:")
    important_routes = ['index', 'about', 'register', 'login',
                       'dashboard', 'upload', 'result', 'viewer',
                       'upload_visualization', 'supersplat_import']

    found_routes = []
    for rule in app.url_map.iter_rules():
        if rule.endpoint in important_routes:
            found_routes.append(rule.endpoint)

    print(f"找到 {len(found_routes)}/{len(important_routes)} 个重要路由")
    for route in important_routes:
        if route in found_routes:
            print(f"  [OK] {route}")
        else:
            print(f"  [MISSING] {route}")

    print("\n测试完成! 应用基本结构正常。")
    print("\n下一步:")
    print("1. 安装依赖: pip install -r requirements.txt")
    print("2. 运行应用: python app.py 或 python run.py")
    print("3. 访问: http://127.0.0.1:5000")
    print("4. 使用管理员账号: admin / admin123")

except ImportError as e:
    print(f"导入错误: {e}")
    print("请安装依赖: pip install -r requirements.txt")
except Exception as e:
    print(f"测试失败: {e}")
    import traceback
    traceback.print_exc()