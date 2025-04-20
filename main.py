import sys
import os
import json
from datetime import datetime
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QPushButton, QLabel, QFileDialog, 
                           QTabWidget, QGroupBox, QLineEdit, QMessageBox,
                           QListWidget, QProgressBar, QSplitter, QFrame,
                           QMenuBar, QMenu, QAction, QTextEdit, QRubberBand,
                           QStatusBar, QDialog, QFormLayout, QDialogButtonBox)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer, QRect, QPoint, QSize, QSettings
from PyQt5.QtGui import QPixmap, QImage, QCursor, QFont
from src.image_import.image_processor import ImageProcessor
from src.splash_screen import CustomSplashScreen

class ImageImportWorker(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(str)
    error = pyqtSignal(str)
    
    def __init__(self, image_processor, template_path=None):
        super().__init__()
        self.image_processor = image_processor
        self.template_path = template_path
        
    def run(self):
        try:
            output_path = self.image_processor.create_ppt_report(
                template_path=self.template_path
            )
            self.finished.emit(output_path)
        except Exception as e:
            self.error.emit(str(e))

class ImageViewer(QLabel):
    roi_selected = pyqtSignal(QPixmap)  # 信号：发送选中的ROI区域

    def __init__(self, parent=None, enable_roi=False):
        super().__init__(parent)
        self.enable_roi = enable_roi  # 是否启用ROI选择
        self.setAlignment(Qt.AlignCenter)
        self.setMinimumSize(400, 300)
        self.setStyleSheet("QLabel { background-color: #f0f0f0; border: 1px solid #cccccc; }")
        self.setText("等待图片导入...")
        
        # ROI选择相关
        self.rubberBand = None
        self.origin = QPoint()
        self.current_pixmap = None
        
        # 设置鼠标追踪
        if enable_roi:
            self.setMouseTracking(True)
            self.setCursor(Qt.CrossCursor)

    def set_image(self, image_path):
        if image_path and os.path.exists(image_path):
            pixmap = QPixmap(image_path)
            self.current_pixmap = pixmap
            scaled_pixmap = pixmap.scaled(self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.setPixmap(scaled_pixmap)
        else:
            self.setText("等待图片导入...")
            self.current_pixmap = None

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.pixmap():
            scaled_pixmap = self.current_pixmap.scaled(self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.setPixmap(scaled_pixmap)

    def mousePressEvent(self, event):
        if not self.enable_roi or not self.current_pixmap:
            return
            
        if event.button() == Qt.LeftButton:
            self.origin = event.pos()
            if not self.rubberBand:
                self.rubberBand = QRubberBand(QRubberBand.Rectangle, self)
            self.rubberBand.setGeometry(QRect(self.origin, QSize()))
            self.rubberBand.show()

    def mouseMoveEvent(self, event):
        if not self.enable_roi or not self.rubberBand:
            return
            
        self.rubberBand.setGeometry(QRect(self.origin, event.pos()).normalized())

    def mouseReleaseEvent(self, event):
        if not self.enable_roi or not self.rubberBand:
            return
            
        if event.button() == Qt.LeftButton:
            rect = self.rubberBand.geometry()
            self.rubberBand.hide()
            
            # 获取选中区域的图片
            if rect.width() > 10 and rect.height() > 10:  # 确保选择区域足够大
                # 计算实际图片上的ROI区域
                pixmap_rect = self.get_pixmap_rect()
                if pixmap_rect:
                    roi_rect = self.convert_view_to_pixmap_rect(rect, pixmap_rect)
                    roi_pixmap = self.current_pixmap.copy(roi_rect)
                    self.roi_selected.emit(roi_pixmap)

    def get_pixmap_rect(self):
        """获取实际显示的图片区域"""
        if not self.pixmap():
            return None
        
        # 获取缩放后的图片尺寸
        scaled_size = self.pixmap().size()
        x = (self.width() - scaled_size.width()) // 2
        y = (self.height() - scaled_size.height()) // 2
        return QRect(x, y, scaled_size.width(), scaled_size.height())

    def convert_view_to_pixmap_rect(self, view_rect, pixmap_rect):
        """将视图坐标转换为实际图片坐标"""
        # 计算选择区域相对于图片的比例
        x_ratio = self.current_pixmap.width() / pixmap_rect.width()
        y_ratio = self.current_pixmap.height() / pixmap_rect.height()
        
        # 计算实际图片上的坐标
        x = (view_rect.x() - pixmap_rect.x()) * x_ratio
        y = (view_rect.y() - pixmap_rect.y()) * y_ratio
        width = view_rect.width() * x_ratio
        height = view_rect.height() * y_ratio
        
        return QRect(int(x), int(y), int(width), int(height))

class NewProjectDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("新建项目")
        self.setFixedWidth(400)
        
        layout = QVBoxLayout(self)
        
        # 添加说明标签
        description = QLabel("请按照格式输入项目名称：公司名称+项目名称+版本\n例如：ACME_自动化检测_V1.0")
        description.setWordWrap(True)
        description.setStyleSheet("color: #666666; margin-bottom: 10px;")
        layout.addWidget(description)
        
        # 创建表单布局
        form_layout = QFormLayout()
        
        # 公司名称输入
        self.company_name = QLineEdit()
        self.company_name.setPlaceholderText("例如：ACME")
        form_layout.addRow("公司名称:", self.company_name)
        
        # 项目名称输入
        self.project_name = QLineEdit()
        self.project_name.setPlaceholderText("例如：自动化检测")
        form_layout.addRow("项目名称:", self.project_name)
        
        # 版本号输入
        self.version = QLineEdit()
        self.version.setPlaceholderText("例如：V1.0")
        form_layout.addRow("版本号:", self.version)
        
        layout.addLayout(form_layout)
        
        # 预览
        preview_group = QGroupBox("项目名称预览")
        preview_layout = QVBoxLayout()
        self.preview_label = QLabel()
        self.preview_label.setStyleSheet("color: #1976D2; font-weight: bold;")
        preview_layout.addWidget(self.preview_label)
        preview_group.setLayout(preview_layout)
        layout.addWidget(preview_group)
        
        # 连接信号
        self.company_name.textChanged.connect(self.update_preview)
        self.project_name.textChanged.connect(self.update_preview)
        self.version.textChanged.connect(self.update_preview)
        
        # 按钮
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            Qt.Horizontal, self)
        button_box.accepted.connect(self.validate_and_accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
    def update_preview(self):
        """更新预览"""
        preview = f"{self.company_name.text()}_{self.project_name.text()}_{self.version.text()}"
        self.preview_label.setText(preview)
        
    def validate_and_accept(self):
        """验证输入并接受"""
        if not self.company_name.text().strip():
            QMessageBox.warning(self, "警告", "请输入公司名称")
            self.company_name.setFocus()
            return
            
        if not self.project_name.text().strip():
            QMessageBox.warning(self, "警告", "请输入项目名称")
            self.project_name.setFocus()
            return
            
        if not self.version.text().strip():
            QMessageBox.warning(self, "警告", "请输入版本号")
            self.version.setFocus()
            return
            
        self.accept()
        
    def get_project_name(self):
        """获取完整的项目名称"""
        return f"{self.company_name.text()}_{self.project_name.text()}_{self.version.text()}"

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("POC Assistant")
        self.setGeometry(100, 100, 1200, 800)
        
        # 初始化设置
        self.settings = QSettings('POCAssistant', 'Settings')
        
        # 加载样式表
        self.load_stylesheet()
        
        # 创建状态栏
        self.statusBar().showMessage("Ready")
        
        # 创建并设置菜单栏
        self.create_menu_bar()
        
        # 初始化图片处理器
        self.image_processor = ImageProcessor()
        
        # 创建中心部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建主布局
        main_layout = QVBoxLayout(central_widget)
        
        # 创建水平分割器
        hsplitter = QSplitter(Qt.Horizontal)
        
        # 创建左侧面板
        left_panel = self.create_left_panel()
        
        # 创建右侧面板
        right_panel = self.create_right_panel()
        
        # 添加面板到分割器
        hsplitter.addWidget(left_panel)
        hsplitter.addWidget(right_panel)
        hsplitter.setStretchFactor(0, 1)
        hsplitter.setStretchFactor(1, 2)
        
        # 添加分割器到主布局
        main_layout.addWidget(hsplitter)
        
        # 设置主布局的边距
        main_layout.setContentsMargins(5, 5, 5, 5)
        
        # 加载默认设置
        self.load_settings()

    def load_settings(self):
        """加载应用程序设置"""
        default_project_path = self.settings.value('default_project_path', '')
        if default_project_path:
            self.default_project_path = default_project_path
        else:
            self.default_project_path = os.path.expanduser('~/Documents/POC_Projects')
            self.settings.setValue('default_project_path', self.default_project_path)

    def create_menu_bar(self):
        """创建菜单栏"""
        menubar = self.menuBar()
        menubar.setNativeMenuBar(False)  # 在 macOS 上禁用原生菜单栏
        
        # 设置菜单栏字体
        font = QFont()
        font.setPointSize(12)
        menubar.setFont(font)
        
        # 文件菜单
        file_menu = menubar.addMenu('文件')
        
        new_project_action = QAction('新建项目', self)
        new_project_action.setShortcut('Ctrl+N')
        new_project_action.triggered.connect(self.create_new_project)
        file_menu.addAction(new_project_action)
        
        open_project_action = QAction('打开项目', self)
        open_project_action.setShortcut('Ctrl+O')
        open_project_action.triggered.connect(self.open_project)
        file_menu.addAction(open_project_action)
        
        save_project_action = QAction('保存项目', self)
        save_project_action.setShortcut('Ctrl+S')
        save_project_action.triggered.connect(self.save_project)
        file_menu.addAction(save_project_action)
        
        file_menu.addSeparator()
        
        default_path_action = QAction('默认位置', self)
        default_path_action.triggered.connect(self.set_default_path)
        file_menu.addAction(default_path_action)
        
        # 功能菜单
        function_menu = menubar.addMenu('功能')
        
        # POC报告功能
        poc_report_action = QAction('POC报告', self)
        poc_report_action.triggered.connect(self.open_poc_report)
        function_menu.addAction(poc_report_action)
        
        # 缺陷生成功能
        defect_gen_action = QAction('缺陷生成', self)
        defect_gen_action.triggered.connect(self.open_defect_generation)
        function_menu.addAction(defect_gen_action)
        
        # 配置清单功能
        config_list_action = QAction('配置清单', self)
        config_list_action.triggered.connect(self.open_config_list)
        function_menu.addAction(config_list_action)
        
        # 配置菜单
        config_menu = menubar.addMenu('配置')
        
        # 配置清单子菜单
        config_items_menu = QMenu('配置清单', self)
        config_items_menu.addAction('相机参数')
        config_items_menu.addAction('镜头参数')
        config_items_menu.addAction('光源参数')
        config_menu.addMenu(config_items_menu)
        
        # 其他功能菜单
        other_menu = menubar.addMenu('其他功能')
        extend_action = QAction('拓展功能', self)
        extend_action.triggered.connect(self.open_extensions)
        other_menu.addAction(extend_action)
        
        # 方案总结菜单
        solution_menu = menubar.addMenu('方案总结')
        industry_action = QAction('行业方案', self)
        industry_action.triggered.connect(self.open_industry_solutions)
        solution_menu.addAction(industry_action)

    def create_new_project(self):
        """创建新项目"""
        # 检查是否已设置默认路径
        default_path = self.settings.value('default_project_path')
        if not default_path:
            reply = QMessageBox.question(self, "提示", 
                "您还未设置默认项目路径，是否现在设置？",
                QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                self.set_default_path()
                default_path = self.settings.value('default_project_path')
                if not default_path:  # 用户取消了路径选择
                    return
            else:
                return

        # 创建新项目对话框
        dialog = NewProjectDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            project_name = dialog.get_project_name()
            project_path = os.path.join(default_path, project_name)
            
            # 检查项目文件夹是否已存在
            if os.path.exists(project_path):
                reply = QMessageBox.question(self, "警告", 
                    f"项目文件夹 '{project_name}' 已存在，是否覆盖？",
                    QMessageBox.Yes | QMessageBox.No)
                if reply == QMessageBox.No:
                    return
            
            try:
                # 创建项目目录结构
                os.makedirs(project_path, exist_ok=True)
                os.makedirs(os.path.join(project_path, "images"), exist_ok=True)
                os.makedirs(os.path.join(project_path, "config"), exist_ok=True)
                os.makedirs(os.path.join(project_path, "RFQ"), exist_ok=True)
                
                # 创建项目配置文件
                self.create_project_config(project_path, project_name)
                
                # 创建README文件
                self.create_readme(project_path, project_name)
                
                # 更新当前项目路径
                self.current_project_path = project_path
                self.settings.setValue('last_project', project_path)
                
                QMessageBox.information(self, "成功", 
                    f"项目 '{project_name}' 创建成功！\n"
                    f"位置：{project_path}\n\n"
                    f"已创建以下文件夹：\n"
                    f"- images/：存储项目相关图片\n"
                    f"- config/：存储配置文件\n"
                    f"- RFQ/：存储RFQ文档")
                
            except Exception as e:
                QMessageBox.critical(self, "错误", f"创建项目失败：{str(e)}")
    
    def create_project_config(self, project_path, project_name):
        """创建项目配置文件"""
        config = {
            "project_name": project_name,
            "created_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "last_modified": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "project_path": project_path,
            "image_path": os.path.join(project_path, "images"),
            "config_path": os.path.join(project_path, "config"),
            "rfq_path": os.path.join(project_path, "RFQ")
        }
        
        config_file = os.path.join(project_path, "config", "project_config.json")
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=4)
    
    def create_readme(self, project_path, project_name):
        """创建项目README文件"""
        readme_content = f"""# {project_name}

## 项目结构
```
{project_name}/
├── images/     # 图片文件夹
├── config/     # 配置文件夹
└── RFQ/        # RFQ文档文件夹
```

## 文件夹说明
- images: 存储项目相关的所有图片文件
- config: 存储项目配置文件
- RFQ: 存储项目相关的RFQ文档

## 创建日期
{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
"""
        
        readme_file = os.path.join(project_path, "README.md")
        with open(readme_file, 'w', encoding='utf-8') as f:
            f.write(readme_content)

    def open_project(self):
        """打开现有项目"""
        project_dir = QFileDialog.getExistingDirectory(self, "选择项目文件夹")
        if project_dir:
            # TODO: 实现项目加载逻辑
            pass

    def save_project(self):
        """保存当前项目"""
        # TODO: 实现项目保存逻辑
        pass

    def set_default_path(self):
        """设置默认项目路径"""
        default_path = QFileDialog.getExistingDirectory(self, "选择默认项目路径", 
            self.settings.value('default_project_path', os.path.expanduser('~/Documents/POC_Projects')))
        if default_path:
            self.settings.setValue('default_project_path', default_path)
            QMessageBox.information(self, "成功", f"默认项目路径已设置为：\n{default_path}")

    def open_poc_report(self):
        """打开POC报告功能"""
        # TODO: 实现POC报告功能
        pass

    def open_defect_generation(self):
        """打开缺陷生成功能"""
        # TODO: 实现缺陷生成功能
        pass

    def open_config_list(self):
        """打开配置清单功能"""
        # TODO: 实现配置清单功能
        pass

    def open_extensions(self):
        """打开拓展功能"""
        # TODO: 实现拓展功能
        pass

    def open_industry_solutions(self):
        """打开行业方案"""
        # TODO: 实现行业方案功能
        pass

    def create_left_panel(self):
        """创建左侧图片导入面板"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # 图片导入组
        import_group = QGroupBox("图片导入")
        import_layout = QVBoxLayout(import_group)
        
        # 选择文件夹按钮和显示
        folder_layout = QHBoxLayout()
        self.folder_path_edit = QLineEdit()
        self.folder_path_edit.setReadOnly(True)
        select_folder_btn = QPushButton("选择文件夹")
        select_folder_btn.clicked.connect(self.select_folder)
        folder_layout.addWidget(self.folder_path_edit)
        folder_layout.addWidget(select_folder_btn)
        import_layout.addLayout(folder_layout)
        
        # 图片列表
        self.image_list = QListWidget()
        self.image_list.itemClicked.connect(self.on_image_selected)
        import_layout.addWidget(self.image_list)
        
        layout.addWidget(import_group)
        return panel

    def create_right_panel(self):
        """创建右侧显示面板"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # 标题
        title_label = QLabel("POC标题")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; padding: 5px;")
        layout.addWidget(title_label)
        
        # 上方分割器（原图展示和细节放大）
        top_splitter = QSplitter(Qt.Horizontal)
        
        # 原图展示
        original_group = QGroupBox("原图展示")
        original_layout = QVBoxLayout(original_group)
        self.original_viewer = ImageViewer(enable_roi=True)  # 启用ROI选择
        self.original_viewer.roi_selected.connect(self.on_roi_selected)
        original_layout.addWidget(self.original_viewer)
        top_splitter.addWidget(original_group)
        
        # 细节放大
        detail_group = QGroupBox("细节放大")
        detail_layout = QVBoxLayout(detail_group)
        self.detail_viewer = ImageViewer()
        detail_layout.addWidget(self.detail_viewer)
        top_splitter.addWidget(detail_group)
        
        # 可行性分析
        analysis_group = QGroupBox("可行性分析")
        analysis_layout = QVBoxLayout(analysis_group)
        self.analysis_text = QTextEdit()
        self.analysis_text.setPlaceholderText("请输入分析评价...")
        self.analysis_text.setText("检测OK，无风险")
        analysis_layout.addWidget(self.analysis_text)
        
        # 添加到主布局
        layout.addWidget(top_splitter)
        layout.addWidget(analysis_group)
        
        return panel
    
    def select_folder(self):
        """选择图片文件夹"""
        folder = QFileDialog.getExistingDirectory(self, "选择图片文件夹")
        if folder:
            self.folder_path_edit.setText(folder)
            image_files = self.image_processor.set_image_folder(folder)
            self.image_list.clear()
            self.image_list.addItems([os.path.basename(f) for f in image_files])
    
    def on_image_selected(self, item):
        """当选择图片列表中的项目时"""
        filename = item.text().strip()
        image_path = os.path.join(self.image_processor.image_folder, filename)
        if os.path.exists(image_path):
            self.original_viewer.set_image(image_path)
            self.detail_viewer.setText("请在左侧图片中拉框选择要放大的区域")
    
    def on_roi_selected(self, roi_pixmap):
        """当ROI区域被选中时"""
        self.detail_viewer.setPixmap(roi_pixmap.scaled(
            self.detail_viewer.size(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        ))

    def load_stylesheet(self):
        """加载应用程序样式表"""
        style_path = os.path.join('resources', 'layouts', 'styles', 'main.qss')
        try:
            with open(style_path, 'r') as f:
                self.setStyleSheet(f.read())
        except Exception as e:
            print(f"加载样式表失败: {str(e)}")
            # 使用默认样式
            self.setStyleSheet("""
                QMainWindow {
                    background-color: #FFFFFF;
                }
                QMenuBar {
                    background-color: #F5F5F5;
                    border-bottom: 1px solid #BDBDBD;
                }
            """)

def main():
    app = QApplication(sys.argv)
    
    # 设置应用程序样式
    app.setStyle('Fusion')
    
    # 创建启动界面
    splash = CustomSplashScreen()
    splash.show()
    
    # 设置启动界面位置居中
    screen = app.primaryScreen().geometry()
    splash_geometry = splash.geometry()
    x = (screen.width() - splash_geometry.width()) // 2
    y = (screen.height() - splash_geometry.height()) // 2
    splash.move(x, y)
    
    # 创建主窗口
    window = MainWindow()
    
    # 模拟加载过程
    def update_splash():
        if not splash.progress():
            # 加载完成，显示主窗口
            window.show()
            # 设置主窗口位置居中
            window_geometry = window.geometry()
            x = (screen.width() - window_geometry.width()) // 2
            y = (screen.height() - window_geometry.height()) // 2
            window.move(x, y)
            # 关闭启动界面
            splash.finish(window)
            timer.stop()
    
    # 设置定时器更新进度
    timer = QTimer()
    timer.timeout.connect(update_splash)
    timer.start(30)  # 每30毫秒更新一次
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main() 