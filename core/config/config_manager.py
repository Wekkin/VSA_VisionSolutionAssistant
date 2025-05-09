class ConfigManager:
    def __init__(self):
        self.current_config = None
        
    def load_config(self, config_id):
        """加载配置"""
        pass
        
    def save_config(self, config_data):
        """保存配置"""
        pass
        
    def export_config(self, format_type='csv'):
        """导出配置"""
        pass
        
    def import_config(self, file_path):
        """导入配置"""
        pass
        
    def validate_config(self, config_data):
        """验证配置有效性"""
        pass
        
    def get_camera_models(self):
        """获取相机型号列表"""
        pass
        
    def get_lens_models(self):
        """获取镜头型号列表"""
        pass
        
    def get_light_models(self):
        """获取光源型号列表"""
        pass 