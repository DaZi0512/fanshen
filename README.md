# GAUSS3D - 三维重建压缩与可视化系统

一个专业的三维重建模型压缩与可视化系统，为高斯点云模型的压缩、质量评估和可视化提供完整解决方案。

## 主要功能

- **用户认证与权限管理**：注册、登录、会话管理
- **模型上传**：支持PLY格式的三维点云模型上传
- **参数配置**：相似度阈值、剪枝率、编码数量等参数设置
- **模拟压缩**：生成PSNR、SSIM、LPIPS、压缩比等质量指标
- **结果可视化**：原始渲染、压缩后渲染、深度图、深度中位图显示
- **图片上传**：支持用户上传本地可视化图片
- **SuperSplat集成**：与SuperSplat 3D编辑器无缝对接
- **日志管理**：记录、查看、导出压缩任务历史
- **管理员功能**：用户管理、任务监控

## 技术栈

- **后端**：Flask + SQLite
- **前端**：自定义CSS设计（深灰+橙色配色，大留白，手绘风格元素）
- **可视化**：Canvas + SuperSplat集成
- **数据处理**：模拟压缩算法生成指标数据

## 安装和运行

1. **安装依赖**：
   ```bash
   pip install -r requirements.txt
   ```

2. **运行应用**：
   ```bash
   python run.py
   # 或直接运行
   python app.py
   ```

3. **访问应用**：
   - 打开浏览器访问：http://127.0.0.1:5000
   - 管理员账号：admin / admin123

## 图片上传功能

系统支持上传4种类型的可视化图片：

1. **原始渲染** - 原始模型渲染结果
2. **压缩后渲染** - 压缩后模型渲染结果
3. **深度图** - 深度信息可视化
4. **深度中位图** - 深度中位数分析图

上传方式：
1. 执行压缩任务后进入结果页面
2. 点击"上传可视化图片"按钮
3. 选择图片类型（1-4）
4. 选择图片文件（支持PNG、JPG、GIF、BMP、TIFF格式）
5. 点击上传，图片将保存到系统中

## SuperSplat 集成

系统与SuperSplat 3D编辑器集成：
1. 上传模型后，在3D查看页面
2. 点击"获取导入脚本"生成SuperSplat导入代码
3. 或直接访问：https://superspl.at/editor

## 项目结构

```
d:\claude\
├── app.py                 # 主应用文件
├── run.py                 # 启动脚本
├── requirements.txt       # Python依赖
├── README.md             # 说明文档
├── database.db           # SQLite数据库（运行后生成）
├── logs/                 # 日志目录
│   ├── logs.csv         # 压缩任务日志
│   └── report.xlsx      # Excel导出文件
├── static/               # 静态文件
│   ├── css/             # 样式文件
│   ├── images/          # 图片资源
│   ├── js/              # JavaScript文件
│   ├── uploads/         # 上传的PLY模型
│   └── visualizations/  # 可视化图片
├── templates/            # HTML模板
│   ├── base.html        # 基础模板
│   ├── index.html       # 首页
│   ├── about.html       # 关于页面
│   ├── register.html    # 注册页面
│   ├── login.html       # 登录页面
│   ├── dashboard.html   # 用户控制台
│   ├── upload.html      # 模型上传
│   ├── settings.html    # 参数设置
│   ├── result.html      # 结果展示
│   ├── viewer.html      # 3D查看页面
│   ├── logs.html        # 日志页面
│   └── admin/           # 管理员页面
└── memory/              # 系统记忆存储
```

## 设计特点

- **配色方案**：深灰+橙色主色调，拒绝千篇一律的紫色和蓝色
- **布局风格**：大留白设计，给内容呼吸的余地
- **设计元素**：手绘风格装饰元素，为冰冷的数字界面注入人情味
- **响应式设计**：适配桌面和移动设备

## 注意事项

- 当前版本使用模拟压缩算法生成指标数据
- 在实际生产环境中，这里会连接真实的高斯点云压缩算法后端服务
- 上传的图片文件大小限制为5MB
- 确保static/uploads和static/visualizations目录有写入权限

## 管理员功能

- 查看所有用户列表
- 查看最近压缩任务
- 删除用户及其关联任务
- 系统使用情况监控

## 故障排除

如果遇到问题：
1. 检查Python版本（推荐3.8+）
2. 确保所有依赖已安装：`pip install -r requirements.txt`
3. 检查数据库文件权限：确保对database.db有读写权限
4. 检查上传目录权限：确保static/uploads和static/visualizations目录可写
5. 查看应用控制台输出的错误信息