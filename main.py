import sys
import os
import time  # 导入time模块

# 添加项目根目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from PyQt5.QtWidgets import QApplication, QProgressBar
from PyQt5.QtGui import QIcon
from UI.UI_App_Root import MainWindow
from utils.db_manager import DBManager
from utils.logger import Logger
from splash_screen import CustomSplashScreen  # 修复导入路径


def main():
    # 初始化日志记录器
    logger = Logger()
    logger.info("启动视觉方案助手应用程序")
    
    try:
        # 初始化数据库
        logger.info("正在初始化数据库...")
        db = DBManager()
        db.connect()
        db.init_tables()
        db.disconnect()
        logger.info("数据库初始化完成")
        
        # 启动应用
        logger.info("正在创建应用实例...")
        app = QApplication(sys.argv)
        
        # 设置应用图标
        icon_path = os.path.join(current_dir, 'icons', 'benzene-ring.png')
        if os.path.exists(icon_path):
            app.setWindowIcon(QIcon(icon_path))
            logger.info("已设置应用程序图标")
        else:
            logger.warning(f"图标文件不存在: {icon_path}")
        
        # 创建主窗口（但不显示）
        window = MainWindow()
        
        # 创建并显示启动画面，设置与主窗口大小一致
        splash = CustomSplashScreen()
        splash.setFixedSize(window.width(), window.height())  # 设置启动画面大小与主窗口一致
        splash.show()
        app.processEvents()  # 确保启动画面显示
        
        # 模拟加载过程，增加延时
        for i in range(99):
            splash.progress()
            app.processEvents()
            time.sleep(0.01)  # 增加延时，确保进度条加载过程可见
        
        # 关闭启动画面，显示主窗口
        splash.finish(window)
        window.show()
        logger.info("应用程序界面已显示")
        
        sys.exit(app.exec_())
    except Exception as e:
        logger.error(f"程序运行出错: {str(e)}")
        raise

if __name__ == '__main__':
    main() 