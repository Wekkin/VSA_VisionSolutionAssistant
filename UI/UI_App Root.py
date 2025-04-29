import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                           QPushButton, QLabel, QListWidget, QStackedWidget, QFrame,
                           QLineEdit, QProgressBar, QScrollArea, QSplitter, QToolButton,
                           QMessageBox)
from PyQt5.QtCore import Qt, QSize, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QIcon, QPixmap, QPalette, QColor, QFont

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
    def __init__(self, title, status, progress, update_time, parent=None):
        super().__init__(parent)
        self.setFrameStyle(QFrame.StyledPanel)
        self.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 8px;
                border: 1px solid #e8e8e8;
            }
            QFrame:hover {
                border-color: #1890ff;
            }
        """)

        layout = QVBoxLayout(self)
        
        # 标题
        title_label = QLabel(title)
        title_label.setFont(QFont("Arial", 12, QFont.Bold))
        
        # 状态标签
        status_label = QLabel(status)
        status_label.setStyleSheet(f"""
            background-color: {'#f6ffed' if status == '已完成' else '#e6f7ff'};
            color: {'#52c41a' if status == '已完成' else '#1890ff'};
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 12px;
        """)
        status_label.setFixedWidth(60)
        
        # 进度条
        progress_bar = QProgressBar()
        progress_bar.setValue(progress)
        progress_bar.setStyleSheet("""
            QProgressBar {
                border: none;
                background-color: #f5f5f5;
                height: 4px;
                border-radius: 2px;
            }
            QProgressBar::chunk {
                background-color: #1890ff;
                border-radius: 2px;
            }
        """)
        
        # 更新时间
        time_label = QLabel(f"更新时间: {update_time}")
        time_label.setStyleSheet("color: #999999; font-size: 12px;")
        
        # 布局
        header_layout = QHBoxLayout()
        header_layout.addWidget(title_label)
        header_layout.addWidget(status_label)
        header_layout.addStretch()
        
        layout.addLayout(header_layout)
        layout.addWidget(progress_bar)
        layout.addWidget(time_label)
        layout.addStretch()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.sidebar_expanded = True
        self.stacked_widget = QStackedWidget()  # 添加堆叠窗口部件
        self.poc_generator = None  # POC生成器实例
        self.config_recorder = None  # 添加配置记录实例变量
        self.integration_analyzer = None  # 添加集成分析实例变量
        self.extensions_window = None     # 添加功能拓展实例变量
        self.initUI()
        
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
        home_btn = QPushButton("首页")
        home_btn.setCheckable(True)
        home_btn.setChecked(True)
        settings_btn = QPushButton("设置")
        settings_btn.setCheckable(True)
        
        
        nav_layout.addWidget(home_btn)
        nav_layout.addWidget(settings_btn)
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
        
        top_layout.addWidget(search_box)
        top_layout.addStretch()
        top_layout.addWidget(new_project_btn)
        
        # 项目列表区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("QScrollArea { border: none; }")
        
        project_widget = QWidget()
        project_layout = QVBoxLayout(project_widget)
        
        # 添加示例项目卡片
        project_layout.addWidget(ProjectCard("汽车零部件表面缺陷检测", "进行中", 75, "2023-12-20"))
        project_layout.addWidget(ProjectCard("PCB板焊点质量检测", "已完成", 100, "2023-12-19"))
        project_layout.addWidget(ProjectCard("包装印刷品质检测", "待审核", 90, "2023-12-18"))
        project_layout.addStretch()
        
        scroll_area.setWidget(project_widget)
        
        # 添加到首页布局
        home_layout.addWidget(top_bar)
        home_layout.addWidget(scroll_area)
        
        # 将首页添加到堆叠窗口
        self.stacked_widget.addWidget(home_page)
        
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
        # 取消其他按钮的选中状态
        self.poc_btn.setChecked(False)
        self.analysis_btn.setChecked(False)
        self.config_btn.setChecked(False)
        self.integration_btn.setChecked(False)
        self.feature_btn.setChecked(False)
        # 显示首页
        self.stacked_widget.setCurrentIndex(0)

    def show_poc_page(self):
        # 取消其他按钮的选中状态
        self.project_btn.setChecked(False)
        self.analysis_btn.setChecked(False)
        self.config_btn.setChecked(False)
        self.integration_btn.setChecked(False)
        self.feature_btn.setChecked(False)
        
        # 如果POC生成器页面不存在，创建它
        if not self.poc_generator:
            from UI_POCGenerator import POCGenerator
            self.poc_generator = POCGenerator()
            self.stacked_widget.addWidget(self.poc_generator)
        
        # 显示POC生成器页面
        self.stacked_widget.setCurrentWidget(self.poc_generator)

    def show_config_page(self):
        # 取消其他按钮的选中状态
        self.project_btn.setChecked(False)
        self.poc_btn.setChecked(False)
        self.analysis_btn.setChecked(False)
        self.integration_btn.setChecked(False)
        self.feature_btn.setChecked(False)
        
        # 如果配置记录页面不存在，创建它
        if not self.config_recorder:
            from UI_ConfigurationRecorder import ConfigurationRecorder
            self.config_recorder = ConfigurationRecorder()
            self.stacked_widget.addWidget(self.config_recorder)
        
        # 显示配置记录页面
        self.stacked_widget.setCurrentWidget(self.config_recorder)

    def show_integration_page(self):
        # 取消其他按钮的选中状态
        self.project_btn.setChecked(False)
        self.poc_btn.setChecked(False)
        self.analysis_btn.setChecked(False)
        self.config_btn.setChecked(False)
        self.feature_btn.setChecked(False)
        
        # 如果集成分析页面不存在，创建它
        if not self.integration_analyzer:
            from UI_IntegrationAnalyzer import IntegrationAnalyzer
            self.integration_analyzer = IntegrationAnalyzer()
            self.stacked_widget.addWidget(self.integration_analyzer)
        
        # 显示集成分析页面
        self.stacked_widget.setCurrentWidget(self.integration_analyzer)

    def show_extensions_page(self):
        # 取消其他按钮的选中状态
        self.project_btn.setChecked(False)
        self.poc_btn.setChecked(False)
        self.analysis_btn.setChecked(False)
        self.config_btn.setChecked(False)
        self.integration_btn.setChecked(False)
        self.feature_btn.setChecked(False)
        
        # 如果功能拓展页面不存在，创建它
        if not self.extensions_window:
            from UI_Extensions import ExtensionsWindow
            # 由于ExtensionsWindow是QMainWindow，我们需要创建一个QWidget来包装它
            container = QWidget()
            layout = QVBoxLayout(container)
            self.extensions_window = ExtensionsWindow()
            layout.addWidget(self.extensions_window)
            self.stacked_widget.addWidget(container)
        
        # 显示功能拓展页面
        self.stacked_widget.setCurrentWidget(self.extensions_window.parent())

    def show_analysis_page(self):
        # 显示"功能开发中"的提示框
        QMessageBox.information(self, 
                              "功能开发中", 
                              "缺陷分析功能正在开发中，敬请期待！",
                              QMessageBox.Ok)
        
        # 取消当前按钮的选中状态，保持在当前页面
        self.analysis_btn.setChecked(False)

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()