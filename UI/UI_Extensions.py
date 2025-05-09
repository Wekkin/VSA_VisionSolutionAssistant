import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                           QPushButton, QLabel, QScrollArea, QFrame, QLineEdit, QFileDialog,
                           QDialog, QFormLayout, QTextEdit, QMessageBox, QGridLayout,
                           QSpacerItem, QSizePolicy)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon, QFont, QColor
from utils.path_utils import get_resource_path

class PluginCard(QFrame):
    def __init__(self, name, description, is_enabled=False, parent=None):
        super().__init__(parent)
        self.setFrameStyle(QFrame.StyledPanel)
        self.setup_ui(name, description, is_enabled)
        
    def setup_ui(self, name, description, is_enabled):
        self.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 8px;
                border: 1px solid #e8e8e8;
                padding: 16px;
                margin: 8px;
            }
            QFrame:hover {
                border-color: #1890ff;
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.09);
            }
        """)
        
        layout = QVBoxLayout(self)
        
        # 顶部布局（标题和操作按钮）
        top_layout = QHBoxLayout()
        
        # 插件名称
        name_label = QLabel(name)
        name_label.setFont(QFont("Arial", 14, QFont.Bold))
        top_layout.addWidget(name_label)
        
        # 启用/禁用开关
        self.switch = QPushButton()
        self.switch.setCheckable(True)
        self.switch.setChecked(is_enabled)
        self.switch.setStyleSheet("""
            QPushButton {
                width: 50px;
                height: 24px;
                border-radius: 12px;
                background-color: #bfbfbf;
            }
            QPushButton:checked {
                background-color: #52c41a;
            }
        """)
        
        # 配置按钮
        config_btn = QPushButton("⚙")
        config_btn.setStyleSheet("""
            QPushButton {
                border: none;
                padding: 4px 8px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #f5f5f5;
            }
        """)
        
        # 删除按钮
        delete_btn = QPushButton("×")
        delete_btn.setStyleSheet("""
            QPushButton {
                border: none;
                padding: 4px 8px;
                border-radius: 4px;
                color: #ff4d4f;
            }
            QPushButton:hover {
                background-color: #fff1f0;
            }
        """)
        
        top_layout.addWidget(self.switch)
        top_layout.addWidget(config_btn)
        top_layout.addWidget(delete_btn)
        
        # 描述文本
        desc_label = QLabel(description)
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("color: #666666; margin-top: 8px;")
        
        layout.addLayout(top_layout)
        layout.addWidget(desc_label)

class APISettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("API 接口设置")
        self.setup_ui()
        
    def setup_ui(self):
        self.setMinimumWidth(400)
        layout = QFormLayout(self)
        
        # API名称
        self.name_input = QLineEdit()
        layout.addRow("API名称:", self.name_input)
        
        # Base URL
        self.url_input = QLineEdit()
        layout.addRow("Base URL:", self.url_input)
        
        # Token
        self.token_input = QLineEdit()
        self.token_input.setEchoMode(QLineEdit.Password)
        layout.addRow("Token:", self.token_input)
        
        # 测试连接按钮
        test_btn = QPushButton("测试连接")
        test_btn.setStyleSheet("""
            QPushButton {
                background-color: #1890ff;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #40a9ff;
            }
        """)
        
        # 保存按钮
        save_btn = QPushButton("保存")
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #52c41a;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #73d13d;
            }
        """)
        
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(test_btn)
        btn_layout.addWidget(save_btn)
        layout.addRow("", btn_layout)

class AddPythonExtensionDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("添加自定义 Python 功能")
        self.setup_ui()
        
    def setup_ui(self):
        self.setMinimumWidth(500)
        layout = QVBoxLayout(self)
        
        # 脚本名称
        name_layout = QHBoxLayout()
        name_label = QLabel("脚本名称:")
        self.name_input = QLineEdit()
        name_layout.addWidget(name_label)
        name_layout.addWidget(self.name_input)
        
        # 文件选择
        file_layout = QHBoxLayout()
        self.file_path = QLineEdit()
        self.file_path.setReadOnly(True)
        browse_btn = QPushButton("浏览")
        browse_btn.clicked.connect(self.browse_file)
        file_layout.addWidget(self.file_path)
        file_layout.addWidget(browse_btn)
        
        # 参数定义
        params_label = QLabel("参数定义 (可选):")
        self.params_input = QTextEdit()
        self.params_input.setPlaceholderText("每行一个参数，格式：参数名=默认值")
        self.params_input.setMaximumHeight(100)
        
        # 是否启用
        enable_layout = QHBoxLayout()
        enable_label = QLabel("是否启用:")
        self.enable_switch = QPushButton()
        self.enable_switch.setCheckable(True)
        self.enable_switch.setChecked(True)
        enable_layout.addWidget(enable_label)
        enable_layout.addWidget(self.enable_switch)
        enable_layout.addStretch()
        
        # 上传按钮
        upload_btn = QPushButton("上传")
        upload_btn.setStyleSheet("""
            QPushButton {
                background-color: #1890ff;
                color: white;
                border: none;
                padding: 8px 24px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #40a9ff;
            }
        """)
        
        layout.addLayout(name_layout)
        layout.addLayout(file_layout)
        layout.addWidget(params_label)
        layout.addWidget(self.params_input)
        layout.addLayout(enable_layout)
        layout.addWidget(upload_btn, alignment=Qt.AlignCenter)
        
    def browse_file(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self, "选择Python文件", "", "Python Files (*.py)"
        )
        if file_name:
            self.file_path.setText(file_name)

class ExtensionsWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("功能拓展模块")
        self.setup_ui()
        
    def setup_ui(self):
        self.setMinimumSize(1000, 800)
        
        # 主窗口部件
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        
        # 顶部标题区域
        title_layout = QHBoxLayout()
        title_label = QLabel("功能拓展模块")
        title_label.setFont(QFont("Arial", 20, QFont.Bold))
        
        # API设置按钮
        api_btn = QPushButton("API 接口设置")
        api_btn.setIcon(QIcon(get_resource_path("icons/api.png")))
        api_btn.clicked.connect(self.show_api_settings)
        api_btn.setStyleSheet("""
            QPushButton {
                background-color: white;
                border: 1px solid #d9d9d9;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                border-color: #1890ff;
                color: #1890ff;
            }
        """)
        
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        title_layout.addWidget(api_btn)
        
        # 添加插件按钮
        add_plugin_btn = QPushButton("+ 添加插件")
        add_plugin_btn.setStyleSheet("""
            QPushButton {
                background-color: #1890ff;
                color: white;
                border: none;
                padding: 8px 24px;
                border-radius: 4px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #40a9ff;
            }
        """)
        
        # 插件列表区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("QScrollArea { border: none; }")
        
        plugins_widget = QWidget()
        plugins_layout = QGridLayout(plugins_widget)
        plugins_layout.setSpacing(16)
        
        # 添加示例插件卡片
        plugins = [
            ("文档处理插件", "支持多种格式文档的读取、转换与处理功能", True),
            ("数据分析工具", "提供数据可视化与分析能力，支持多种图表类型", True),
            ("自动化工作流", "创建和管理自动化工作流程，提高工作效率", False),
            ("智能助手", "基于AI的智能对话与任务处理助手", True),
            ("团队协作", "增强团队协作功能，支持实时消息与任务分配", False),
            ("报表生成器", "自动生成各类业务报表，支持多种导出格式", True)
        ]
        
        for i, (name, desc, enabled) in enumerate(plugins):
            card = PluginCard(name, desc, enabled)
            row = i // 2
            col = i % 2
            plugins_layout.addWidget(card, row, col)
        
        scroll_area.setWidget(plugins_widget)
        
        # Python扩展按钮
        python_btn = QPushButton("添加自定义 Python 功能")
        python_btn.clicked.connect(self.show_python_dialog)
        python_btn.setStyleSheet("""
            QPushButton {
                background-color: #52c41a;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 4px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #73d13d;
            }
        """)
        
        main_layout.addLayout(title_layout)
        main_layout.addWidget(add_plugin_btn, alignment=Qt.AlignRight)
        main_layout.addWidget(scroll_area)
        main_layout.addWidget(python_btn, alignment=Qt.AlignCenter)
        
    def show_api_settings(self):
        dialog = APISettingsDialog(self)
        dialog.exec_()
        
    def show_python_dialog(self):
        dialog = AddPythonExtensionDialog(self)
        dialog.exec_()

def main():
    app = QApplication(sys.argv)
    window = ExtensionsWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()