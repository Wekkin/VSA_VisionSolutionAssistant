import sys
import os
import json
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                           QPushButton, QLabel, QScrollArea, QFrame, QLineEdit, QFileDialog,
                           QDialog, QFormLayout, QTextEdit, QMessageBox, QGridLayout,
                           QSpacerItem, QSizePolicy, QInputDialog)
from PyQt5.QtCore import Qt, QSize, QThread
from PyQt5.QtGui import QIcon, QFont, QColor
from utils.path_utils import get_resource_path

PLUGINS_CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'plugins.json')

class PluginRunnerThread(QThread):
    def __init__(self, cmd):
        super().__init__()
        self.cmd = cmd
    def run(self):
        import subprocess
        subprocess.Popen(self.cmd)

class PluginCard(QFrame):
    def __init__(self, name, description, script_path=None, is_dof=False, param_type=None, parent=None, delete_callback=None):
        super().__init__(parent)
        self.setFrameStyle(QFrame.StyledPanel)
        self.name = name
        self.description = description
        self.script_path = script_path
        self.is_dof = is_dof
        self.param_type = param_type
        self.delete_callback = delete_callback  # 新增：删除回调
        self.setup_ui(name, description)

    def setup_ui(self, name, description):
        self.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 8px;
                border: 1px solid #e8e8e8;
                padding: 16px;
                margin: 8px 0;
            }
            QFrame:hover {
                border-color: #1890ff;
                /* box-shadow: 0 2px 8px rgba(0, 0, 0, 0.09); */
            }
        """)
        layout = QVBoxLayout(self)
        top_layout = QHBoxLayout()
        name_label = QLabel(name)
        name_label.setFont(QFont("Arial", 14, QFont.Bold))
        top_layout.addWidget(name_label)
        top_layout.addStretch()
        # 运行按钮
        run_btn = QPushButton()
        run_btn.setIcon(QIcon(get_resource_path('icons/run.png')))
        run_btn.setIconSize(QSize(24, 24))
        run_btn.setToolTip("运行插件")
        run_btn.setStyleSheet("border:none;background:transparent;padding:4px;")
        run_btn.clicked.connect(self.run_plugin)
        # 设置按钮
        settings_btn = QPushButton()
        settings_btn.setIcon(QIcon(get_resource_path('icons/settings.png')))
        settings_btn.setIconSize(QSize(24, 24))
        settings_btn.setToolTip("设置插件")
        settings_btn.setStyleSheet("border:none;background:transparent;padding:4px;")
        settings_btn.clicked.connect(self.settings_plugin)
        # 删除按钮
        delete_btn = QPushButton()
        delete_btn.setIcon(QIcon(get_resource_path('icons/delete.png')))
        delete_btn.setIconSize(QSize(24, 24))
        delete_btn.setToolTip("删除插件")
        delete_btn.setStyleSheet("border:none;background:transparent;padding:4px;")
        delete_btn.clicked.connect(self.delete_plugin)
        top_layout.addWidget(run_btn)
        top_layout.addWidget(settings_btn)
        top_layout.addWidget(delete_btn)
        desc_label = QLabel(self.description)
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("color: #666666; margin-top: 8px;")
        layout.addLayout(top_layout)
        layout.addWidget(desc_label)
        layout.addStretch()

    def run_plugin(self):
        if self.is_dof:
            dlg = DOFDialog(self)
            dlg.exec_()
        elif self.script_path and os.path.exists(self.script_path):
            import subprocess
            args = []
            if self.param_type == 'folder':
                from PyQt5.QtWidgets import QFileDialog
                folder = QFileDialog.getExistingDirectory(self, "请选择要清理的主目录", "")
                if not folder:
                    QMessageBox.information(self, "提示", "未选择目录，已取消。")
                    return
                args.append(folder)
            try:
                print("[插件调试] 调用命令:", sys.executable, self.script_path, *args)
                # 判断是否为blender等长时间运行插件
                if self.script_path.endswith('blender_demo.py'):
                    self.plugin_thread = PluginRunnerThread([sys.executable, self.script_path] + args)
                    self.plugin_thread.start()
                    QMessageBox.information(self, "插件运行", "Blender插件已启动，窗口弹出后可交互操作。")
                else:
                    result = subprocess.run([sys.executable, self.script_path] + args, capture_output=True, text=True)
                    print("[插件调试] stdout:", result.stdout)
                    print("[插件调试] stderr:", result.stderr)
                    output = result.stdout.strip() or result.stderr.strip() or "(无输出)"
                    QMessageBox.information(self, "插件运行结果", output)
            except Exception as e:
                print(f"[插件调试] 运行脚本异常: {e}")
                QMessageBox.warning(self, "运行失败", f"运行脚本失败: {e}")
        else:
            print("[插件调试] 未找到插件脚本文件:", self.script_path)
            QMessageBox.warning(self, "运行失败", "未找到插件脚本文件")

    def settings_plugin(self):
        QMessageBox.information(self, "设置", f"这里可以设置插件：{self.name}")

    def delete_plugin(self):
        reply = QMessageBox.question(self, "删除插件", f"确定要删除插件：{self.name}？", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.setParent(None)
            self.deleteLater()
            if self.delete_callback:
                self.delete_callback(self)

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

class DOFDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("景深（DOF）计算器")
        self.setMinimumWidth(400)
        layout = QFormLayout(self)
        self.setStyleSheet("""
            QDialog {
                background: white;
            }
            QLineEdit, QTextEdit {
                font-size: 14px;
                border: 1px solid #d9d9d9;
                border-radius: 4px;
                padding: 6px;
            }
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
        self.wd_input = QLineEdit()
        self.f_input = QLineEdit()
        self.focal_input = QLineEdit()
        self.pixel_input = QLineEdit()
        layout.addRow("工作距离WD (mm):", self.wd_input)
        layout.addRow("光圈值F:", self.f_input)
        layout.addRow("焦距f (mm):", self.focal_input)
        layout.addRow("像元尺寸p (μm):", self.pixel_input)
        self.result = QTextEdit()
        self.result.setReadOnly(True)
        self.result.setMaximumHeight(100)
        layout.addRow("计算结果:", self.result)
        calc_btn = QPushButton("计算")
        calc_btn.clicked.connect(self.calculate)
        layout.addRow(calc_btn)
    def calculate(self):
        try:
            wd = float(self.wd_input.text())
            f_number = float(self.f_input.text())
            focal_length = float(self.focal_input.text())
            pixel_size_um = float(self.pixel_input.text())
            c_factor = 3
            pixel_size_mm = pixel_size_um / 1000
            c = c_factor * pixel_size_mm
            numerator = wd * f_number * c
            f_squared = focal_length ** 2
            denominator_front = f_squared + numerator
            dof_front = (numerator / denominator_front) * wd
            denominator_rear = f_squared - numerator
            if denominator_rear <= 0:
                dof_rear = float('inf')
                total_dof = float('inf')
            else:
                dof_rear = (numerator / denominator_rear) * wd
                total_dof = dof_front + dof_rear
            result_text = (
                f"前景深: {dof_front:.2f} mm\n"
                f"后景深: {'无限远' if dof_rear == float('inf') else f'{dof_rear:.2f} mm'}\n"
                f"总景深: {'无限远' if total_dof == float('inf') else f'{total_dof:.2f} mm'}"
            )
            self.result.setText(result_text)
        except Exception as e:
            self.result.setText(f"输入有误: {e}")

class ExtensionsWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("功能拓展模块")
        self.setup_ui()
        
    def setup_ui(self):
        self.setMinimumSize(1100, 800)
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        # 顶部标题区域
        title_layout = QHBoxLayout()
        title_label = QLabel("功能拓展模块")
        title_label.setFont(QFont("Arial", 20, QFont.Bold))
        title_layout.addWidget(title_label)
        title_layout.addStretch()
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
        title_layout.addWidget(add_plugin_btn)
        main_layout.addLayout(title_layout)
        # 插件列表区域
        self.plugins_widget = QWidget()
        self.plugins_layout = QVBoxLayout(self.plugins_widget)
        self.plugins_layout.setSpacing(16)
        self.plugin_cards = []
        self.load_plugins_from_cache()
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("QScrollArea { border: none; }")
        scroll_area.setWidget(self.plugins_widget)
        # 让scroll_area自动填满剩余空间
        main_layout.addWidget(scroll_area, stretch=1)
        # 绑定添加插件按钮
        add_plugin_btn.clicked.connect(self.add_plugin_flow)

    def add_plugin_flow(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "选择Python插件脚本", "", "Python Files (*.py)")
        if not file_path:
            return
        name, ok = QInputDialog.getText(self, "插件名称", "请输入插件名称：")
        if not ok or not name.strip():
            return
        # 参数类型选择（可扩展更多类型）
        param_type = None
        if 'clean_empty_folders' in os.path.basename(file_path):
            param_type = 'folder'
        self.add_plugin_card(name.strip(), f"自定义Python插件：{os.path.basename(file_path)}", script_path=file_path, param_type=param_type)
        self.save_plugins_to_cache()

    def add_plugin_card(self, name, desc, script_path=None, is_dof=False, param_type=None):
        card = PluginCard(name, desc, script_path=script_path, is_dof=is_dof, param_type=param_type, parent=self.plugins_widget, delete_callback=self.on_plugin_deleted)
        self.plugins_layout.addWidget(card)
        self.plugin_cards.append(card)

    def on_plugin_deleted(self, card):
        if card in self.plugin_cards:
            self.plugin_cards.remove(card)
            self.save_plugins_to_cache()

    def save_plugins_to_cache(self):
        plugins = []
        for card in self.plugin_cards:
            if card.is_dof:
                plugins.append({'name': card.name, 'desc': card.description, 'is_dof': True})
            else:
                plugins.append({'name': card.name, 'desc': card.description, 'script_path': card.script_path, 'param_type': card.param_type})
        with open(PLUGINS_CONFIG_PATH, 'w', encoding='utf-8') as f:
            json.dump(plugins, f, ensure_ascii=False, indent=2)

    def load_plugins_from_cache(self):
        self.plugin_cards.clear()
        # 清空布局
        while self.plugins_layout.count():
            item = self.plugins_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        # 加载缓存
        if os.path.exists(PLUGINS_CONFIG_PATH):
            with open(PLUGINS_CONFIG_PATH, 'r', encoding='utf-8') as f:
                plugins = json.load(f)
            for p in plugins:
                if p.get('is_dof'):
                    self.add_plugin_card(p['name'], p['desc'], is_dof=True)
                else:
                    self.add_plugin_card(p['name'], p['desc'], script_path=p.get('script_path'), param_type=p.get('param_type'))
        else:
            # 默认添加镜头景深计算器
            self.add_plugin_card("镜头景深计算器", "支持镜头景深（DOF）计算，适用于机器视觉应用。", is_dof=True)

    def show_api_settings(self):
        dialog = APISettingsDialog(self)
        dialog.exec_()

def main():
    app = QApplication(sys.argv)
    window = ExtensionsWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()