import sqlite3
from pathlib import Path

class DBManager:
    def __init__(self):
        self.db_path = Path('data/vsa.db')
        self.connection = None
        self.cursor = None
        
    def connect(self):
        """连接数据库"""
        if not self.db_path.parent.exists():
            self.db_path.parent.mkdir(parents=True)
        self.connection = sqlite3.connect(str(self.db_path))
        self.cursor = self.connection.cursor()
        
    def disconnect(self):
        """断开数据库连接"""
        if self.connection:
            self.connection.close()
            
    def execute(self, query, params=None):
        """执行SQL查询"""
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            self.connection.commit()
            return self.cursor.fetchall()
        except Exception as e:
            print(f"数据库执行错误: {e}")
            self.connection.rollback()
            return None
            
    def init_tables(self):
        """初始化数据库表"""
        # 创建配置表
        self.execute('''
            CREATE TABLE IF NOT EXISTS configurations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                station_id TEXT NOT NULL,
                camera_model TEXT,
                lens_model TEXT,
                light_model TEXT,
                resolution TEXT,
                fov TEXT,
                working_distance TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 创建项目表
        self.execute('''
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                status TEXT,
                progress INTEGER,
                update_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''') 