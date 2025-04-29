import sys
import os
import json
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                           QPushButton, QLabel, QListWidget, QStackedWidget, QFrame,
                           QLineEdit, QProgressBar, QScrollArea, QSplitter, QToolButton,
                           QMessageBox, QDialog)
from PyQt5.QtCore import Qt, QSize, QPropertyAnimation, QEasingCurve, QUrl
from PyQt5.QtGui import QIcon, QPixmap, QPalette, QColor, QFont, QDesktopServices
from utils.logger import Logger
from UI.UI_Settings import SettingsPage

class SidebarButton(QPushButton):
    def __init__(self, text, icon_path=None, parent=None):
        super().__init__(text, parent)
        self.setCheckable(True)
        self.setFixedHeight(40)
        if icon_path:
            self.setIcon(QIcon(icon_path))
        self.setStyleSheet("""
            QPushButton {
                border: none;
                border-radius: 5px;
                padding: 8px 16px;
                text-align: left;
                margin: 2px 8px;
                color: #333333;
                background-color: transparent;
            }
            QPushButton:hover {
                background-color: #e6f3ff;
            }
            QPushButton:checked {
                background-color: #1890ff;
                color: white;
            }
        """)

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
        
        # 打开按钮
        open_btn = QPushButton()
        open_btn.setIcon(QIcon("icons/folder-open.png"))
        open_btn.setIconSize(QSize(20, 20))
        open_btn.setToolTip("打开项目文件夹")
        open_btn.setFixedSize(32, 32)
        open_btn.setStyleSheet("""
            QPushButton {
                border: none;
                border-radius: 4px;
                background-color: transparent;
            }
            QPushButton:hover {
                background-color: #e6f7ff;
            }
        """)
        open_btn.setCursor(Qt.PointingHandCursor)
        open_btn.clicked.connect(self.open_project_folder)
        
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
        
        btn_layout.addWidget(open_btn)
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
            self.show_project_details()
            
    def show_project_details(self):
        """显示项目详情"""
        # TODO: 实现项目详情页面
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
                    import shutil
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

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.logger = Logger()
        self.logger.info("初始化主窗口")
        self.sidebar_expanded = True
        self.stacked_widget = QStackedWidget()
        
        # 初始化页面索引
        self.home_page_index = 0
        self.settings_page_index = None
        self.poc_page_index = None
        self.config_page_index = None
        self.integration_page_index = None
        self.extensions_page_index = None
        
        # 初始化页面引用
        self.poc_generator = None
        self.config_recorder = None
        self.integration_analyzer = None
        self.extensions_window = None
        self.settings_page = None
        self.project_wizard = None
        self.projects_data = []  # 存储项目数据
        
        self.initUI()
        self.logger.info("主窗口初始化完成")
        
    def initUI(self):
        self.setWindowTitle('视觉方案助手')
        self.setMinimumSize(1200, 800)
        
        # 主窗口部件
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # 顶部导航栏
        nav_bar = QWidget()
        nav_bar.setFixedHeight(50)
        nav_bar.setStyleSheet("""
            QWidget {
                background-color: white;
                border-bottom: 1px solid #e8e8e8;
            }
            QPushButton {
                border: none;
                padding: 8px 16px;
                color: #666;
                font-size: 14px;
                background: transparent;
            }
            QPushButton:hover {
                color: #1890ff;
            }
            QPushButton:checked {
                color: #1890ff;
                font-weight: bold;
                border-bottom: 2px solid #1890ff;
            }
        """)
        nav_layout = QHBoxLayout(nav_bar)
        nav_layout.setContentsMargins(10, 0, 10, 0)
        
        # 导航按钮
        self.home_btn = QPushButton("首页")
        self.home_btn.setCheckable(True)
        self.home_btn.setChecked(True)
        self.home_btn.clicked.connect(self.show_home_page)
        
        self.settings_btn = QPushButton("设置")
        self.settings_btn.setCheckable(True)
        self.settings_btn.clicked.connect(self.show_settings_page)
        
        nav_layout.addWidget(self.home_btn)
        nav_layout.addWidget(self.settings_btn)
        nav_layout.addStretch()
        
        # 内容区域容器
        content_container = QWidget()
        content_layout = QHBoxLayout(content_container)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        
        # 侧边栏容器
        self.sidebar_container = QWidget()
        self.sidebar_container.setFixedWidth(200)
        sidebar_container_layout = QHBoxLayout(self.sidebar_container)
        sidebar_container_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_container_layout.setSpacing(0)
        
        # 侧边栏
        sidebar = QWidget()
        sidebar.setStyleSheet("background-color: #f7f9fa;")
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        
        # Logo
        logo_layout = QHBoxLayout()
        logo_label = QLabel("视觉方案助手")
        logo_label.setStyleSheet("font-size: 18px; font-weight: bold; padding: 20px;")
        
        # 隐藏按钮
        self.toggle_btn = QToolButton()
        self.toggle_btn.setIcon(QIcon("icons/collapse.png"))  # 需要准备对应图标
        self.toggle_btn.setStyleSheet("""
            QToolButton {
                border: none;
                padding: 4px;
                background: transparent;
            }
            QToolButton:hover {
                background-color: #e6f3ff;
            }
        """)
        self.toggle_btn.clicked.connect(self.toggle_sidebar)
        
        logo_layout.addWidget(logo_label)
        logo_layout.addWidget(self.toggle_btn)
        logo_layout.addStretch()
        sidebar_layout.addLayout(logo_layout)
        
        # 侧边栏按钮
        self.project_btn = SidebarButton("项目管理", "icons/project.png")
        self.poc_btn = SidebarButton("POC制作", "icons/poc.png")
        self.analysis_btn = SidebarButton("缺陷分析", "icons/analysis.png")
        self.config_btn = SidebarButton("配置记录", "icons/config.png")
        self.integration_btn = SidebarButton("集成分析", "icons/integration.png")
        self.feature_btn = SidebarButton("功能拓展", "icons/feature.png")
        
        sidebar_layout.addWidget(self.project_btn)
        sidebar_layout.addWidget(self.poc_btn)
        sidebar_layout.addWidget(self.analysis_btn)
        sidebar_layout.addWidget(self.config_btn)
        sidebar_layout.addWidget(self.integration_btn)
        sidebar_layout.addWidget(self.feature_btn)
        sidebar_layout.addStretch()
        
        sidebar_container_layout.addWidget(sidebar)
        
        # 主内容区域
        content = QWidget()
        content.setStyleSheet("background-color: #f0f2f5;")
        content_layout = QVBoxLayout(content)
        
        # 创建堆叠窗口部件
        self.stacked_widget = QStackedWidget()
        
        # 创建首页
        home_page = QWidget()
        home_layout = QVBoxLayout(home_page)
        
        # 顶部栏
        top_bar = QWidget()
        top_bar.setStyleSheet("background-color: white; border-bottom: 1px solid #e8e8e8;")
        top_layout = QHBoxLayout(top_bar)
        
        # 搜索框
        search_box = QLineEdit()
        search_box.setPlaceholderText("搜索项目...")
        search_box.setStyleSheet("""
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
        search_box.setFixedWidth(300)
        search_box.textChanged.connect(lambda text: self.update_project_cards(text))
        
        # 新建项目按钮
        new_project_btn = QPushButton("+ 新建项目")
        new_project_btn.setStyleSheet("""
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
        new_project_btn.clicked.connect(self.show_project_wizard)
        
        # 刷新按钮
        refresh_btn = QPushButton()
        refresh_btn.setIcon(QIcon("icons/refresh.png"))
        refresh_btn.setIconSize(QSize(20, 20))
        refresh_btn.setToolTip("刷新项目列表")
        refresh_btn.setStyleSheet("""
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
        refresh_btn.clicked.connect(self.refresh_project_list)
        
        # 顶部工具栏布局
        top_layout.addWidget(search_box)
        top_layout.addWidget(refresh_btn)
        top_layout.addStretch()
        top_layout.addWidget(new_project_btn)
        
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
        
        # 初始加载项目列表
        self.refresh_project_list()
        
        # 添加到首页布局
        home_layout.addWidget(top_bar)
        home_layout.addWidget(scroll_area)
        
        # 将首页添加到堆叠窗口
        self.stacked_widget.addWidget(home_page)
        self.home_page_index = 0
        
        # 创建并添加设置页面
        from UI.UI_Settings import SettingsPage
        self.settings_page = SettingsPage()
        self.stacked_widget.addWidget(self.settings_page)
        self.settings_page_index = self.stacked_widget.count() - 1
        
        # 将堆叠窗口添加到主内容布局
        content_layout.addWidget(self.stacked_widget)
        
        # 将侧边栏和主内容区域添加到内容容器
        content_container.layout().addWidget(self.sidebar_container)
        content_container.layout().addWidget(content)
        
        # 将导航栏和内容容器添加到主布局
        main_layout.addWidget(nav_bar)
        main_layout.addWidget(content_container)
        
        # 连接侧边栏按钮信号
        self.project_btn.clicked.connect(self.show_home_page)
        self.poc_btn.clicked.connect(self.show_poc_page)
        self.config_btn.clicked.connect(self.show_config_page)
        self.integration_btn.clicked.connect(self.show_integration_page)
        self.feature_btn.clicked.connect(self.show_extensions_page)
        self.analysis_btn.clicked.connect(self.show_analysis_page)
        
        # 设置首页按钮为选中状态
        self.project_btn.setChecked(True)

    def toggle_sidebar(self):
        """切换侧边栏显示/隐藏"""
        if self.sidebar_expanded:
            # 创建收起动画
            self.animation = QPropertyAnimation(self.sidebar_container, b"minimumWidth")
            self.animation.setDuration(200)
            self.animation.setStartValue(200)
            self.animation.setEndValue(50)
            self.animation.setEasingCurve(QEasingCurve.InOutQuart)
            self.animation.start()
            self.toggle_btn.setIcon(QIcon("icons/expand.png"))  # 需要准备对应图标
        else:
            # 创建展开动画
            self.animation = QPropertyAnimation(self.sidebar_container, b"minimumWidth")
            self.animation.setDuration(200)
            self.animation.setStartValue(50)
            self.animation.setEndValue(200)
            self.animation.setEasingCurve(QEasingCurve.InOutQuart)
            self.animation.start()
            self.toggle_btn.setIcon(QIcon("icons/collapse.png"))  # 需要准备对应图标
            
        self.sidebar_expanded = not self.sidebar_expanded

    def show_home_page(self):
        """显示首页"""
        self.logger.info("切换到首页")
        self.home_btn.setChecked(True)
        self.settings_btn.setChecked(False)
        self.project_btn.setChecked(True)
        self.poc_btn.setChecked(False)
        self.analysis_btn.setChecked(False)
        self.config_btn.setChecked(False)
        self.integration_btn.setChecked(False)
        self.feature_btn.setChecked(False)
        self.stacked_widget.setCurrentIndex(0)

    def show_settings_page(self):
        """显示设置页面"""
        self.logger.info("切换到设置页面")
        self.home_btn.setChecked(False)
        self.settings_btn.setChecked(True)
        
        # 取消所有侧边栏按钮的选中状态
        self.project_btn.setChecked(False)
        self.poc_btn.setChecked(False)
        self.analysis_btn.setChecked(False)
        self.config_btn.setChecked(False)
        self.integration_btn.setChecked(False)
        self.feature_btn.setChecked(False)
        
        # 显示设置页面
        self.stacked_widget.setCurrentIndex(self.settings_page_index)

    def show_poc_page(self):
        self.logger.info("切换到POC制作页面")
        # 取消其他按钮的选中状态
        self.project_btn.setChecked(False)
        self.analysis_btn.setChecked(False)
        self.config_btn.setChecked(False)
        self.integration_btn.setChecked(False)
        self.feature_btn.setChecked(False)
        
        # 如果POC生成器页面不存在，创建它
        if not self.poc_generator:
            from UI.UI_POCGenerator import POCGenerator
            self.poc_generator = POCGenerator()
            self.stacked_widget.addWidget(self.poc_generator)
            self.poc_page_index = self.stacked_widget.count() - 1
        
        # 显示POC生成器页面
        self.stacked_widget.setCurrentIndex(self.poc_page_index)

    def show_config_page(self):
        self.logger.info("切换到配置记录页面")
        # 取消其他按钮的选中状态
        self.project_btn.setChecked(False)
        self.poc_btn.setChecked(False)
        self.analysis_btn.setChecked(False)
        self.integration_btn.setChecked(False)
        self.feature_btn.setChecked(False)
        
        # 如果配置记录页面不存在，创建它
        if not self.config_recorder:
            from UI.UI_ConfigurationRecorder import ConfigurationRecorder
            self.config_recorder = ConfigurationRecorder()
            self.stacked_widget.addWidget(self.config_recorder)
            self.config_page_index = self.stacked_widget.count() - 1
        
        # 显示配置记录页面
        self.stacked_widget.setCurrentIndex(self.config_page_index)

    def show_integration_page(self):
        self.logger.info("切换到集成分析页面")
        # 取消其他按钮的选中状态
        self.project_btn.setChecked(False)
        self.poc_btn.setChecked(False)
        self.analysis_btn.setChecked(False)
        self.config_btn.setChecked(False)
        self.feature_btn.setChecked(False)
        
        # 如果集成分析页面不存在，创建它
        if not self.integration_analyzer:
            from UI.UI_IntegrationAnalyzer import IntegrationAnalyzer
            self.integration_analyzer = IntegrationAnalyzer()
            self.stacked_widget.addWidget(self.integration_analyzer)
            self.integration_page_index = self.stacked_widget.count() - 1
        
        # 显示集成分析页面
        self.stacked_widget.setCurrentIndex(self.integration_page_index)

    def show_extensions_page(self):
        self.logger.info("切换到功能拓展页面")
        # 取消其他按钮的选中状态
        self.project_btn.setChecked(False)
        self.poc_btn.setChecked(False)
        self.analysis_btn.setChecked(False)
        self.config_btn.setChecked(False)
        self.integration_btn.setChecked(False)
        
        # 如果功能拓展页面不存在，创建它
        if not self.extensions_window:
            from UI.UI_Extensions import ExtensionsWindow
            # 由于ExtensionsWindow是QMainWindow，我们需要创建一个QWidget来包装它
            container = QWidget()
            layout = QVBoxLayout(container)
            self.extensions_window = ExtensionsWindow()
            layout.addWidget(self.extensions_window)
            self.stacked_widget.addWidget(container)
            self.extensions_page_index = self.stacked_widget.count() - 1
        
        # 显示功能拓展页面
        self.stacked_widget.setCurrentIndex(self.extensions_page_index)

    def show_analysis_page(self):
        self.logger.info("尝试访问开发中的缺陷分析功能")
        # 显示"功能开发中"的提示框
        QMessageBox.information(self, 
                              "功能开发中", 
                              "缺陷分析功能正在开发中，敬请期待！",
                              QMessageBox.Ok)
        
        # 取消当前按钮的选中状态，保持在当前页面
        self.analysis_btn.setChecked(False)

    def show_project_wizard(self):
        """显示项目创建向导"""
        from UI.UI_ProjectWizard import ProjectWizard
        
        # 检查是否已设置默认项目路径
        if not self.settings_page:
            self.settings_page = SettingsPage()
        
        project_path = self.settings_page.get_project_path()
        if not project_path:
            reply = QMessageBox.warning(
                self,
                "未设置项目路径",
                "您还未设置默认项目路径，是否现在设置？",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes
            )
            if reply == QMessageBox.Yes:
                self.show_settings_page()
            return
            
        # 创建并显示项目向导
        wizard = ProjectWizard(self)
        if wizard.exec_() == QDialog.Accepted:
            # 刷新项目列表
            self.refresh_project_list()
            
    def refresh_project_list(self):
        """刷新项目列表"""
        try:
            # 清空现有项目数据
            self.projects_data = []
            
            # 获取项目根目录
            if not self.settings_page:
                self.settings_page = SettingsPage()
            base_path = self.settings_page.get_project_path()
            
            if not base_path or not os.path.exists(base_path):
                self.logger.warning("项目路径不存在")
                return
            
            # 获取所有项目文件夹
            for folder_name in os.listdir(base_path):
                folder_path = os.path.join(base_path, folder_name)
                if not os.path.isdir(folder_path):
                    continue
                    
                # 检查是否是项目文件夹（包含config子文件夹和project_info.json）
                config_folder = os.path.join(folder_path, f"{folder_name}_config")
                info_file = os.path.join(config_folder, "project_info.json")
                
                if os.path.exists(info_file):
                    try:
                        with open(info_file, 'r', encoding='utf-8') as f:
                            project_info = json.load(f)
                            # 计算项目进度
                            project_info['progress'] = self.calculate_project_progress(folder_path)
                            self.projects_data.append(project_info)
                    except Exception as e:
                        self.logger.error(f"读取项目信息失败: {str(e)}")
                        continue
            
            # 按创建时间倒序排序
            self.projects_data.sort(key=lambda x: x.get('create_date', ''), reverse=True)
            
            # 更新项目列表显示
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
            card = self.create_project_card(project_info)
            self.project_layout.addWidget(card)
        
        # 添加弹性空间
        self.project_layout.addStretch()

    def filter_projects(self, search_text):
        """根据搜索文本过滤项目"""
        if not search_text:
            return self.projects_data
            
        search_text = search_text.lower()
        return [
            project for project in self.projects_data
            if search_text in project.get('name', '').lower() or
               search_text in project.get('company', '').lower() or
               search_text in project.get('project', '').lower() or
               search_text in project.get('remark', '').lower()
        ]

    def create_project_card(self, project_info):
        """创建项目卡片"""
        # 创建卡片
        card = ProjectCard(project_info, self)
        
        return card

def main():
    app = QApplication(sys.argv)
    
    # 设置全局应用程序样式
    app.setStyleSheet("""
        QToolTip {
            background-color: white;
            color: #262626;
            border: 1px solid #d9d9d9;
            padding: 5px;
            border-radius: 4px;
            font-size: 12px;
        }
        QMessageBox {
            background-color: white;
        }
        QMessageBox QLabel {
            color: #262626;
        }
        QMessageBox QPushButton {
            background-color: white;
            border: 1px solid #d9d9d9;
            border-radius: 4px;
            padding: 5px 15px;
            min-width: 80px;
            color: #262626;
        }
        QMessageBox QPushButton:hover {
            border-color: #40a9ff;
            color: #40a9ff;
        }
    """)
    
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()