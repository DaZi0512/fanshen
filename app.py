#!/usr/bin/env python3
"""
高斯三维重建模型压缩与可视化系统
基于Flask的Web应用，深灰+橙色配色，大留白，手绘风格元素
"""

import os
import sqlite3
import uuid
import time
import csv
import json
from datetime import datetime
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, send_file, abort
from flask import send_from_directory

# ============================================================================
# 应用配置
# ============================================================================
app = Flask(__name__)
app.config.update(
    SECRET_KEY=os.environ.get('SECRET_KEY', 'anti-mainstream-secret-key-2026'),
    UPLOAD_FOLDER='static/uploads',
    VISUALIZATIONS_FOLDER='static/visualizations',
    LOGS_FOLDER='logs',
    MAX_CONTENT_LENGTH=1 * 1024 * 1024 * 1024,  # 1GB
    DATABASE='database.db',
    ADMIN_USERNAME='admin',
    ADMIN_PASSWORD='admin123'  # 生产环境应使用环境变量
)

# 允许的文件扩展名
ALLOWED_EXTENSIONS = {'ply'}
IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff'}

# 确保目录存在
for folder in [app.config['UPLOAD_FOLDER'], app.config['VISUALIZATIONS_FOLDER'], app.config['LOGS_FOLDER']]:
    os.makedirs(folder, exist_ok=True)

