#!/usr/bin/env python3
"""
测试应用基本功能
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    # 测试导入
    from app import app

    print("[[✓]] 应用导入成功")

    # 测试路由
    routes = []
    for rule in app.url_map.iter_rules():
        routes.append(rule.endpoint)

    print(f"[✓] 共找到 {len(routes)} 个路由")

    # 检查重要路由
    important_routes = [
        'index',
        'about',
        'register',
        'login',
        'dashboard',
        'upload',
        'result',
        'viewer',
        'upload_visualization',  # 新增的上传接口
        'supersplat_import'
    ]

    print("检查重要路由:")
    for route in important_routes:
        if route in routes:
            print(f"  [✓] {route}")
        else:
            print(f"  [✗] {route} (缺失)")

    # 检查配置
    print("\n检查应用配置:")
    print(f"  上传目录: {app.config.get('UPLOAD_FOLDER', '未设置')}")
    print(f"  可视化目录: {app.config.get('VISUALIZATIONS_FOLDER', '未设置')}")

    # 检查目录
    directories = [
        app.config.get('UPLOAD_FOLDER'),
        app.config.get('VISUALIZATIONS_FOLDER'),
        app.config.get('LOGS_FOLDER')
    ]

    print("\n检查目录权限:")
    for dir_path in directories:
        if dir_path:
            if os.path.exists(dir_path):
                print(f"  [✓] {dir_path} 存在")
                if os.access(dir_path, os.W_OK):
                    print(f"    [✓] 可写入")
                else:
                    print(f"    [✗] 不可写入")
            else:
                print(f"  [✗] {dir_path} 不存在")

    print("\n[✓] 测试完成！应用可以正常启动。")

except ImportError as e:
    print(f"[✗] 导入错误: {e}")
    print("请确保已安装依赖：pip install -r requirements.txt")
except Exception as e:
    print(f"[✗] 测试失败: {e}")
    import traceback
    traceback.print_exc()