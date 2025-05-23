from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
                            QLabel, QLineEdit, QTextEdit, QMessageBox, QGridLayout)
from PyQt5.QtCore import Qt
from utils.logger import Logger
import os
import json
from datetime import datetime
from pathlib import Path
import traceback

class ProjectWizard(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = Logger()
        self.settings = self.load_settings()
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle("新建项目")
        self.setMinimumWidth(500)
        layout = QVBoxLayout()
        layout.setSpacing(15)
        
        # 项目信息输入网格布局
        info_group = QGridLayout()
        info_group.setSpacing(10)
        
        # 公司名称输入
        company_label = QLabel("公司名称:")
        self.company_edit = QLineEdit()
        self.company_edit.setPlaceholderText("例如：华为")
        info_group.addWidget(company_label, 0, 0)
        info_group.addWidget(self.company_edit, 0, 1)
        
        # 项目名称输入
        project_label = QLabel("项目名称:")
        self.project_edit = QLineEdit()
        self.project_edit.setPlaceholderText("例如：手机屏幕检测")
        info_group.addWidget(project_label, 1, 0)
        info_group.addWidget(self.project_edit, 1, 1)
        
        # 版本号输入
        version_label = QLabel("版本号:")
        self.version_edit = QLineEdit()
        self.version_edit.setPlaceholderText("例如：V1.0")
        info_group.addWidget(version_label, 2, 0)
        info_group.addWidget(self.version_edit, 2, 1)
        
        # 项目名称预览
        preview_label = QLabel("完整名称:")
        self.name_preview = QLabel()
        self.name_preview.setStyleSheet("""
            QLabel {
                color: #1890ff;
                font-weight: bold;
                padding: 4px;
            }
        """)
        info_group.addWidget(preview_label, 3, 0)
        info_group.addWidget(self.name_preview, 3, 1)
        
        # 备注输入
        remark_layout = QVBoxLayout()
        remark_label = QLabel("项目备注")
        self.remark_edit = QTextEdit()
        self.remark_edit.setPlaceholderText("请输入项目备注信息...")
        self.remark_edit.setMaximumHeight(100)
        remark_layout.addWidget(remark_label)
        remark_layout.addWidget(self.remark_edit)
        
        # 项目路径预览
        path_layout = QVBoxLayout()
        path_label = QLabel("项目将创建在以下位置：")
        self.path_preview = QLabel()
        self.path_preview.setStyleSheet("""
            QLabel {
                color: #666666;
                background-color: #f5f5f5;
                padding: 8px;
                border-radius: 4px;
            }
        """)
        self.path_preview.setWordWrap(True)
        path_layout.addWidget(path_label)
        path_layout.addWidget(self.path_preview)
        
        # 按钮
        btn_layout = QHBoxLayout()
        cancel_btn = QPushButton("取消")
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: white;
                border: 1px solid #d9d9d9;
                padding: 8px 20px;
                border-radius: 4px;
            }
            QPushButton:hover {
                border-color: #40a9ff;
                color: #40a9ff;
            }
        """)
        self.create_btn = QPushButton("创建项目")
        self.create_btn.setStyleSheet("""
            QPushButton {
                background-color: #1890ff;
                color: white;
                border: none;
                padding: 8px 20px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #40a9ff;
            }
            QPushButton:disabled {
                background-color: #d9d9d9;
            }
        """)
        self.create_btn.setEnabled(False)
        
        btn_layout.addStretch()
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(self.create_btn)
        
        # 添加所有布局
        layout.addLayout(info_group)
        layout.addLayout(remark_layout)
        layout.addLayout(path_layout)
        layout.addStretch()
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)
        
        # 连接信号
        self.company_edit.textChanged.connect(self.update_preview)
        self.project_edit.textChanged.connect(self.update_preview)
        self.version_edit.textChanged.connect(self.update_preview)
        cancel_btn.clicked.connect(self.reject)
        self.create_btn.clicked.connect(self.create_project)
        
    def update_preview(self):
        """更新预览"""
        self.settings = self.load_settings()  # 每次都重新读取
        company = self.company_edit.text().strip()
        project = self.project_edit.text().strip()
        version = self.version_edit.text().strip()
        self.logger.info(f"[新建项目] update_preview: company={company}, project={project}, version={version}")
        if company and project and version:
            # 构建项目名称
            project_name = f"{company}_{project}_{version}"
            self.name_preview.setText(project_name)
            # 获取当前日期
            current_date = datetime.now().strftime("%Y%m%d")
            # 构建项目文件夹名
            folder_name = f"{project_name}_{current_date}"
            # 获取基础路径
            base_path = self.settings.get('project_path', '')
            if base_path:
                full_path = os.path.join(base_path, folder_name)
                self.logger.info(f"[新建项目] 预览路径: {full_path}")
                self.path_preview.setText(full_path)
                self.create_btn.setEnabled(True)
            else:
                self.logger.warning("[新建项目] 未设置默认项目路径，创建按钮禁用")
                self.path_preview.setText("错误：未设置默认项目路径，请在设置中配置")
                self.create_btn.setEnabled(False)
        else:
            self.logger.info("[新建项目] 关键信息未填写，创建按钮禁用")
            self.name_preview.setText("")
            self.path_preview.setText("")
            self.create_btn.setEnabled(False)
            
    def load_settings(self):
        """加载设置"""
        try:
            config_file = os.path.join(str(Path.home()), '.vsa', 'config', 'settings.json')
            if os.path.exists(config_file):
                with open(config_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                self.logger.info(f"[新建项目] 成功加载设置: {settings}")
                return settings
            self.logger.info("[新建项目] 未找到设置文件，返回空设置")
            return {}
        except Exception as e:
            tb = traceback.format_exc()
            self.logger.error(f"[新建项目] 加载设置失败: {str(e)}\n{tb}")
            return {}
            
    def create_project(self):
        """创建项目"""
        try:
            company = self.company_edit.text().strip()
            project = self.project_edit.text().strip()
            version = self.version_edit.text().strip()
            remark = self.remark_edit.toPlainText().strip()
            self.logger.info(f"[新建项目] 创建参数: company={company}, project={project}, version={version}, remark={remark}")
            if not all([company, project, version]):
                self.logger.warning("[新建项目] 有必填项未填写，创建中断")
                QMessageBox.warning(self, "错误", "请填写所有必填项")
                return
            # 构建项目名称
            project_name = f"{company}_{project}_{version}"
            # 获取当前日期
            current_date = datetime.now().strftime("%Y%m%d")
            # 构建项目文件夹名
            folder_name = f"{project_name}_{current_date}"
            # 获取基础路径
            base_path = self.settings.get('project_path', '')
            if not base_path:
                self.logger.error("[新建项目] 未设置默认项目路径，创建中断")
                QMessageBox.warning(self, "错误", "未设置默认项目路径，请在设置中配置")
                return
            # 创建主项目文件夹
            project_path = os.path.join(base_path, folder_name)
            os.makedirs(project_path, exist_ok=True)
            os.makedirs(os.path.join(project_path, f"{folder_name}_image"), exist_ok=True)
            self.logger.info(f"[新建项目] 项目创建成功: {project_path}")
            QMessageBox.information(self, "成功", "项目创建成功！")
            self.accept()
        except Exception as e:
            tb = traceback.format_exc()
            self.logger.error(f"[新建项目] 创建项目失败: {str(e)}\n{tb}")
            QMessageBox.critical(self, "错误", f"创建项目失败: {str(e)}")

    def get_project_info(self):
        company = self.company_edit.text().strip()
        project = self.project_edit.text().strip()
        version = self.version_edit.text().strip()
        project_name = f"{company}_{project}_{version}"
        current_date = datetime.now().strftime("%Y%m%d")
        folder_name = f"{project_name}_{current_date}"
        base_path = self.settings.get('project_path', '')
        project_path = os.path.join(base_path, folder_name)
        return {
            'company': company,
            'project': project,
            'version': version,
            'name': project_name,
            'folder_name': folder_name,
            'project_path': project_path,
            'remark': self.remark_edit.toPlainText(),
            'create_date': current_date
        } 