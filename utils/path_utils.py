import sys
import os

def get_resource_path(relative_path):
    """
    获取资源文件的绝对路径，兼容PyInstaller打包和源码运行两种环境。
    :param relative_path: 相对路径，如'src/template.pptx'
    :return: 绝对路径
    """
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath('.'), relative_path) 