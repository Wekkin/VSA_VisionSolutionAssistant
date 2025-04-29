from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QStackedWidget, QFrame, QTextEdit, QFileDialog, QListWidget, QListWidgetItem, QComboBox, QGridLayout, QApplication, QScrollArea, QCheckBox, QLineEdit, QDialog, QMessageBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor, QIcon
import sys
import os
import json
from datetime import datetime

class StepBar(QWidget):
    def __init__(self, steps, current_step=0, parent=None):
        super().__init__(parent)
        self.steps = steps
        self.current_step = current_step
        self.layout = QHBoxLayout(self)  # 保存为实例变量
        self.layout.setSpacing(0)
        self.initUI()

    def setCurrentStep(self, idx):
        """更新当前步骤"""
        if idx != self.current_step:
            self.current_step = idx
            # 清除现有布局中的所有部件
            while self.layout.count():
                item = self.layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
            # 重新初始化UI
            self.initUI()

    def initUI(self):
        """初始化或更新UI"""
        for i, step in enumerate(self.steps):
            step_widget = QWidget()
            step_layout = QVBoxLayout(step_widget)
            step_layout.setContentsMargins(0, 0, 0, 0)
            
            # 圆形编号
            circle = QLabel(str(i+1) if i > self.current_step else '✓' if i < self.current_step else str(i+1))
            circle.setFixedSize(32, 32)
            circle.setAlignment(Qt.AlignCenter)
            circle.setFont(QFont('Arial', 14, QFont.Bold))
            
            # 设置圆形样式
            if i < self.current_step:  # 已完成的步骤
                circle.setStyleSheet('background:#e8e8e8;color:#8c8c8c;border-radius:16px;border:2px solid #e8e8e8;')
            elif i == self.current_step:  # 当前步骤
                circle.setStyleSheet('background:white;color:#1890ff;border-radius:16px;border:2px solid #1890ff;')
            else:  # 未开始的步骤
                circle.setStyleSheet('background:#f0f2f5;color:#bfbfbf;border-radius:16px;border:2px solid #e8e8e8;')
            
            # 步骤名称
            label = QLabel(step)
            label.setAlignment(Qt.AlignCenter)
            label.setFont(QFont('Arial', 10, QFont.Bold))
            
            # 设置文字样式
            if i < self.current_step:  # 已完成的步骤
                label.setStyleSheet('color:#8c8c8c;')
            elif i == self.current_step:  # 当前步骤
                label.setStyleSheet('color:#1890ff;')
            else:  # 未开始的步骤
                label.setStyleSheet('color:#bfbfbf;')
            
            step_layout.addWidget(circle)
            step_layout.addWidget(label)
            self.layout.addWidget(step_widget)
            
            # 连接线
            if i < len(self.steps) - 1:
                line = QFrame()
                line.setFixedHeight(2)
                line.setFixedWidth(40)
                if i < self.current_step:  # 已完成步骤之间的线
                    line.setStyleSheet('background:#e8e8e8;')
                else:  # 其他线
                    line.setStyleSheet('background:#f0f2f5;')
                self.layout.addWidget(line)
        
        self.layout.addStretch()

