from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                            QLabel, QLineEdit, QFileDialog, QGroupBox, QMessageBox)
from PyQt5.QtCore import Qt, QTimer
from utils.logger import Logger
import json
import os
from pathlib import Path
import traceback

class SettingsPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = Logger()
        home_dir = str(Path.home())
        self.config_dir = os.path.join(home_dir, '.vsa', 'config')
        self.config_file = os.path.join(self.config_dir, 'settings.json')
        self.settings = self.load_settings()
        self.initUI()
        
    def initUI(self):
        layout = QVBoxLayout()
        layout.setSpacing(20)
        
        # 项目设置组
        project_group = QGroupBox("项目设置")
        project_layout = QVBoxLayout()
        
        # 项目文件夹路径设置
        path_layout = QHBoxLayout()
        path_label = QLabel("默认项目文件夹:")
        self.path_edit = QLineEdit()
        self.path_edit.setText(self.settings.get('project_path', ''))
        self.path_edit.setReadOnly(True)
        browse_btn = QPushButton("浏览...")
        browse_btn.clicked.connect(self.browse_folder)
        
        path_layout.addWidget(path_label)
        path_layout.addWidget(self.path_edit)
        path_layout.addWidget(browse_btn)
        
        project_layout.addLayout(path_layout)
        
        # 添加当前设置状态标签
        self.status_label = QLabel()
        self.status_label.setStyleSheet("color: #52c41a;")  # 绿色
        project_layout.addWidget(self.status_label)
        
        project_group.setLayout(project_layout)
        
        # 保存和重置按钮
        buttons_layout = QHBoxLayout()
        
        # 重置按钮
        reset_btn = QPushButton("重置")
        reset_btn.setStyleSheet("""
            QPushButton {
                background-color: #ffffff;
                color: #1890ff;
                border: 1px solid #1890ff;
                padding: 8px 16px;
                border-radius: 4px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #e6f7ff;
            }
            QPushButton:pressed {
                background-color: #ffffff;
                border-color: #096dd9;
                color: #096dd9;
            }
        """)
        reset_btn.clicked.connect(self.reset_settings)
        
        # 保存按钮
        self.save_btn = QPushButton("保存设置")
        self.save_btn.setStyleSheet("""
            QPushButton {
                background-color: #1890ff;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #40a9ff;
            }
            QPushButton:pressed {
                background-color: #096dd9;
            }
            QPushButton:disabled {
                background-color: #d9d9d9;
                color: #ffffff;
            }
        """)
        self.save_btn.clicked.connect(self.save_settings)
        
        buttons_layout.addStretch()
        buttons_layout.addWidget(reset_btn)
        buttons_layout.addWidget(self.save_btn)
        
        # 添加到主布局
        layout.addWidget(project_group)
        layout.addLayout(buttons_layout)
        layout.addStretch()
        
        self.setLayout(layout)
        
        # 初始状态下禁用保存按钮
        self.save_btn.setEnabled(False)
        
    def browse_folder(self):
        """选择项目文件夹"""
        folder = QFileDialog.getExistingDirectory(
            self,
            "选择默认项目文件夹",
            self.path_edit.text()
        )
        if folder:
            self.logger.info(f"[设置] 用户选择项目文件夹: {folder}")
            self.path_edit.setText(folder)
            self.save_btn.setEnabled(True)  # 启用保存按钮
            self.status_label.setText("设置已更改，请点击保存")
            self.status_label.setStyleSheet("color: #faad14;")  # 黄色警告
        else:
            self.logger.info("[设置] 用户取消选择项目文件夹")
            
    def load_settings(self):
        """加载设置"""
        try:
            if not os.path.exists(self.config_dir):
                os.makedirs(self.config_dir)
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                self.logger.info(f"[设置] 成功加载设置: {settings}")
                return settings
            self.logger.info("[设置] 未找到设置文件，返回空设置")
            return {}
        except Exception as e:
            tb = traceback.format_exc()
            self.logger.error(f"[设置] 加载设置失败: {str(e)}\n{tb}")
            QMessageBox.warning(self, "加载失败", f"加载设置失败: {str(e)}")
            return {}
            
    def save_settings(self):
        """保存设置"""
        try:
            settings = {
                'project_path': self.path_edit.text()
            }
            if not os.path.exists(self.config_dir):
                os.makedirs(self.config_dir)
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, ensure_ascii=False, indent=4)
            self.logger.info(f"[设置] 设置已保存: {settings}")
            self.settings = settings
            # 显示保存成功
            self.status_label.setText("✓ 设置已保存")
            self.status_label.setStyleSheet("color: #52c41a;")  # 绿色
            self.save_btn.setEnabled(False)  # 禁用保存按钮
            # 弹出提示
            QMessageBox.information(self, "保存成功", "设置已成功保存！")
        except Exception as e:
            tb = traceback.format_exc()
            self.logger.error(f"[设置] 保存设置失败: {str(e)}\n{tb}")
            QMessageBox.critical(self, "保存失败", f"保存设置失败: {str(e)}")
            
    def reset_settings(self):
        """重置设置"""
        reply = QMessageBox.question(
            self,
            "确认重置",
            "确定要重置所有设置吗？这将清除所有已保存的配置。",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.logger.info("[设置] 用户确认重置所有设置")
            self.path_edit.clear()
            self.settings = {}
            self.save_btn.setEnabled(True)
            self.status_label.setText("设置已重置，请点击保存")
            self.status_label.setStyleSheet("color: #faad14;")  # 黄色警告
        else:
            self.logger.info("[设置] 用户取消重置设置")
            
    def get_project_path(self):
        """获取项目路径"""
        # 每次都重新读取，确保变更能被检测到
        self.settings = self.load_settings()
        return self.settings.get('project_path', '') 