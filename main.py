import sys
import os

# 添加项目根目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from PyQt5.QtWidgets import QApplication
from UI.UI_App_Root import MainWindow
from utils.db_manager import DBManager
from utils.logger import Logger

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
        window = MainWindow()
        window.show()
        logger.info("应用程序界面已显示")
        
        sys.exit(app.exec_())
    except Exception as e:
        logger.error(f"程序运行出错: {str(e)}")
        raise

if __name__ == '__main__':
    main() 