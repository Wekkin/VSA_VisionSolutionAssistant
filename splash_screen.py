from PyQt5.QtWidgets import QSplashScreen, QProgressBar, QApplication, QLabel
from PyQt5.QtCore import Qt, QTimer, QRect, QPoint
from PyQt5.QtGui import QPixmap, QPainter, QColor, QLinearGradient, QGradient, QFont, QPen
import os

class CustomSplashScreen(QSplashScreen):
    def __init__(self):
        # 创建渐变背景
        splash_width = 1200
        splash_height = 800
        gradient_pixmap = self.create_gradient_background(splash_width, splash_height)
        super().__init__(gradient_pixmap)
        
        # 设置窗口标志
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setWindowFlag(Qt.WindowStaysOnTopHint)
        
        # 创建标题标签
        self.title_label = QLabel(self)
        self.title_label.setText("视觉办公助手")
        self.title_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 38px;
                font-weight: bold;
                font-family: "Arial";
            }
        """)
        # 将标题放置在窗口正中心
        title_y = (splash_height - 40) // 2  # 40是标题高度
        self.title_label.setGeometry(0, title_y, splash_width, 40)
        self.title_label.setAlignment(Qt.AlignCenter)
        
        # 创建版本标签
        self.version_label = QLabel(self)
        self.version_label.setText("Vision Proof of Concept")
        self.version_label.setStyleSheet("""
            QLabel {
                color: #FFFFFF;
                font-size: 14px;
                font-family: "Arial";
            }
        """)
        # 调整版本标签位置，放在标题下方
        version_y = title_y + 50  # 标题下方50像素
        self.version_label.setGeometry(0, version_y, splash_width, 30)
        self.version_label.setAlignment(Qt.AlignCenter)
        
        # 创建进度条
        self.progress_bar = QProgressBar(self)
        progress_width = splash_width - 100
        self.progress_bar.setGeometry(50, splash_height - 100, progress_width, 20)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #FFFFFF;
                border-radius: 10px;
                background-color: #FFFFFF;
                color: #333333;
                text-align: center;
            }
            QProgressBar::chunk {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #0000cf,
                    stop:0.5 #f132fb,
                    stop:1 #a1ecfe
                );
                border-radius: 8px;
            }
        """)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        
        # 设置加载消息
        self.loading_messages = [
            "正在初始化应用程序...",
            "加载图像处理模块...",
            "准备用户界面...",
            "配置系统参数...",
            "即将完成..."
        ]
        self.current_message = ""
        
        # 创建消息标签
        self.message_label = QLabel(self)
        self.message_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 14px;
            }
        """)
        self.message_label.setGeometry(0, splash_height - 130, splash_width, 30)
        self.message_label.setAlignment(Qt.AlignCenter)
        
    def create_gradient_background(self, width, height):
        """创建渐变背景"""
        pixmap = QPixmap(width, height)
        pixmap.fill(Qt.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # 创建渐变
        gradient = QLinearGradient(0, 0, width, height)
        gradient.setColorAt(0, QColor(0, 0, 207))      # 深蓝色 #0000cf
        gradient.setColorAt(0.5, QColor(241, 50, 251)) # 亮粉色 #f132fb
        gradient.setColorAt(1, QColor(161, 236, 254))  # 浅蓝色 #a1ecfe
        
        # 填充背景
        painter.fillRect(0, 0, width, height, gradient)
        
        # 添加科技感网格和线条效果
        painter.setPen(QPen(QColor(255, 255, 255, 30), 1))
        
        # 绘制交叉的对角线网格
        grid_size = 40
        for i in range(-height, width + height, grid_size):
            # 主对角线
            painter.drawLine(i, 0, i + height, height)
            painter.drawLine(i, height, i + height, 0)
            
            # 次对角线（垂直偏移）
            painter.drawLine(i + grid_size//2, 0, i + height + grid_size//2, height)
            painter.drawLine(i + grid_size//2, height, i + height + grid_size//2, 0)
        
        # 添加装饰性几何图形
        painter.setPen(QPen(QColor(255, 255, 255, 40), 2))
        # 绘制几个大的菱形
        for i in range(3):
            x = width // 4 * (i + 1)
            y = height // 3
            size = 80
            points = [
                QPoint(x, y - size),
                QPoint(x + size, y),
                QPoint(x, y + size),
                QPoint(x - size, y)
            ]
            for j in range(4):
                painter.drawLine(points[j], points[(j + 1) % 4])
                
        painter.end()
        return pixmap
        
    def progress(self):
        """更新进度条"""
        current_value = self.progress_bar.value()
        if current_value < 99:
            # 更新进度
            new_value = current_value + 1
            self.progress_bar.setValue(new_value)
            
            # 更新加载消息
            message_index = min(len(self.loading_messages) - 1, new_value // 20)
            self.current_message = self.loading_messages[message_index]
            self.message_label.setText(self.current_message)
            
            # 返回是否完成
            return new_value < 99
        return False 