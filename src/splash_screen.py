from PyQt5.QtWidgets import QSplashScreen, QProgressBar, QApplication
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPixmap, QPainter, QColor
import os

class CustomSplashScreen(QSplashScreen):
    def __init__(self):
        # 创建启动界面背景图
        splash_pix = QPixmap('resources/splash_background.png')
        super().__init__(splash_pix)
        
        # 设置窗口标志
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setWindowFlag(Qt.WindowStaysOnTopHint)
        
        # 创建进度条
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setGeometry(50, splash_pix.height() - 50, splash_pix.width() - 100, 20)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #2196F3;
                border-radius: 5px;
                background-color: #E3F2FD;
                text-align: center;
                color: #000000;
            }
            QProgressBar::chunk {
                background-color: #2196F3;
                border-radius: 3px;
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
        
    def progress(self):
        """更新进度条"""
        current_value = self.progress_bar.value()
        if current_value < 100:
            # 更新进度
            new_value = current_value + 1
            self.progress_bar.setValue(new_value)
            
            # 更新加载消息
            message_index = min(len(self.loading_messages) - 1, new_value // 20)
            self.current_message = self.loading_messages[message_index]
            self.repaint()
            
            # 返回是否完成
            return new_value < 100
        return False
    
    def drawContents(self, painter: QPainter):
        """重写绘制方法，添加自定义文本"""
        # 绘制加载消息
        painter.setPen(QColor(33, 150, 243))
        painter.setFont(QApplication.font())
        painter.drawText(self.rect(), Qt.AlignBottom | Qt.AlignHCenter, 
                        self.current_message) 