# ============================================================================
# 数据库工具
# ============================================================================
def get_db():
    """获取数据库连接"""
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """初始化数据库"""
    with app.app_context():
        db = get_db()
        cursor = db.cursor()

        # 用户表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # 压缩任务表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS compression_run (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                model_name TEXT NOT NULL,
                similarity REAL NOT NULL,
                prune REAL NOT NULL,
                num_codes INTEGER NOT NULL,
                psnr REAL,
                ssim REAL,
                lpips REAL,
                before_mb REAL,
                after_mb REAL,
                ratio REAL,
                duration REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES user (id) ON DELETE CASCADE
            )
        ''')

        # 初始化日志文件
        log_file = os.path.join(app.config['LOGS_FOLDER'], 'logs.csv')
        if not os.path.exists(log_file):
            with open(log_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'id', 'username', 'model_name', 'similarity', 'prune', 'num_codes',
                    'psnr', 'ssim', 'lpips', 'before_mb', 'after_mb', 'ratio', 'duration', 'created_at'
                ])

        db.commit()

# ============================================================================
# 装饰器与工具函数
# ============================================================================
def login_required(f):
    """用户登录要求装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('请先登录以访问此页面', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """管理员登录要求装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_logged_in' not in session:
            flash('请以管理员身份登录', 'warning')
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

def allowed_file(filename):
    """检查文件扩展名是否允许"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def allowed_image_file(filename):
    """检查图片文件扩展名是否允许"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in IMAGE_EXTENSIONS

def simulate_compression(model_name, similarity, prune, num_codes):
    """模拟压缩过程，生成指标"""
    import random

    # 模拟处理时间
    time.sleep(random.uniform(1.5, 3.0))

    # 生成模拟指标
    base_size = random.uniform(50.0, 200.0)  # MB
    compressed_size = base_size * (1 - prune) * random.uniform(0.7, 0.9)

    return {
        'psnr': 30.0 + similarity * 5 + random.uniform(-2, 2),
        'ssim': 0.85 + similarity * 0.1 + random.uniform(-0.05, 0.05),
        'lpips': 0.1 - similarity * 0.05 + random.uniform(-0.02, 0.02),
        'before_mb': round(base_size, 2),
        'after_mb': round(compressed_size, 2),
        'ratio': round(base_size / compressed_size, 2) if compressed_size > 0 else 0,
        'duration': round(random.uniform(2.5, 4.5), 2)
    }

def log_compression(user_id, username, model_name, params, metrics):
    """记录压缩日志到CSV"""
    log_file = os.path.join(app.config['LOGS_FOLDER'], 'logs.csv')

    with open(log_file, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            str(uuid.uuid4())[:8],
            username,
            model_name,
            params['similarity'],
            params['prune'],
            params['num_codes'],
            metrics['psnr'],
            metrics['ssim'],
            metrics['lpips'],
            metrics['before_mb'],
            metrics['after_mb'],
            metrics['ratio'],
            metrics['duration'],
            datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        ])

# ============================================================================
# 路由：公开页面
# ============================================================================
@app.route('/')
def index():
    """首页"""
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    """用户注册"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()

        if not all([username, email, password]):
            flash('所有字段均为必填', 'error')
            return render_template('register.html')

        password_hash = generate_password_hash(password)

        try:
            db = get_db()
            cursor = db.cursor()
            cursor.execute(
                'INSERT INTO user (username, email, password_hash) VALUES (?, ?, ?)',
                (username, email, password_hash)
            )
            db.commit()
            flash('注册成功！请登录', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('用户名或邮箱已存在', 'error')
        except Exception as e:
            flash(f'注册失败: {str(e)}', 'error')

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """用户登录"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()

        db = get_db()
        cursor = db.cursor()
        cursor.execute('SELECT id, username, password_hash FROM user WHERE username = ?', (username,))
        user = cursor.fetchone()

        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            flash(f'欢迎回来，{user["username"]}！', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('用户名或密码错误', 'error')

    return render_template('login.html')

@app.route('/logout')
def logout():
    """用户退出"""
    session.clear()
    flash('已退出登录', 'info')
    return redirect(url_for('index'))

# ============================================================================
# 模板过滤器
# ============================================================================
@app.template_filter('datetimeformat')
def datetimeformat(value, format='%Y-%m-%d %H:%M:%S'):
    """格式化日期时间"""
    if isinstance(value, str):
        try:
            value = datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
        except:
            return value
    return value.strftime(format) if hasattr(value, 'strftime') else value

# ============================================================================
# 路由：需要登录的页面
# ============================================================================
@app.route('/dashboard')
@login_required
def dashboard():
    """用户控制台"""
    # 获取用户的最近任务
    db = get_db()
    cursor = db.cursor()
    cursor.execute('''
        SELECT * FROM compression_run
        WHERE user_id = ?
        ORDER BY created_at DESC
        LIMIT 10
    ''', (session['user_id'],))
    recent_tasks = cursor.fetchall()

    return render_template('dashboard.html', recent_tasks=recent_tasks)

@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    """模型上传"""
    if request.method == 'POST':
        if 'model_file' not in request.files:
            flash('未选择文件', 'error')
            return redirect(request.url)

        file = request.files['model_file']
        if file.filename == '':
            flash('未选择文件', 'error')
            return redirect(request.url)

        if file and allowed_file(file.filename):
            # 安全化文件名
            original_name = secure_filename(file.filename)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            safe_name = f"{session['username']}_{timestamp}_{original_name}"

            # 保存文件
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], safe_name)
            file.save(file_path)

            # 保存到会话
            session['uploaded_model'] = safe_name
            session['original_model_name'] = original_name

            flash('模型上传成功！', 'success')
            return redirect(url_for('settings'))
        else:
            flash('仅支持 .ply 格式文件', 'error')

    return render_template('upload.html')

@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    """参数设置"""
    if 'uploaded_model' not in session:
        flash('请先上传模型', 'warning')
        return redirect(url_for('upload'))

    if request.method == 'POST':
        try:
            similarity = float(request.form.get('similarity', 0.8))
            prune = float(request.form.get('prune', 0.5))
            num_codes = int(request.form.get('num_codes', 128))

            # 参数验证
            if not (0.70 <= similarity <= 0.95):
                flash('相似度应在 0.70 ~ 0.95 之间', 'error')
                return redirect(request.url)

            if not (0.30 <= prune <= 0.90):
                flash('剪枝率应在 0.30 ~ 0.90 之间', 'error')
                return redirect(request.url)

            if num_codes not in [64, 128, 256, 512, 1024, 2048]:
                flash('编码数应为预设值之一', 'error')
                return redirect(request.url)

            # 保存参数到会话
            session['compression_params'] = {
                'similarity': similarity,
                'prune': prune,
                'num_codes': num_codes
            }

            flash('参数设置完成！', 'success')
            return redirect(url_for('compress'))

        except ValueError:
            flash('参数格式错误', 'error')

    return render_template('settings.html')

@app.route('/clear-session-model', methods=['POST'])
@login_required
def clear_session_model():
    """清除会话中的模型数据"""
    session.pop('uploaded_model', None)
    session.pop('original_model_name', None)
    session.pop('compression_params', None)
    session.pop('last_run_id', None)
    session.pop('compression_metrics', None)
    flash('会话模型数据已清除', 'info')
    return redirect(url_for('dashboard'))

@app.route('/compress')
@login_required
def compress():
    """执行压缩"""
    if 'uploaded_model' not in session:
        flash('请先上传模型', 'warning')
        return redirect(url_for('upload'))

    if 'compression_params' not in session:
        flash('请先设置参数', 'warning')
        return redirect(url_for('settings'))

    # 获取参数
    model_name = session.get('original_model_name', '未知模型')
    params = session['compression_params']

    # 模拟压缩过程
    metrics = simulate_compression(model_name, params['similarity'], params['prune'], params['num_codes'])

    # 保存到数据库
    db = get_db()
    cursor = db.cursor()
    cursor.execute('''
        INSERT INTO compression_run
        (user_id, model_name, similarity, prune, num_codes, psnr, ssim, lpips, before_mb, after_mb, ratio, duration)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        session['user_id'], model_name, params['similarity'], params['prune'], params['num_codes'],
        metrics['psnr'], metrics['ssim'], metrics['lpips'], metrics['before_mb'],
        metrics['after_mb'], metrics['ratio'], metrics['duration']
    ))
    run_id = cursor.lastrowid
    db.commit()

    # 记录日志
    log_compression(
        session['user_id'], session['username'], model_name, params, metrics
    )

    # 保存到会话
    session['last_run_id'] = run_id
    session['compression_metrics'] = metrics

    flash('压缩完成！', 'success')
    return redirect(url_for('result'))

