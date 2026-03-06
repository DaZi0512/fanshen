/* ============================================================================
   高斯三维重建模型压缩与可视化系统 - 反主流美学交互脚本
   设计理念：深度交互、微动效、反主流用户体验
   ============================================================================ */

document.addEventListener('DOMContentLoaded', function() {
    console.log('GAUSS3D - 反主流美学系统已加载');

    // ============================================================================
    // 全局初始化
    // ============================================================================

    // 移除Flash消息的自动消失
    initFlashMessages();

    // 初始化工具提示
    initTooltips();

    // 初始化手绘动画
    initHandDrawnAnimations();

    // 初始化表单交互
    initFormInteractions();

    // 初始化文件上传区域
    initFileUpload();

    // 初始化范围滑块
    initRangeSliders();

    // ============================================================================
    // 页面特定初始化
    // ============================================================================

    // 3D查看器页面
    if (document.querySelector('.viewer-canvas')) {
        init3DViewer();
    }

    // 结果页面 - 指标动画
    if (document.querySelector('.metric-value')) {
        initMetricAnimations();
    }

    // 日志页面 - 确认对话框
    if (document.querySelector('.btn-danger')) {
        initConfirmDialogs();
    }

    // ============================================================================
    // 核心功能函数
    // ============================================================================

    /**
     * 初始化Flash消息交互
     */
    function initFlashMessages() {
        const flashMessages = document.querySelectorAll('.flash-message');

        flashMessages.forEach(flash => {
            // 添加点击关闭
            flash.addEventListener('click', function(e) {
                if (e.target.classList.contains('flash-close') ||
                    e.target.closest('.flash-close')) {
                    return;
                }
                this.style.opacity = '0';
                this.style.transform = 'translateY(-10px)';
                setTimeout(() => this.remove(), 300);
            });

            // 自动消失（8秒后）
            setTimeout(() => {
                flash.style.opacity = '0';
                flash.style.transform = 'translateY(-10px)';
                setTimeout(() => flash.remove(), 300);
            }, 8000);
        });
    }

    /**
     * 初始化工具提示
     */
    function initTooltips() {
        const tooltipElements = document.querySelectorAll('[data-tooltip]');

        tooltipElements.forEach(element => {
            element.addEventListener('mouseenter', function(e) {
                const tooltipText = this.getAttribute('data-tooltip');
                const tooltip = document.createElement('div');
                tooltip.className = 'custom-tooltip';
                tooltip.textContent = tooltipText;

                // 添加到body
                document.body.appendChild(tooltip);

                // 定位
                const rect = this.getBoundingClientRect();
                tooltip.style.left = `${rect.left + rect.width / 2 - tooltip.offsetWidth / 2}px`;
                tooltip.style.top = `${rect.top - tooltip.offsetHeight - 8}px`;
                tooltip.style.opacity = '1';

                // 保存引用
                this._tooltip = tooltip;
            });

            element.addEventListener('mouseleave', function() {
                if (this._tooltip) {
                    this._tooltip.remove();
                    this._tooltip = null;
                }
            });
        });

        // 添加工具提示样式
        const style = document.createElement('style');
        style.textContent = `
            .custom-tooltip {
                position: fixed;
                background: var(--color-dark);
                color: white;
                padding: 6px 12px;
                border-radius: var(--border-radius-sm);
                font-size: 0.85rem;
                z-index: 9999;
                pointer-events: none;
                opacity: 0;
                transition: opacity 0.2s;
                border: 1px solid var(--color-orange-primary);
                max-width: 200px;
                text-align: center;
                white-space: nowrap;
            }
            .custom-tooltip::after {
                content: '';
                position: absolute;
                top: 100%;
                left: 50%;
                transform: translateX(-50%);
                border-width: 4px;
                border-style: solid;
                border-color: var(--color-dark) transparent transparent transparent;
            }
        `;
        document.head.appendChild(style);
    }

    /**
     * 初始化手绘动画
     */
    function initHandDrawnAnimations() {
        // 为手绘元素添加随机动画
        const handDrawnElements = document.querySelectorAll('.hand-drawn-circle, .hand-drawn-dot');

        handDrawnElements.forEach(element => {
            // 随机初始位置偏移
            const randomX = Math.random() * 20 - 10;
            const randomY = Math.random() * 20 - 10;
            element.style.transform = `translate(${randomX}px, ${randomY}px)`;

            // 随机浮动动画
            const duration = 10 + Math.random() * 20;
            const delay = Math.random() * 5;

            element.style.animation = `float ${duration}s ease-in-out ${delay}s infinite`;
        });
    }

    /**
     * 初始化表单交互
     */
    function initFormInteractions() {
        // 输入框焦点效果
        const inputs = document.querySelectorAll('.form-input, .form-select, .form-textarea');

        inputs.forEach(input => {
            const container = input.closest('.form-group');

            input.addEventListener('focus', function() {
                if (container) {
                    container.classList.add('focused');
                }
            });

            input.addEventListener('blur', function() {
                if (container) {
                    container.classList.remove('focused');
                }
            });
        });

        // 表单验证提示
        const forms = document.querySelectorAll('form');
        forms.forEach(form => {
            form.addEventListener('submit', function(e) {
                const requiredFields = this.querySelectorAll('[required]');
                let isValid = true;

                requiredFields.forEach(field => {
                    if (!field.value.trim()) {
                        isValid = false;
                        highlightError(field);
                    } else {
                        removeError(field);
                    }
                });

                if (!isValid) {
                    e.preventDefault();
                    showFormError('请填写所有必填字段');
                }
            });
        });

        function highlightError(field) {
            field.style.borderColor = 'var(--color-error)';
            field.style.boxShadow = '0 0 0 3px rgba(244, 67, 54, 0.1)';

            let errorMsg = field.nextElementSibling;
            if (!errorMsg || !errorMsg.classList.contains('error-message')) {
                errorMsg = document.createElement('div');
                errorMsg.className = 'error-message';
                errorMsg.style.color = 'var(--color-error)';
                errorMsg.style.fontSize = '0.85rem';
                errorMsg.style.marginTop = '4px';
                errorMsg.textContent = '此字段为必填项';
                field.parentNode.appendChild(errorMsg);
            }
        }

        function removeError(field) {
            field.style.borderColor = '';
            field.style.boxShadow = '';

            const errorMsg = field.nextElementSibling;
            if (errorMsg && errorMsg.classList.contains('error-message')) {
                errorMsg.remove();
            }
        }

        function showFormError(message) {
            // 创建错误提示
            const errorDiv = document.createElement('div');
            errorDiv.className = 'flash-message flash-error';
            errorDiv.innerHTML = `
                <span class="flash-icon">
                    <i class="fas fa-exclamation-circle"></i>
                </span>
                <span class="flash-text">${message}</span>
                <button class="flash-close">
                    <i class="fas fa-times"></i>
                </button>
            `;

            // 添加到页面顶部
            const flashContainer = document.querySelector('.flash-container');
            if (flashContainer) {
                flashContainer.prepend(errorDiv);
            } else {
                document.querySelector('.main-content').prepend(errorDiv);
            }

            // 初始化新消息
            initFlashMessages();
        }
    }

    /**
     * 初始化文件上传区域
     */
    function initFileUpload() {
        const fileUploadAreas = document.querySelectorAll('.file-upload-area');

        fileUploadAreas.forEach(area => {
            const fileInput = area.querySelector('.file-input');
            const fileName = area.querySelector('.file-name');
            const fileLabel = area.querySelector('.file-label');

            if (!fileInput) return;

            // 点击区域触发文件选择
            area.addEventListener('click', function(e) {
                if (e.target !== fileLabel && !fileLabel.contains(e.target)) {
                    fileInput.click();
                }
            });

            // 拖放功能
            area.addEventListener('dragover', function(e) {
                e.preventDefault();
                this.classList.add('dragover');
            });

            area.addEventListener('dragleave', function() {
                this.classList.remove('dragover');
            });

            area.addEventListener('drop', function(e) {
                e.preventDefault();
                this.classList.remove('dragover');

                if (e.dataTransfer.files.length) {
                    fileInput.files = e.dataTransfer.files;
                    updateFileName();
                }
            });

            // 文件选择变化
            fileInput.addEventListener('change', updateFileName);

            function updateFileName() {
                if (fileInput.files.length) {
                    const file = fileInput.files[0];
                    const fileSize = formatFileSize(file.size);
                    fileName.innerHTML = `已选择: <strong>${file.name}</strong> (${fileSize})`;
                    fileName.style.color = 'var(--color-orange-primary)';
                } else {
                    fileName.innerHTML = '未选择文件';
                    fileName.style.color = 'var(--color-text-tertiary)';
                }
            }

            function formatFileSize(bytes) {
                if (bytes === 0) return '0 Bytes';
                const k = 1024;
                const sizes = ['Bytes', 'KB', 'MB', 'GB'];
                const i = Math.floor(Math.log(bytes) / Math.log(k));
                return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
            }
        });
    }

    /**
     * 初始化范围滑块
     */
    function initRangeSliders() {
        const rangeInputs = document.querySelectorAll('input[type="range"]');

        rangeInputs.forEach(range => {
            const valueDisplay = range.nextElementSibling;

            // 初始值显示
            if (valueDisplay && valueDisplay.classList.contains('range-value')) {
                valueDisplay.textContent = range.value;
            }

            // 值变化时更新显示
            range.addEventListener('input', function() {
                if (valueDisplay) {
                    valueDisplay.textContent = this.value;

                    // 添加微动效
                    valueDisplay.style.transform = 'scale(1.1)';
                    setTimeout(() => {
                        valueDisplay.style.transform = 'scale(1)';
                    }, 150);
                }
            });

            // 添加视觉反馈
            range.addEventListener('mousedown', function() {
                this.style.cursor = 'grabbing';
            });

            range.addEventListener('mouseup', function() {
                this.style.cursor = 'grab';
            });
        });
    }

    /**
     * 初始化3D查看器
     */
    function init3DViewer() {
        const canvas = document.querySelector('.viewer-canvas');
        if (!canvas) return;

        // 创建简单的旋转立方体动画
        let angle = 0;
        let animationId = null;

        function animateCube() {
            angle += 0.01;
            const x = Math.sin(angle) * 20;
            const y = Math.cos(angle) * 20;

            canvas.style.transform = `perspective(800px) rotateX(${y}deg) rotateY(${x}deg)`;
            animationId = requestAnimationFrame(animateCube);
        }

        // 开始动画
        animateCube();

        // 鼠标交互
        let isDragging = false;
        let lastX = 0;
        let lastY = 0;

        canvas.addEventListener('mousedown', function(e) {
            isDragging = true;
            lastX = e.clientX;
            lastY = e.clientY;
            this.style.cursor = 'grabbing';
        });

        document.addEventListener('mousemove', function(e) {
            if (!isDragging) return;

            const deltaX = e.clientX - lastX;
            const deltaY = e.clientY - lastY;

            angle += deltaX * 0.01;
            lastX = e.clientX;
            lastY = e.clientY;
        });

        document.addEventListener('mouseup', function() {
            isDragging = false;
            canvas.style.cursor = 'grab';
        });

        // 清理动画
        canvas._cleanup = function() {
            if (animationId) {
                cancelAnimationFrame(animationId);
            }
            document.removeEventListener('mousemove', arguments.callee);
            document.removeEventListener('mouseup', arguments.callee);
        };
    }

    /**
     * 初始化指标动画
     */
    function initMetricAnimations() {
        const metricValues = document.querySelectorAll('.metric-value');

        metricValues.forEach(metric => {
            const originalValue = metric.textContent;
            const isNumeric = /^[\d.]+$/.test(originalValue);

            if (isNumeric) {
                const targetValue = parseFloat(originalValue);
                let currentValue = 0;
                const duration = 1500;
                const steps = 60;
                const increment = targetValue / steps;
                let step = 0;

                function animate() {
                    if (step < steps) {
                        currentValue += increment;
                        metric.textContent = currentValue.toFixed(2);
                        step++;
                        setTimeout(animate, duration / steps);
                    } else {
                        metric.textContent = targetValue.toFixed(2);
                    }
                }

                // 延迟开始动画
                setTimeout(animate, 300);
            }
        });
    }

    /**
     * 初始化确认对话框
     */
    function initConfirmDialogs() {
        const dangerButtons = document.querySelectorAll('.btn-danger');

        dangerButtons.forEach(button => {
            if (button.tagName === 'A' &&
                (button.href.includes('/delete') || button.href.includes('/clear'))) {

                button.addEventListener('click', function(e) {
                    const action = this.textContent.toLowerCase();
                    const message = `确定要${action}吗？此操作不可撤销。`;

                    if (!confirm(message)) {
                        e.preventDefault();
                    }
                });
            }
        });
    }

    // ============================================================================
    // SuperSplat导入功能
    // ============================================================================
    if (typeof window.supersplatImport === 'undefined') {
        window.supersplatImport = {
            /**
             * 获取导入脚本
             */
            getImportScript: function() {
                fetch('/viewer/supersplat-import')
                    .then(response => response.json())
                    .then(data => {
                        if (data.import_script) {
                            // 显示导入脚本
                            this.showScriptModal(data.import_script, data.model_url);
                        } else if (data.error) {
                            alert('错误: ' + data.error);
                        }
                    })
                    .catch(error => {
                        console.error('导入失败:', error);
                        alert('获取导入脚本失败');
                    });
            },

            /**
             * 显示脚本模态框
             */
            showScriptModal: function(script, modelUrl) {
                // 创建模态框
                const modal = document.createElement('div');
                modal.className = 'supersplat-modal';
                modal.innerHTML = `
                    <div class="modal-content">
                        <div class="modal-header">
                            <h3><i class="fas fa-code"></i> SuperSplat 导入脚本</h3>
                            <button class="modal-close">&times;</button>
                        </div>
                        <div class="modal-body">
                            <p>将以下脚本复制到 SuperSplat 编辑器中：</p>
                            <pre><code>${script}</code></pre>
                            <p>或手动导入模型：</p>
                            <div class="model-url">
                                <strong>模型URL：</strong>
                                <code>${modelUrl}</code>
                                <button class="btn-copy" data-text="${modelUrl}">
                                    <i class="fas fa-copy"></i> 复制
                                </button>
                            </div>
                        </div>
                        <div class="modal-footer">
                            <button class="btn btn-secondary" onclick="window.supersplatImport.copyScript()">
                                <i class="fas fa-copy"></i> 复制脚本
                            </button>
                            <button class="btn btn-primary" onclick="window.supersplatModal.close()">
                                关闭
                            </button>
                        </div>
                    </div>
                `;

                // 样式
                const style = document.createElement('style');
                style.textContent = `
                    .supersplat-modal {
                        position: fixed;
                        top: 0;
                        left: 0;
                        width: 100%;
                        height: 100%;
                        background: rgba(0, 0, 0, 0.8);
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        z-index: 10000;
                    }
                    .modal-content {
                        background: var(--color-surface);
                        border-radius: var(--border-radius-lg);
                        width: 90%;
                        max-width: 600px;
                        max-height: 80vh;
                        overflow: hidden;
                        border: 1px solid var(--color-orange-primary);
                    }
                    .modal-header {
                        background: var(--color-surface-light);
                        padding: var(--space-md) var(--space-lg);
                        display: flex;
                        justify-content: space-between;
                        align-items: center;
                        border-bottom: 1px solid var(--color-medium-gray);
                    }
                    .modal-header h3 {
                        margin: 0;
                        color: var(--color-text-primary);
                        display: flex;
                        align-items: center;
                        gap: var(--space-sm);
                    }
                    .modal-close {
                        background: none;
                        border: none;
                        color: var(--color-text-tertiary);
                        font-size: 1.5rem;
                        cursor: pointer;
                        padding: 0;
                        width: 30px;
                        height: 30px;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        border-radius: var(--border-radius-sm);
                    }
                    .modal-close:hover {
                        background: rgba(255, 107, 53, 0.1);
                        color: var(--color-orange-primary);
                    }
                    .modal-body {
                        padding: var(--space-lg);
                        overflow-y: auto;
                        max-height: calc(80vh - 120px);
                    }
                    .modal-body pre {
                        background: var(--color-bg);
                        padding: var(--space-md);
                        border-radius: var(--border-radius-md);
                        overflow-x: auto;
                        margin: var(--space-md) 0;
                        border: 1px solid var(--color-medium-gray);
                    }
                    .modal-body code {
                        color: var(--color-orange-secondary);
                        font-family: 'Courier New', monospace;
                    }
                    .model-url {
                        background: var(--color-surface-light);
                        padding: var(--space-md);
                        border-radius: var(--border-radius-md);
                        margin-top: var(--space-md);
                        display: flex;
                        flex-wrap: wrap;
                        align-items: center;
                        gap: var(--space-sm);
                    }
                    .model-url code {
                        flex: 1;
                        word-break: break-all;
                        color: var(--color-text-secondary);
                    }
                    .btn-copy {
                        background: var(--color-surface);
                        border: 1px solid var(--color-medium-gray);
                        color: var(--color-text-secondary);
                        padding: var(--space-xs) var(--space-sm);
                        border-radius: var(--border-radius-sm);
                        cursor: pointer;
                        display: flex;
                        align-items: center;
                        gap: var(--space-xs);
                        font-size: 0.9rem;
                    }
                    .btn-copy:hover {
                        background: var(--color-orange-primary);
                        color: white;
                        border-color: var(--color-orange-primary);
                    }
                    .modal-footer {
                        padding: var(--space-md) var(--space-lg);
                        background: var(--color-surface-light);
                        border-top: 1px solid var(--color-medium-gray);
                        display: flex;
                        justify-content: flex-end;
                        gap: var(--space-md);
                    }
                `;

                document.head.appendChild(style);
                document.body.appendChild(modal);

                // 关闭按钮
                modal.querySelector('.modal-close').addEventListener('click', function() {
                    document.body.removeChild(modal);
                });

                // 点击背景关闭
                modal.addEventListener('click', function(e) {
                    if (e.target === modal) {
                        document.body.removeChild(modal);
                    }
                });

                // 复制URL按钮
                modal.querySelectorAll('.btn-copy').forEach(button => {
                    button.addEventListener('click', function() {
                        const text = this.getAttribute('data-text');
                        navigator.clipboard.writeText(text).then(() => {
                            const originalText = this.innerHTML;
                            this.innerHTML = '<i class="fas fa-check"></i> 已复制';
                            setTimeout(() => {
                                this.innerHTML = originalText;
                            }, 2000);
                        });
                    });
                });

                // 保存引用
                window.supersplatModal = {
                    close: function() {
                        document.body.removeChild(modal);
                    }
                };
            },

            /**
             * 复制脚本到剪贴板
             */
            copyScript: function() {
                const script = document.querySelector('.supersplat-modal code')?.textContent;
                if (script) {
                    navigator.clipboard.writeText(script).then(() => {
                        alert('脚本已复制到剪贴板');
                    });
                }
            }
        };
    }

    // ============================================================================
    // 全局键盘快捷键
    // ============================================================================
    document.addEventListener('keydown', function(e) {
        // Ctrl/Cmd + S - 保存（防止页面刷新）
        if ((e.ctrlKey || e.metaKey) && e.key === 's') {
            e.preventDefault();
            console.log('保存操作 - 在真实应用中这里会保存数据');
            // 这里可以触发自动保存功能
        }

        // Escape - 关闭所有模态框
        if (e.key === 'Escape') {
            const modals = document.querySelectorAll('.supersplat-modal');
            modals.forEach(modal => {
                document.body.removeChild(modal);
            });
        }
    });

    // ============================================================================
    // 页面切换动画
    // ============================================================================
    document.addEventListener('click', function(e) {
        const link = e.target.closest('a');
        if (link && link.href && link.href.startsWith(window.location.origin) &&
            !link.href.includes('#') && !link.getAttribute('target')) {

            e.preventDefault();

            // 添加页面淡出效果
            document.querySelector('.main-content').style.opacity = '0.5';
            document.querySelector('.main-content').style.transform = 'translateY(10px)';
            document.querySelector('.main-content').style.transition = 'all 0.3s ease';

            // 导航
            setTimeout(() => {
                window.location.href = link.href;
            }, 300);
        }
    });

    // ============================================================================
    // 性能监控
    // ============================================================================
    if ('performance' in window) {
        window.addEventListener('load', function() {
            setTimeout(() => {
                const perfData = performance.getEntriesByType('navigation')[0];
                if (perfData) {
                    console.log(`页面加载时间: ${perfData.loadEventEnd.toFixed(2)}ms`);
                }
            }, 0);
        });
    }
});