class RFQCheckStep(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.project_path = None  # 存储当前选择的项目路径
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)  # 设置整体边距
        
        # 项目选择区域
        project_layout = QHBoxLayout()
        project_layout.setSpacing(12)  # 设置按钮之间的间距
        
        project_label = QLabel("当前项目：")
        project_label.setStyleSheet("font-weight: bold;")
        
        self.project_path_label = QLabel("未选择")
        self.project_path_label.setStyleSheet("""
            color: #999;
            padding: 4px 8px;
            background: #f5f5f5;
            border-radius: 4px;
        """)
        
        # 选择项目按钮
        select_project_btn = QPushButton("选择项目")
        select_project_btn.setFixedHeight(32)  # 统一按钮高度
        select_project_btn.setStyleSheet("""
            QPushButton {
                background: #1890ff;
                color: white;
                padding: 4px 16px;
                border-radius: 4px;
                border: none;
            }
            QPushButton:hover {
                background: #40a9ff;
            }
        """)
        select_project_btn.clicked.connect(self.select_project)
        
        # 保存按钮
        save_btn = QPushButton('保存检查结果')
        save_btn.setFixedHeight(32)  # 统一按钮高度
        save_btn.setStyleSheet("""
            QPushButton {
                background: #52c41a;
                color: white;
                padding: 4px 16px;
                border-radius: 4px;
                border: none;
            }
            QPushButton:hover {
                background: #73d13d;
            }
            QPushButton:pressed {
                background: #389e0d;
            }
        """)
        save_btn.clicked.connect(self.save_check_results)
        
        project_layout.addWidget(project_label)
        project_layout.addWidget(self.project_path_label, stretch=1)
        project_layout.addWidget(select_project_btn)
        project_layout.addWidget(save_btn)
        layout.addLayout(project_layout)
        
        # 分隔线
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setStyleSheet("background-color: #e8e8e8;")
        layout.addWidget(separator)
        
        # 步骤标题
        title = QLabel('RFQ完整性检查')
        title.setFont(QFont('Arial', 18, QFont.Bold))
        layout.addWidget(title)
        
        # 创建滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: white;
            }
            QScrollBar:vertical {
                border: none;
                background: #f0f0f0;
                width: 8px;
                margin: 0px 0px 0px 0px;
            }
            QScrollBar::handle:vertical {
                background: #c1c1c1;
                min-height: 30px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical:hover {
                background: #a8a8a8;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
        
        # 创建内容容器
        content_widget = QWidget()
        self.content_layout = QVBoxLayout(content_widget)
        self.content_layout.setSpacing(8)  # 减小行间距
        
        # RFQ检查项列表
        self.check_items = [
            {"name": "项目名称", "required": True},
            {"name": "行业名称", "required": True},
            {"name": "是否新项目", "required": True},
            {"name": "预算情况", "required": True},
            {"name": "检测精度", "required": True},
            {"name": "节拍要求", "required": True},
            {"name": "产品种类", "required": True},
            {"name": "检测环境", "required": False},
            {"name": "安装空间", "required": False},
            {"name": "产品材质", "required": True},
            {"name": "产品尺寸", "required": True},
            {"name": "缺陷类型", "required": True},
            {"name": "最小缺陷尺寸", "required": True},
            {"name": "相机型号", "required": False},
            {"name": "光源要求", "required": False},
            {"name": "通讯协议", "required": False},
            {"name": "交付时间", "required": True},
            {"name": "客户联系人", "required": True}
        ]
        
        # 添加检查项
        for item in self.check_items:
            self.add_check_item(item)
        
        # 添加自定义检查项的按钮
        add_btn = QPushButton("+ 添加自定义检查项")
        add_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: #1890ff;
                border: none;
                padding: 8px;
                text-align: left;
            }
            QPushButton:hover {
                color: #40a9ff;
            }
        """)
        add_btn.clicked.connect(self.add_custom_item)
        self.content_layout.addWidget(add_btn)
        
        self.content_layout.addStretch()
        scroll_area.setWidget(content_widget)
        layout.addWidget(scroll_area, stretch=1)

    def add_check_item(self, item, is_custom=False):
        """添加检查项"""
        item_widget = QWidget()
        item_widget.setFixedHeight(50)  # 设置固定高度
        item_widget.setStyleSheet("""
            QWidget {
                background-color: #fafafa;
                border: 1px solid #e8e8e8;
                border-radius: 4px;
            }
            QWidget:hover {
                border-color: #40a9ff;
            }
        """)
        item_layout = QHBoxLayout(item_widget)
        item_layout.setContentsMargins(8, 0, 8, 0)  # 减小左右边距
        
        # 检查框和标签容器
        check_container = QWidget()
        check_layout = QHBoxLayout(check_container)
        check_layout.setContentsMargins(0, 0, 0, 0)
        check_container.setFixedWidth(130)  # 设置固定宽度
        
        # 检查框
        checkbox = QCheckBox()
        checkbox.setStyleSheet("""
            QCheckBox {
                background: transparent;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
            }
            QCheckBox::indicator:unchecked {
                border: 2px solid #d9d9d9;
                border-radius: 2px;
                background: white;
            }
            QCheckBox::indicator:checked {
                border: none;
                border-radius: 2px;
                background: #1890ff;
                image: url(icons/check.png);
            }
        """)
        
        # 标签
        label = QLabel(f"{item['name']}")
        if item['required']:
            label.setText(f"{item['name']} *")
            label.setStyleSheet("color: #262626; font-weight: bold;")
        else:
            label.setStyleSheet("color: #595959;")
        
        check_layout.addWidget(checkbox)
        check_layout.addWidget(label)
        check_layout.addStretch()
        
        # 备注输入框
        note_edit = QLineEdit()
        note_edit.setPlaceholderText("添加备注...")
        note_edit.setStyleSheet("""
            QLineEdit {
                border: 1px solid #d9d9d9;
                border-radius: 4px;
                padding: 4px 8px;
                background: white;
            }
            QLineEdit:focus {
                border-color: #40a9ff;
            }
        """)
        
        # 如果是自定义项，添加删除按钮
        if is_custom:
            delete_btn = QPushButton("×")
            delete_btn.setStyleSheet("""
                QPushButton {
                    color: #999;
                    border: none;
                    background: transparent;
                    font-size: 16px;
                    padding: 0 4px;
                }
                QPushButton:hover {
                    color: #ff4d4f;
                }
            """)
            delete_btn.clicked.connect(lambda: self.delete_custom_item(item_widget))
            item_layout.addWidget(check_container)
            item_layout.addWidget(note_edit, stretch=1)  # 让备注框占据剩余空间
            item_layout.addWidget(delete_btn)
        else:
            item_layout.addWidget(check_container)
            item_layout.addWidget(note_edit, stretch=1)  # 让备注框占据剩余空间
        
        self.content_layout.insertWidget(self.content_layout.count() - 2, item_widget)  # 插入到添加按钮之前

    def add_custom_item(self):
        """添加自定义检查项"""
        dialog = QDialog(self)
        dialog.setWindowTitle("添加自定义检查项")
        dialog.setFixedWidth(400)
        dialog.setStyleSheet("background-color: white;")
        
        layout = QVBoxLayout(dialog)
        
        # 名称输入
        name_edit = QLineEdit()
        name_edit.setPlaceholderText("输入检查项名称...")
        name_edit.setStyleSheet("""
            QLineEdit {
                border: 1px solid #d9d9d9;
                border-radius: 4px;
                padding: 8px;
                margin-bottom: 16px;
            }
            QLineEdit:focus {
                border-color: #40a9ff;
            }
        """)
        
        # 是否必填
        required_check = QCheckBox("设为必填项")
        required_check.setStyleSheet("""
            QCheckBox {
                color: #262626;
                margin-bottom: 16px;
            }
        """)
        
        # 按钮区
        btn_layout = QHBoxLayout()
        cancel_btn = QPushButton("取消")
        confirm_btn = QPushButton("确定")
        
        for btn in [cancel_btn, confirm_btn]:
            btn.setFixedWidth(80)
            btn.setStyleSheet("""
                QPushButton {
                    padding: 6px 0;
                    border-radius: 4px;
                }
            """)
        
        cancel_btn.setStyleSheet(cancel_btn.styleSheet() + """
            QPushButton {
                background: white;
                border: 1px solid #d9d9d9;
                color: #595959;
            }
            QPushButton:hover {
                border-color: #40a9ff;
                color: #40a9ff;
            }
        """)
        
        confirm_btn.setStyleSheet(confirm_btn.styleSheet() + """
            QPushButton {
                background: #1890ff;
                border: none;
                color: white;
            }
            QPushButton:hover {
                background: #40a9ff;
            }
        """)
        
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(confirm_btn)
        
        layout.addWidget(name_edit)
        layout.addWidget(required_check)
        layout.addLayout(btn_layout)
        
        cancel_btn.clicked.connect(dialog.reject)
        confirm_btn.clicked.connect(lambda: self.confirm_add_custom_item(
            dialog, name_edit.text(), required_check.isChecked()
        ))
        
        dialog.exec_()

    def confirm_add_custom_item(self, dialog, name, required):
        """确认添加自定义检查项"""
        if name.strip():
            self.add_check_item({"name": name, "required": required}, is_custom=True)
            dialog.accept()
        else:
            QMessageBox.warning(dialog, "提示", "请输入检查项名称")

    def delete_custom_item(self, item_widget):
        """删除自定义检查项"""
        self.content_layout.removeWidget(item_widget)
        item_widget.deleteLater()

    def select_project(self):
        """选择项目目录"""
        # 从主窗口获取默认项目路径
        default_path = ""
        main_window = self.window()
        if hasattr(main_window, 'settings_page'):
            settings_page = main_window.settings_page
            if hasattr(settings_page, 'get_project_path'):
                default_path = settings_page.get_project_path()
        
        if not default_path:
            # 如果没有设置默认路径，提示用户
            QMessageBox.warning(
                self,
                "提示",
                "请先在设置页面设置默认项目路径！",
                QMessageBox.Ok
            )
            # 切换到设置页面
            if hasattr(main_window, 'show_settings_page'):
                main_window.show_settings_page()
            return
        
        # 打开目录选择对话框，使用默认路径
        project_path = QFileDialog.getExistingDirectory(
            self,
            "选择项目目录",
            default_path,
            QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks
        )
        
        if project_path:
            self.project_path = project_path
            # 显示项目名称而不是完整路径
            self.project_path_label.setText(os.path.basename(project_path))
            self.project_path_label.setStyleSheet("""
                color: #262626;
                padding: 4px 8px;
                background: #f0f7ff;
                border: 1px solid #91caff;
                border-radius: 4px;
            """)
    
    def save_check_results(self):
        """保存检查结果"""
        if not self.project_path:
            QMessageBox.warning(self, "错误", "请先选择项目目录")
            return
            
        try:
            # 收集所有检查项的状态和备注
            results = []
            for i in range(self.content_layout.count() - 2):  # 减去添加按钮和stretch
                item_widget = self.content_layout.itemAt(i).widget()
                if isinstance(item_widget, QWidget):
                    checkbox = item_widget.findChild(QCheckBox)
                    label = item_widget.findChild(QLabel)
                    note_edit = item_widget.findChild(QLineEdit)
                    
                    if checkbox and label and note_edit:
                        results.append({
                            "name": label.text().replace(" *", ""),
                            "checked": checkbox.isChecked(),
                            "note": note_edit.text(),
                            "required": "*" in label.text()
                        })
            
            # 使用项目名称作为文件名
            project_name = os.path.basename(self.project_path)
            save_path = os.path.join(self.project_path, f"{project_name}_RFQ检查结果.json")
            
            # 保存结果到JSON文件
            with open(save_path, 'w', encoding='utf-8') as f:
                json.dump({
                    "project_name": project_name,
                    "check_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "items": results
                }, f, ensure_ascii=False, indent=2)
            
            QMessageBox.information(self, "成功", f"检查结果已保存到：\n{save_path}")
            
        except Exception as e:
            QMessageBox.warning(self, "错误", f"保存失败: {str(e)}")

class DefectMatrixStep(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        title = QLabel('缺陷矩阵生成')
        title.setFont(QFont('Arial', 18, QFont.Bold))
        layout.addWidget(title)
        # 表格占位
        table = QLabel('缺陷类型与检测参数表格（示意）')
        table.setStyleSheet('background:#fafafa;border:1px solid #e8e8e8;padding:32px;border-radius:8px;')
        layout.addWidget(table)
        layout.addStretch()

class ImageUploadStep(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        # 左侧缺陷类型列表
        defect_list = QListWidget()
        for name in ['表面划伤','凹坑','气泡','异物']:
            item = QListWidgetItem(f'📁 {name}')
            defect_list.addItem(item)
        defect_list.setFixedWidth(120)
        layout.addWidget(defect_list)
        # 中间拖拽上传区
        upload_area = QLabel('拖拽图片到此上传')
        upload_area.setAlignment(Qt.AlignCenter)
        upload_area.setStyleSheet('background:#fafafa;border:2px dashed #bfbfbf;border-radius:8px;font-size:16px;')
        layout.addWidget(upload_area, stretch=1)
        # 右侧缩略图区
        thumb_area = QLabel('缩略图预览区')
        thumb_area.setAlignment(Qt.AlignTop)
        thumb_area.setStyleSheet('background:#f5f5f5;border-radius:8px;padding:8px;')
        thumb_area.setFixedWidth(180)
        layout.addWidget(thumb_area)

class LightConfigStep(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        title = QLabel('光照配置')
        title.setFont(QFont('Arial', 18, QFont.Bold))
        layout.addWidget(title)
        form = QLabel('光源类型、角度、亮度等参数表单（示意）')
        form.setStyleSheet('background:#fafafa;border:1px solid #e8e8e8;padding:32px;border-radius:8px;')
        layout.addWidget(form)
        layout.addStretch()

class PPTGenStep(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        title = QLabel('自动生成PPT')
        title.setFont(QFont('Arial', 18, QFont.Bold))
        layout.addWidget(title)
        # 模板选择
        template_box = QComboBox()
        template_box.addItems(['标准模板','简洁模板','深色模板'])
        layout.addWidget(template_box, alignment=Qt.AlignLeft)
        # 图片缩略图区
        thumbs = QHBoxLayout()
        for _ in range(3):
            thumb = QLabel('缩略图')
            thumb.setFixedSize(120,90)
            thumb.setStyleSheet('background:#fafafa;border:1px solid #e8e8e8;border-radius:8px;')
            thumbs.addWidget(thumb)
        layout.addLayout(thumbs)
        # 预览/导出按钮
        btns = QHBoxLayout()
        preview_btn = QPushButton('预览PPT')
        export_btn = QPushButton('导出PPT')
        preview_btn.setStyleSheet('background:#f0f2f5;color:#1890ff;padding:6px 16px;border-radius:4px;')
        export_btn.setStyleSheet('background:#1890ff;color:white;padding:6px 16px;border-radius:4px;')
        btns.addWidget(preview_btn)
        btns.addWidget(export_btn)
        btns.addStretch()
        layout.addLayout(btns)
        layout.addStretch()

class RiskNoteStep(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        title = QLabel('风险备注与标注')
        title.setFont(QFont('Arial', 18, QFont.Bold))
        layout.addWidget(title)
        note = QTextEdit()
        note.setPlaceholderText('为每个缺陷类型添加风险说明、备注...')
        layout.addWidget(note)
        layout.addStretch()

class FolderCleanStep(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        title = QLabel('空文件夹清理')
        title.setFont(QFont('Arial', 18, QFont.Bold))
        layout.addWidget(title)
        info = QLabel('自动检测并列出所有空文件夹，支持一键清理或手动选择删除。')
        info.setStyleSheet('background:#fafafa;border:1px solid #e8e8e8;padding:32px;border-radius:8px;')
        layout.addWidget(info)
        layout.addStretch()

class POCGenerator(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.steps = [
            'RFQ完整性检查',
            '缺陷矩阵生成',
            '图片上传',
            '光照配置',
            '自动生成PPT',
            '风险备注与标注',
            '空文件夹清理'
        ]
        self.current_step = 0
        self.initUI()

    def initUI(self):
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(24, 24, 24, 24)
        # 顶部步骤条
        self.step_bar = StepBar(self.steps, self.current_step)
        main_layout.addWidget(self.step_bar)
        # 内容区
        self.stack = QStackedWidget()
        self.pages = [
            RFQCheckStep(),
            DefectMatrixStep(),
            ImageUploadStep(),
            LightConfigStep(),
            PPTGenStep(),
            RiskNoteStep(),
            FolderCleanStep()
        ]
        for page in self.pages:
            self.stack.addWidget(page)
        main_layout.addWidget(self.stack, stretch=1)
        # 底部按钮区
        btn_bar = QHBoxLayout()
        self.prev_btn = QPushButton('上一步')
        self.next_btn = QPushButton('下一步')
        self.prev_btn.setStyleSheet('background:#f0f2f5;color:#1890ff;padding:8px 32px;border-radius:4px;')
        self.next_btn.setStyleSheet('background:#1890ff;color:white;padding:8px 32px;border-radius:4px;')
        self.prev_btn.clicked.connect(self.prev_step)
        self.next_btn.clicked.connect(self.next_step)
        btn_bar.addStretch()
        btn_bar.addWidget(self.prev_btn)
        btn_bar.addWidget(self.next_btn)
        main_layout.addLayout(btn_bar)
        self.update_btn_state()

    def prev_step(self):
        if self.current_step > 0:
            self.current_step -= 1
            self.stack.setCurrentIndex(self.current_step)
            self.step_bar.setCurrentStep(self.current_step)
            self.update_btn_state()

    def next_step(self):
        if self.current_step < len(self.steps) - 1:
            self.current_step += 1
            self.stack.setCurrentIndex(self.current_step)
            self.step_bar.setCurrentStep(self.current_step)
            self.update_btn_state()

    def update_btn_state(self):
        self.prev_btn.setEnabled(self.current_step > 0)
        if self.current_step == len(self.steps) - 1:
            self.next_btn.setText('完成')
        else:
            self.next_btn.setText('下一步')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = POCGenerator()
    win.setWindowTitle('POC生成器')
    win.resize(1000, 700)
    win.show()
    sys.exit(app.exec_())