@app.route('/result')
@login_required
def result():
    """结果展示页"""
    if 'last_run_id' not in session:
        flash('请先执行压缩', 'warning')
        return redirect(url_for('dashboard'))

    # 获取最新压缩记录
    db = get_db()
    cursor = db.cursor()
    cursor.execute('''
        SELECT * FROM compression_run
        WHERE id = ? AND user_id = ?
    ''', (session['last_run_id'], session['user_id']))
    run = cursor.fetchone()

    if not run:
        flash('压缩记录不存在', 'error')
        return redirect(url_for('dashboard'))

    # 准备可视化数据
    visualizations = []
    vis_folder = app.config['VISUALIZATIONS_FOLDER']
    if os.path.exists(vis_folder):
        for i in range(1, 5):  # 模拟4个可视化图片
            visualizations.append({
                'name': f'visualization_{i}.png',
                'url': url_for('static', filename=f'visualizations/vis_{i}.png')
            })

    return render_template('result.html', run=run, visualizations=visualizations)

@app.route('/upload-visualization', methods=['POST'])
@login_required
def upload_visualization():
    """上传可视化图片"""
    # 检查文件
    if 'visualization_file' not in request.files:
        return jsonify({'error': '未选择文件'}), 400

    file = request.files['visualization_file']
    if file.filename == '':
        return jsonify({'error': '未选择文件'}), 400

    # 检查文件扩展名
    if not allowed_image_file(file.filename):
        return jsonify({'error': '不支持的文件格式，请上传PNG、JPG、GIF、BMP或TIFF格式的图片'}), 400

    # 获取索引（1-4）
    try:
        index = int(request.form.get('index', 1))
        if index < 1 or index > 4:
            return jsonify({'error': '索引必须在1-4之间'}), 400
    except ValueError:
        return jsonify({'error': '无效的索引参数'}), 400

    # 安全保存文件
    safe_filename = f'vis_{index}.png'  # 统一保存为PNG格式

    file_path = os.path.join(app.config['VISUALIZATIONS_FOLDER'], safe_filename)

    try:
        # 保存文件
        file.save(file_path)

        # 验证文件是否保存成功
        if not os.path.exists(file_path):
            return jsonify({'error': '文件保存失败'}), 500

        # 返回成功响应
        return jsonify({
            'success': True,
            'filename': safe_filename,
            'url': url_for('static', filename=f'visualizations/{safe_filename}'),
            'index': index,
            'message': '图片上传成功'
        })
    except Exception as e:
        return jsonify({'error': f'上传失败: {str(e)}'}), 500