// ============================================================================
// 工具函数
// ============================================================================

/**
 * 格式化日期时间
 */
function formatDateTime(date) {
    return new Date(date).toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
    });
}

/**
 * 格式化文件大小
 */
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

/**
 * 生成随机ID
 */
function generateId(length = 8) {
    return Math.random().toString(36).substr(2, length);
}

/**
 * 防抖函数
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

/**
 * 节流函数
 */
function throttle(func, limit) {
    let inThrottle;
    return function(...args) {
        if (!inThrottle) {
            func.apply(this, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

// ============================================================================
// 全局错误处理
// ============================================================================
window.addEventListener('error', function(e) {
    console.error('全局错误:', e.error);
    // 在实际应用中，这里可以发送错误到监控服务
});

window.addEventListener('unhandledrejection', function(e) {
    console.error('未处理的Promise拒绝:', e.reason);
    // 在实际应用中，这里可以发送错误到监控服务
});

// ============================================================================
// 离线检测
// ============================================================================
window.addEventListener('online', function() {
    console.log('网络已连接');
    // 可以显示网络恢复通知
});

window.addEventListener('offline', function() {
    console.log('网络已断开');
    // 可以显示网络断开通知
});

// ============================================================================
// 导出全局对象
// ============================================================================
window.GAUSS3D = window.GAUSS3D || {};
Object.assign(window.GAUSS3D, {
    utils: {
        formatDateTime,
        formatFileSize,
        generateId,
        debounce,
        throttle
    }
});

console.log('GAUSS3D 交互系统初始化完成');