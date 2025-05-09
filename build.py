import os
import shutil
import subprocess
import sys
import platform

def build_app():
    print("开始打包应用程序...")
    
    # 确保在项目根目录
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # 安装必要的打包工具
    print("正在安装 PyInstaller...")
    subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller==5.13.2"], check=True)
    
    # 使用PyInstaller打包
    print("开始打包应用程序...")
    subprocess.run([
        "pyinstaller",
        "--onefile",
        "--windowed",
        "--name=VSA视觉方案助手",
        "--icon=icons/benzene-ring.ico",
        "--add-data=icons:icons",
        "--add-data=config:config",
        "--add-data=UI:UI",
        "--add-data=utils:utils",
        "--add-data=core:core",
        "--add-data=data:data",
        "--hidden-import=PyQt5",
        "--hidden-import=PyQt5.QtCore",
        "--hidden-import=PyQt5.QtGui",
        "--hidden-import=PyQt5.QtWidgets",
        "--hidden-import=numpy",
        "--hidden-import=pandas",
        "--hidden-import=cv2",
        "--hidden-import=skimage",
        "--hidden-import=pyqtgraph",
        "--hidden-import=PIL",
        "main.py"
    ], check=True)
    
    # 创建发布目录
    dist_dir = "dist/VSA视觉方案助手"
    if not os.path.exists(dist_dir):
        os.makedirs(dist_dir)
    
    # 复制必要的文件到发布目录
    shutil.copy("README.md", dist_dir)
    shutil.copy("LICENSE", dist_dir)
    
    print("打包完成！")
    print(f"可执行文件位于: {os.path.abspath(dist_dir)}")

if __name__ == "__main__":
    try:
        build_app()
    except subprocess.CalledProcessError as e:
        print(f"打包过程中出现错误: {str(e)}")
        sys.exit(1)
    except Exception as e:
        print(f"发生未知错误: {str(e)}")
        sys.exit(1) 