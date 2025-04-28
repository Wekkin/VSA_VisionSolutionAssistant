import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                           QPushButton, QLabel, QListWidget, QStackedWidget, QFrame,
                           QLineEdit, QProgressBar, QScrollArea, QSplitter)
from PyQt5.QtCore import Qt, QSize
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
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle('工业视觉辅助系统')
        self.setMinimumSize(1200, 800)
        
        # 主窗口部件
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # 侧边栏
        sidebar = QWidget()
        sidebar.setFixedWidth(200)
        sidebar.setStyleSheet("background-color: #f7f9fa;")
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        
        # Logo
        logo_label = QLabel("视觉方案助手")
        logo_label.setAlignment(Qt.AlignCenter)
        logo_label.setStyleSheet("font-size: 18px; font-weight: bold; padding: 20px;")
        sidebar_layout.addWidget(logo_label)
        
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
        
        # 主内容区域
        content = QWidget()
        content.setStyleSheet("background-color: #f0f2f5;")
        content_layout = QVBoxLayout(content)
        
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
        
        # 添加到主内容布局
        content_layout.addWidget(top_bar)
        content_layout.addWidget(scroll_area)
        
        # 添加到主布局
        main_layout.addWidget(sidebar)
        main_layout.addWidget(content)

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()