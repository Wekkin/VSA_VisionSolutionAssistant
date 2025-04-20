import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QPushButton, QLabel, QFileDialog, 
                           QTabWidget, QGroupBox, QLineEdit, QMessageBox,
                           QListWidget, QProgressBar, QSplitter, QFrame,
                           QMenuBar, QMenu, QAction, QTextEdit, QRubberBand,
                           QStatusBar)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer, QRect, QPoint, QSize
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

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("工业视觉检测办公助手")
        self.setGeometry(100, 100, 1200, 800)
        
        # 创建状态栏
        self.statusBar().showMessage("就绪")
        
        # 创建并设置菜单栏
        self.create_menu_bar()
        
        # 设置窗口样式
        self.setStyleSheet("""
            QMainWindow {
                background-color: #FFFFFF;
            }
            QMenuBar {
                background-color: #F5F5F5;
                border-bottom: 1px solid #BDBDBD;
                min-height: 25px;
                font-size: 14px;
            }
            QMenuBar::item {
                padding: 5px 10px;
                margin: 0px;
                background: transparent;
            }
            QMenuBar::item:selected {
                background-color: #E3F2FD;
                color: #1976D2;
            }
            QMenuBar::item:pressed {
                background-color: #1976D2;
                color: white;
            }
            QMenu {
                background-color: #FFFFFF;
                border: 1px solid #BDBDBD;
                padding: 5px 0px;
            }
            QMenu::item {
                padding: 8px 25px;
                border: none;
            }
            QMenu::item:selected {
                background-color: #E3F2FD;
                color: #1976D2;
            }
            QMenu::separator {
                height: 1px;
                background: #BDBDBD;
                margin: 5px 0px;
            }
            QStatusBar {
                background-color: #F5F5F5;
                color: #424242;
            }
            QGroupBox {
                font-weight: bold;
                border: 1px solid #BDBDBD;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 5px 15px;
                min-height: 25px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QLineEdit, QTextEdit {
                padding: 5px;
                border: 1px solid #BDBDBD;
                border-radius: 4px;
            }
        """)
        
        # 初始化图片处理器
        self.image_processor = ImageProcessor()
        
        # 创建中心部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建主布局
        main_layout = QVBoxLayout(central_widget)  # 改为垂直布局
        
        # 创建水平分割器用于左右面板
        hsplitter = QSplitter(Qt.Horizontal)
        
        # 创建左侧图片导入区域
        left_panel = self.create_left_panel()
        
        # 创建右侧显示区域
        right_panel = self.create_right_panel()
        
        # 添加面板到分割器
        hsplitter.addWidget(left_panel)
        hsplitter.addWidget(right_panel)
        hsplitter.setStretchFactor(0, 1)  # 左侧面板
        hsplitter.setStretchFactor(1, 3)  # 右侧面板
        
        # 添加分割器到主布局
        main_layout.addWidget(hsplitter)
        
        # 设置主布局的边距
        main_layout.setContentsMargins(5, 5, 5, 5)

    def create_menu_bar(self):
        """创建菜单栏"""
        # 创建菜单栏
        menubar = self.menuBar()
        menubar.setNativeMenuBar(False)  # 在 macOS 上禁用原生菜单栏
        
        # 设置菜单栏字体
        font = QFont()
        font.setPointSize(12)
        menubar.setFont(font)
        
        # 文件菜单
        file_menu = menubar.addMenu('文件')
        new_action = QAction('新建项目', self)
        new_action.setShortcut('Ctrl+N')
        file_menu.addAction(new_action)
        
        open_action = QAction('打开项目', self)
        open_action.setShortcut('Ctrl+O')
        file_menu.addAction(open_action)
        
        save_action = QAction('保存项目', self)
        save_action.setShortcut('Ctrl+S')
        file_menu.addAction(save_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction('退出', self)
        exit_action.setShortcut('Ctrl+Q')
        file_menu.addAction(exit_action)
        
        # 功能菜单
        function_menu = menubar.addMenu('功能')
        function_menu.addAction('图片导入')
        function_menu.addAction('批量处理')
        
        # POC菜单
        poc_menu = menubar.addMenu('POC')
        poc_menu.addAction('新建POC')
        poc_menu.addAction('POC列表')
        
        # 缺陷菜单
        defect_menu = menubar.addMenu('缺陷')
        defect_menu.addAction('缺陷库')
        defect_menu.addAction('缺陷分析')
        
        # 配置菜单
        config_menu = menubar.addMenu('配置')
        config_menu.addAction('相机参数')
        config_menu.addAction('系统设置')
        
        # 集成菜单
        integration_menu = menubar.addMenu('集成')
        integration_menu.addAction('导出方案')
        integration_menu.addAction('部署配置')
        
        # 其他菜单
        other_menu = menubar.addMenu('其他')
        
        # 帮助菜单
        help_menu = menubar.addMenu('帮助')
        help_menu.addAction('使用说明')
        about_action = QAction('关于', self)
        help_menu.addAction(about_action)

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

def main():
    app = QApplication(sys.argv)
    
    # 设置应用程序样式
    app.setStyle('Fusion')
    
    # 创建启动界面
    splash = CustomSplashScreen()
    splash.show()
    
    # 创建主窗口
    window = MainWindow()
    
    # 模拟加载过程
    def update_splash():
        if not splash.progress():
            # 加载完成，显示主窗口
            window.show()
            splash.finish(window)
            timer.stop()
    
    # 设置定时器更新进度
    timer = QTimer()
    timer.timeout.connect(update_splash)
    timer.start(30)  # 每30毫秒更新一次
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main() 