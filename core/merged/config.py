from dataclasses import dataclass
from datetime import datetime

@dataclass
class Configuration:
    id: int = None
    station_id: str = ""
    camera_model: str = ""
    lens_model: str = ""
    light_model: str = ""
    resolution: str = ""
    fov: str = ""
    working_distance: str = ""
    created_at: datetime = None
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'station_id': self.station_id,
            'camera_model': self.camera_model,
            'lens_model': self.lens_model,
            'light_model': self.light_model,
            'resolution': self.resolution,
            'fov': self.fov,
            'working_distance': self.working_distance,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }
    
    @classmethod
    def from_dict(cls, data):
        """从字典创建实例"""
        return cls(
            id=data.get('id'),
            station_id=data.get('station_id', ''),
            camera_model=data.get('camera_model', ''),
            lens_model=data.get('lens_model', ''),
            light_model=data.get('light_model', ''),
            resolution=data.get('resolution', ''),
            fov=data.get('fov', ''),
            working_distance=data.get('working_distance', ''),
            created_at=datetime.strptime(data['created_at'], '%Y-%m-%d %H:%M:%S') if data.get('created_at') else None
        ) 