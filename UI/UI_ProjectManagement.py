import os
import json
import shutil
import datetime
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
                           QLineEdit, QScrollArea, QMessageBox, QFrame, QDialog)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon, QFont, QDesktopServices
from PyQt5.QtCore import QUrl
from utils.logger import Logger
from PyQt5.QtWidgets import QProgressBar

CACHE_PATH = os.path.abspath(os.path.join('data', 'projects_cache.json'))

class ProjectCard(QFrame):
    def __init__(self, project_info, parent=None):
        super().__init__(parent)
        self.project_info = project_info
        self.parent_window = parent
        self.setFrameStyle(QFrame.StyledPanel)
        self.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 8px;
                border: 1px solid #e8e8e8;
                margin: 5px;
            }
            QFrame:hover {
                border: 2px solid #1890ff;
                background-color: #fafafa;
            }
        """)
        self.setCursor(Qt.PointingHandCursor)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)
        
        # 标题和状态行
        header_layout = QHBoxLayout()
        header_layout.setSpacing(10)
        
        # 标题
        title_label = QLabel(project_info['name'])
        title_label.setFont(QFont("Arial", 14, QFont.Bold))
        title_label.setStyleSheet("color: #262626;")
        
        # 状态标签
        status = self.get_project_status(project_info.get('progress', 0))
        status_label = QLabel(status)
        status_color = {
            "已完成": ("#f6ffed", "#52c41a"),  # 绿色
            "进行中": ("#e6f7ff", "#1890ff"),  # 蓝色
            "未开始": ("#fff7e6", "#fa8c16"),  # 橙色
        }.get(status, ("#f5f5f5", "#8c8c8c"))  # 默认灰色
        
        status_label.setStyleSheet(f"""
            QLabel {{
                background-color: {status_color[0]};
                color: {status_color[1]};
                padding: 2px 12px;
                border-radius: 4px;
                font-size: 12px;
                font-weight: bold;
                min-width: 70px;
                max-width: 70px;
                qproperty-alignment: AlignCenter;
            }}
        """)
        
        # 操作按钮
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(5)
        
        # info按钮
        info_btn = QPushButton()
        info_btn.setIcon(QIcon("icons/info.png"))
        info_btn.setIconSize(QSize(20, 20))
        info_btn.setToolTip("查看项目详情")
        info_btn.setFixedSize(32, 32)
        info_btn.setStyleSheet("""
            QPushButton {
                border: none;
                border-radius: 4px;
                background-color: transparent;
            }
            QPushButton:hover {
                background-color: #e6f7ff;
            }
        """)
        info_btn.setCursor(Qt.PointingHandCursor)
        info_btn.clicked.connect(self.show_project_details)
        
        # 删除按钮
        delete_btn = QPushButton()
        delete_btn.setIcon(QIcon("icons/delete.png"))
        delete_btn.setIconSize(QSize(20, 20))
        delete_btn.setToolTip("删除项目")
        delete_btn.setFixedSize(32, 32)
        delete_btn.setStyleSheet("""
            QPushButton {
                border: none;
                border-radius: 4px;
                background-color: transparent;
            }
            QPushButton:hover {
                background-color: #fff1f0;
            }
        """)
        delete_btn.setCursor(Qt.PointingHandCursor)
        delete_btn.clicked.connect(self.delete_project)
        
        btn_layout.addWidget(info_btn)
        btn_layout.addWidget(delete_btn)
        
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addLayout(btn_layout)
        header_layout.addWidget(status_label)
        
        # 进度条
        progress = project_info.get('progress', 0)
        progress_bar = QProgressBar()
        progress_bar.setValue(progress)
        progress_bar.setStyleSheet(f"""
            QProgressBar {{
                border: none;
                background-color: #f5f5f5;
                height: 4px;
                border-radius: 2px;
                text-align: right;
                margin: 5px 0;
            }}
            QProgressBar::chunk {{
                background-color: {status_color[1]};
                border-radius: 2px;
            }}
        """)
        progress_bar.setTextVisible(False)
        
        # 底部信息
        footer_layout = QHBoxLayout()
        footer_layout.setSpacing(10)
        
        # 更新时间
        time_label = QLabel(f"创建时间: {project_info.get('create_date', '')}")
        time_label.setStyleSheet("color: #8c8c8c; font-size: 12px;")
        
        # 进度百分比
        progress_label = QLabel(f"{progress}%")
        progress_label.setStyleSheet(f"color: {status_color[1]}; font-size: 12px; font-weight: bold;")
        
        footer_layout.addWidget(time_label)
        footer_layout.addStretch()
        footer_layout.addWidget(progress_label)
        
        # 添加所有元素到主布局
        layout.addLayout(header_layout)
        layout.addWidget(progress_bar)
        layout.addLayout(footer_layout)
        
        # 添加鼠标点击事件
        self.mousePressEvent = self.on_card_click
        
    def get_project_status(self, progress):
        """根据进度确定项目状态"""
        if progress == 100:
            return "已完成"
        elif progress > 0:
            return "进行中"
        else:
            return "未开始"
            
    def on_card_click(self, event):
        """卡片点击事件"""
        if event.button() == Qt.LeftButton:
            self.open_project_folder()
            
    def show_project_details(self):
        """显示项目详情"""
        QMessageBox.information(
            self,
            "项目详情",
            f"项目名称: {self.project_info['name']}\n"
            f"公司: {self.project_info.get('company', '')}\n"
            f"项目: {self.project_info.get('project', '')}\n"
            f"版本: {self.project_info.get('version', '')}\n"
            f"创建时间: {self.project_info.get('create_date', '')}\n"
            f"备注: {self.project_info.get('remark', '')}\n"
            f"路径: {self.project_info.get('path', '')}"
        )
            
    def open_project_folder(self):
        """打开项目文件夹"""
        path = self.project_info.get('path', '')
        if path and os.path.exists(path):
            QDesktopServices.openUrl(QUrl.fromLocalFile(path))
        else:
            QMessageBox.warning(self, "错误", "项目文件夹不存在")
            
    def delete_project(self):
        """删除项目"""
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("确认删除")
        msg_box.setText(f'确定要删除项目 "{self.project_info["name"]}" 吗？')
        msg_box.setInformativeText("此操作将删除项目的所有文件，且不可恢复！")
        msg_box.setIcon(QMessageBox.Question)
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg_box.setDefaultButton(QMessageBox.No)
        
        # 设置对话框样式
        msg_box.setStyleSheet("""
            QMessageBox {
                background-color: white;
            }
            QMessageBox QLabel {
                color: #262626;
                min-width: 300px;
            }
            QPushButton {
                background-color: white;
                border: 1px solid #d9d9d9;
                border-radius: 4px;
                padding: 5px 15px;
                min-width: 80px;
            }
            QPushButton:hover {
                border-color: #40a9ff;
                color: #40a9ff;
            }
            QPushButton:focus {
                border-color: #40a9ff;
                outline: none;
            }
            QPushButton[text="Yes"] {
                background-color: #ff4d4f;
                border-color: #ff4d4f;
                color: white;
            }
            QPushButton[text="Yes"]:hover {
                background-color: #ff7875;
                border-color: #ff7875;
            }
            QPushButton[text="No"] {
                background-color: white;
                border-color: #d9d9d9;
                color: #262626;
            }
            QPushButton[text="No"]:hover {
                border-color: #40a9ff;
                color: #40a9ff;
            }
        """)
        
        reply = msg_box.exec_()
        
        if reply == QMessageBox.Yes:
            try:
                # 删除项目文件夹
                path = self.project_info.get('path', '')
                if path and os.path.exists(path):
                    shutil.rmtree(path)
                    
                # 通知主窗口刷新项目列表
                if self.parent_window:
                    self.parent_window.refresh_project_list()
                    
            except Exception as e:
                error_box = QMessageBox(self)
                error_box.setWindowTitle("错误")
                error_box.setText(f"删除项目失败: {str(e)}")
                error_box.setIcon(QMessageBox.Critical)
                error_box.setStyleSheet("""
                    QMessageBox {
                        background-color: white;
                    }
                    QMessageBox QLabel {
                        color: #262626;
                        min-width: 300px;
                    }
                    QPushButton {
                        background-color: white;
                        border: 1px solid #d9d9d9;
                        border-radius: 4px;
                        padding: 5px 15px;
                        min-width: 80px;
                    }
                    QPushButton:hover {
                        border-color: #40a9ff;
                        color: #40a9ff;
                    }
                """)
                error_box.exec_()

class ProjectManagement(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = Logger()
        self.projects_data = []  # 存储项目数据
        self.initUI()
        
    def initUI(self):
        """初始化项目管理界面"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # 顶部栏
        top_bar = QWidget()
        top_bar.setStyleSheet("background-color: white; border-bottom: 1px solid #e8e8e8;")
        top_layout = QHBoxLayout(top_bar)
        
        # 搜索框
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("搜索项目...")
        self.search_box.setStyleSheet("""
            QLineEdit {
                border: 1px solid #d9d9d9;
                border-radius: 4px;
                padding: 5px 10px;
                background: white;
            }
            QLineEdit:focus {
                border-color: #1890ff;
            }
        """)
        self.search_box.setFixedWidth(300)
        self.search_box.textChanged.connect(self.update_project_cards)
        
        # 新建项目按钮
        self.new_project_btn = QPushButton("+ 新建项目")
        self.new_project_btn.setStyleSheet("""
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
        self.new_project_btn.clicked.connect(self.show_project_wizard)
        
        # 刷新按钮
        self.refresh_btn = QPushButton()
        self.refresh_btn.setIcon(QIcon("icons/refresh.png"))
        self.refresh_btn.setIconSize(QSize(20, 20))
        self.refresh_btn.setToolTip("刷新项目列表")
        self.refresh_btn.setStyleSheet("""
            QPushButton {
                border: 1px solid #d9d9d9;
                border-radius: 4px;
                padding: 4px;
                margin-left: 8px;
                background-color: white;
                min-width: 32px;
                min-height: 32px;
            }
            QPushButton:hover {
                border-color: #40a9ff;
                background-color: #e6f7ff;
            }
            QPushButton:pressed {
                border-color: #096dd9;
                background-color: #e6f7ff;
            }
        """)
        self.refresh_btn.clicked.connect(self.refresh_project_list)
        
        # 顶部工具栏布局
        top_layout.addWidget(self.search_box)
        top_layout.addWidget(self.refresh_btn)
        top_layout.addStretch()
        top_layout.addWidget(self.new_project_btn)
        
        # 项目列表区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
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
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }
        """)
        
        project_widget = QWidget()
        project_widget.setStyleSheet("background-color: transparent;")
        self.project_layout = QVBoxLayout(project_widget)
        self.project_layout.setSpacing(10)
        self.project_layout.setContentsMargins(10, 10, 10, 10)
        
        scroll_area.setWidget(project_widget)
        
        # 添加到主布局
        layout.addWidget(top_bar)
        layout.addWidget(scroll_area)
        
        # 初始加载项目列表
        self.refresh_project_list()
        
    def refresh_project_list(self):
        """刷新项目列表，支持从缓存文件搜索"""
        try:
            self.projects_data = []
            # 优先从缓存文件加载
            if os.path.exists(CACHE_PATH):
                with open(CACHE_PATH, 'r', encoding='utf-8') as f:
                    self.projects_data = json.load(f)
            # 按创建时间倒序排序
            self.projects_data.sort(key=lambda x: x.get('create_date', ''), reverse=True)
            self.update_project_cards()
            self.logger.info("项目列表已刷新")
        except Exception as e:
            self.logger.error(f"刷新项目列表失败: {str(e)}")
            QMessageBox.warning(self, "错误", f"刷新项目列表失败: {str(e)}")
            
    def calculate_project_progress(self, project_path):
        """计算项目进度"""
        try:
            progress = 0
            total_steps = 3  # 总步骤数
            
            # 检查image文件夹
            image_folder = os.path.join(project_path, os.path.basename(project_path) + "_image")
            if os.path.exists(image_folder) and os.listdir(image_folder):
                progress += 1
            
            # 检查config文件夹
            config_folder = os.path.join(project_path, os.path.basename(project_path) + "_config")
            if os.path.exists(config_folder) and len(os.listdir(config_folder)) > 1:  # 不只包含project_info.json
                progress += 1
            
            # 检查Defectmatrix文件夹
            defect_folder = os.path.join(project_path, os.path.basename(project_path) + "_Defectmatrix")
            if os.path.exists(defect_folder) and os.listdir(defect_folder):
                progress += 1
            
            return int((progress / total_steps) * 100)
            
        except Exception as e:
            self.logger.error(f"计算项目进度失败: {str(e)}")
            return 0
            
    def update_project_cards(self, search_text=""):
        """更新项目卡片显示"""
        # 清空现有项目卡片
        while self.project_layout.count():
            item = self.project_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # 根据搜索文本过滤项目
        filtered_projects = self.filter_projects(search_text)
        
        # 添加新的项目卡片
        for project_info in filtered_projects:
            card = ProjectCard(project_info, self)
            self.project_layout.addWidget(card)
        
        # 添加弹性空间
        self.project_layout.addStretch()
        
    def filter_projects(self, search_text):
        """根据关键字从缓存中搜索项目"""
        if not search_text:
            return self.projects_data
        search_text = search_text.lower()
        return [
            project for project in self.projects_data
            if search_text in project.get('name', '').lower() or
               search_text in project.get('company', '').lower() or
               search_text in project.get('project', '').lower() or
               search_text in project.get('remark', '').lower() or
               search_text in project.get('folder_name', '').lower()
        ]
        
    def show_project_wizard(self):
        """显示项目创建向导并引导用户创建规范项目结构"""
        from UI.UI_ProjectWizard import ProjectWizard
        from UI.UI_Settings import SettingsPage
        settings_page = SettingsPage()
        workspace = settings_page.get_project_path()
        if not workspace:
            reply = QMessageBox.warning(
                self,
                "未设置项目路径",
                "您还未设置默认项目路径，是否现在设置？",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes
            )
            if reply == QMessageBox.Yes:
                # TODO: 显示设置页面
                pass
            return
        # 弹出引导提示
        QMessageBox.information(self, "新建项目引导", "将在工作空间下创建规范的项目文件夹和模板文件。\n\n结构示例：\n项目名/\n├── 项目名_image/\n├── 项目名_RFQ/\n├── 项目名_CameraConfig.xlsx\n└── 项目名_DefectMatrixt.xlsx")
        # 创建并显示项目向导
        wizard = ProjectWizard(self)
        if wizard.exec_() == QDialog.Accepted:
            project_info = wizard.get_project_info()
            folder_name = project_info['folder_name']
            project_dir = project_info['project_path']
            company = project_info.get('company')
            create_date = project_info.get('create_date')
            # 1. 创建项目主文件夹
            os.makedirs(project_dir, exist_ok=True)
            # 2. 创建子文件夹
            image_dir = os.path.join(project_dir, f"{folder_name}_image")
            rfq_dir = os.path.join(project_dir, f"{folder_name}_RFQ")
            os.makedirs(image_dir, exist_ok=True)
            os.makedirs(rfq_dir, exist_ok=True)
            # 3. 复制模板表格
            src_cam = os.path.abspath(os.path.join('src', 'CameraConfig.xlsx'))
            dst_cam = os.path.join(project_dir, f"{folder_name}_CameraConfig.xlsx")
            if os.path.exists(src_cam):
                shutil.copy(src_cam, dst_cam)
            src_def = os.path.abspath(os.path.join('src', 'DefectMatrixt.xlsx'))
            dst_def = os.path.join(project_dir, f"{folder_name}_DefectMatrixt.xlsx")
            if os.path.exists(src_def):
                shutil.copy(src_def, dst_def)
            # 4. 缓存项目信息到./data/projects_cache.json
            cache_item = {
                'name': project_info['name'],
                'folder_name': folder_name,
                'company': company,
                'create_date': create_date,
                'path': project_dir,
                'remark': project_info.get('remark', ''),
                'project': project_info.get('project', ''),
                'version': project_info.get('version', '')
            }
            self.save_project_cache(cache_item)
            # 5. 刷新项目列表
            self.refresh_project_list()
            QMessageBox.information(self, "创建成功", f"项目 {folder_name} 已创建并缓存信息，可通过关键字搜索。")

    def save_project_cache(self, cache_item):
        """保存项目信息到缓存文件"""
        os.makedirs(os.path.dirname(CACHE_PATH), exist_ok=True)
        cache = []
        if os.path.exists(CACHE_PATH):
            with open(CACHE_PATH, 'r', encoding='utf-8') as f:
                try:
                    cache = json.load(f)
                except Exception:
                    cache = []
        # 避免重复
        cache = [item for item in cache if item['folder_name'] != cache_item['folder_name']]
        cache.append(cache_item)
        with open(CACHE_PATH, 'w', encoding='utf-8') as f:
            json.dump(cache, f, ensure_ascii=False, indent=2)