@app.route('/logs')
@login_required
def logs():
    """日志查看页"""
    log_file = os.path.join(app.config['LOGS_FOLDER'], 'logs.csv')
    log_data = []

    if os.path.exists(log_file):
        with open(log_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            log_data = list(reader)

            # 转换数值字段类型
            numeric_fields = ['similarity', 'prune', 'psnr', 'ssim', 'lpips', 'before_mb', 'after_mb', 'ratio', 'duration']
            int_fields = ['num_codes']

            for log in log_data:
                # 转换浮点数字段
                for field in numeric_fields:
                    if field in log and log[field]:
                        try:
                            log[field] = float(log[field])
                        except (ValueError, TypeError):
                            log[field] = 0.0

                # 转换整数字段
                for field in int_fields:
                    if field in log and log[field]:
                        try:
                            log[field] = int(log[field])
                        except (ValueError, TypeError):
                            log[field] = 0

    return render_template('logs.html', logs=log_data)

@app.route('/logs/delete/<int:line_num>')
@login_required
def delete_log(line_num):
    """删除单条日志"""
    log_file = os.path.join(app.config['LOGS_FOLDER'], 'logs.csv')

    if not os.path.exists(log_file):
        flash('日志文件不存在', 'error')
        return redirect(url_for('logs'))

    # 读取所有行
    with open(log_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # 检查行号有效性（跳过表头）
    if 1 <= line_num < len(lines):
        # 删除指定行
        del lines[line_num]

        # 重新写入
        with open(log_file, 'w', encoding='utf-8') as f:
            f.writelines(lines)

        flash('日志删除成功', 'success')
    else:
        flash('无效的行号', 'error')

    return redirect(url_for('logs'))

@app.route('/logs/clear')
@login_required
def clear_logs():
    """清空日志"""
    log_file = os.path.join(app.config['LOGS_FOLDER'], 'logs.csv')

    # 重建日志文件（只保留表头）
    with open(log_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            'id', 'username', 'model_name', 'similarity', 'prune', 'num_codes',
            'psnr', 'ssim', 'lpips', 'before_mb', 'after_mb', 'ratio', 'duration', 'created_at'
        ])

    flash('日志已清空', 'success')
    return redirect(url_for('logs'))

@app.route('/logs/export')
@login_required
def export_logs():
    """导出日志为Excel"""
    import pandas as pd

    log_file = os.path.join(app.config['LOGS_FOLDER'], 'logs.csv')
    export_file = os.path.join(app.config['LOGS_FOLDER'], 'report.xlsx')

    if not os.path.exists(log_file):
        flash('日志文件不存在', 'error')
        return redirect(url_for('logs'))

    try:
        # 读取CSV并导出为Excel
        df = pd.read_csv(log_file)
        df.to_excel(export_file, index=False)

        return send_file(export_file, as_attachment=True, download_name='compression_report.xlsx')
    except Exception as e:
        flash(f'导出失败: {str(e)}', 'error')
        return redirect(url_for('logs'))

@app.route('/viewer')
@login_required
def viewer():
    """3D查看页"""
    return render_template('viewer.html',
                          has_model='uploaded_model' in session,
                          model_name=session.get('original_model_name', ''))

@app.route('/api/local-visualizations')
@login_required
def local_visualizations():
    """获取本地可视化资源API"""
    visualizations = []
    vis_folder = app.config['VISUALIZATIONS_FOLDER']

    if os.path.exists(vis_folder):
        # 模拟返回可视化文件列表
        for i in range(1, 5):
            visualizations.append({
                'name': f'visualization_{i}',
                'url': url_for('static', filename=f'visualizations/vis_{i}.png')
            })

    return jsonify({
        'model_name': session.get('original_model_name', '未知模型'),
        'visualizations': visualizations
    })

@app.route('/viewer/supersplat-import')
@login_required
def supersplat_import():
    """SuperSplat导入元数据"""
    if 'uploaded_model' not in session:
        return jsonify({'error': '无上传模型'}), 400

    model_url = url_for('static', filename=f"uploads/{session['uploaded_model']}", _external=True)

    return jsonify({
        'model_url': model_url,
        'editor_url': 'https://superspl.at/editor',
        'import_script': f"""
// 自动导入脚本
const modelData = {{
    url: '{model_url}',
    name: '{session.get('original_model_name', 'model')}',
    format: 'ply'
}};
// 这里可以调用SuperSplat API进行自动导入
console.log('导入模型:', modelData);
"""
    })

# ============================================================================
# 路由：管理员页面
# ============================================================================
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """管理员登录"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()

        if username == app.config['ADMIN_USERNAME'] and password == app.config['ADMIN_PASSWORD']:
            session['admin_logged_in'] = True
            flash('管理员登录成功', 'success')
            return redirect(url_for('admin_users'))
        else:
            flash('管理员账号或密码错误', 'error')

    return render_template('admin/login.html')

@app.route('/admin/users')
@admin_required
def admin_users():
    """管理员页面 - 用户与任务列表"""
    db = get_db()
    cursor = db.cursor()

    # 获取用户列表
    cursor.execute('SELECT id, username, email, created_at FROM user ORDER BY created_at DESC')
    users = cursor.fetchall()

    # 获取最近20条压缩任务
    cursor.execute('''
        SELECT cr.*, u.username
        FROM compression_run cr
        JOIN user u ON cr.user_id = u.id
        ORDER BY cr.created_at DESC
        LIMIT 20
    ''')
    recent_tasks = cursor.fetchall()

    return render_template('admin/users.html', users=users, tasks=recent_tasks)

@app.route('/admin/delete-user/<int:user_id>')
@admin_required
def delete_user(user_id):
    """删除用户及其关联任务"""
    db = get_db()
    cursor = db.cursor()

    # 检查是否为当前登录用户
    if 'user_id' in session and session['user_id'] == user_id:
        # 清除用户会话
        session.pop('user_id', None)
        session.pop('username', None)

    # 删除用户（外键级联删除会同时删除关联的压缩记录）
    cursor.execute('DELETE FROM user WHERE id = ?', (user_id,))
    db.commit()

    flash('用户删除成功', 'success')
    return redirect(url_for('admin_users'))

@app.route('/admin/logout')
def admin_logout():
    """管理员退出"""
    session.pop('admin_logged_in', None)
    flash('管理员已退出', 'info')
    return redirect(url_for('admin_login'))

# ============================================================================
# 错误处理
# ============================================================================
@app.errorhandler(404)
def page_not_found(e):
    """404错误页"""
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    """500错误页"""
    import uuid
    return render_template('500.html',
                          error_id=f"SERVER-{uuid.uuid4().hex[:8]}",
                          now=datetime.now()), 500

# ============================================================================
# 静态文件路由
# ============================================================================
@app.route('/static/uploads/<filename>')
def uploaded_file(filename):
    """提供上传的文件"""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# ============================================================================
# 启动应用
# ============================================================================
if __name__ == '__main__':
    # 初始化数据库
    init_db()

    # 生成一些模拟可视化图片的占位符
    vis_folder = app.config['VISUALIZATIONS_FOLDER']
    for i in range(1, 5):
        placeholder_path = os.path.join(vis_folder, f'vis_{i}.png')
        if not os.path.exists(placeholder_path):
            # 在实际项目中这里应该生成或复制实际的图片
            # 现在只创建空文件作为占位
            open(placeholder_path, 'w').close()

    print("=" * 60)
    print("高斯三维重建模型压缩与可视化系统")
    print("三维重建压缩与可视化系统")
    print("=" * 60)
    print("访问地址: http://127.0.0.1:5000")
    print("管理员账号: admin / admin123")
    print("=" * 60)

    app.run(debug=True, host='0.0.0.0', port=5000)