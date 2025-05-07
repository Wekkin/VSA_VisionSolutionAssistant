from dataclasses import dataclass
from datetime import datetime

@dataclass
class Project:
    id: int = None
    name: str = ""
    status: str = "进行中"  # 进行中, 已完成, 待审核
    progress: int = 0
    update_time: datetime = None
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'name': self.name,
            'status': self.status,
            'progress': self.progress,
            'update_time': self.update_time.strftime('%Y-%m-%d') if self.update_time else None
        }
    
    @classmethod
    def from_dict(cls, data):
        """从字典创建实例"""
        return cls(
            id=data.get('id'),
            name=data.get('name', ''),
            status=data.get('status', '进行中'),
            progress=data.get('progress', 0),
            update_time=datetime.strptime(data['update_time'], '%Y-%m-%d') if data.get('update_time') else None
        ) 