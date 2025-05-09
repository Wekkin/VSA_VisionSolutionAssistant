import os
import subprocess
import sys
import shutil

def build_appimage():
    print("开始构建 AppImage...")
    
    # 确保在项目根目录
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # 首先运行 PyInstaller 打包
    print("正在使用 PyInstaller 打包应用程序...")
    subprocess.run([
        "pyinstaller",
        "build.spec"
    ], check=True)
    
    # 创建 AppDir 结构
    print("正在创建 AppDir 结构...")
    os.makedirs("AppDir/usr/bin", exist_ok=True)
    os.makedirs("AppDir/usr/share/applications", exist_ok=True)
    os.makedirs("AppDir/usr/share/icons/hicolor/256x256/apps", exist_ok=True)
    
    # 复制可执行文件
    shutil.copy("dist/VSA_VisionSolutionAssistant/vsa_app", "AppDir/usr/bin/")
    
    # 复制并重命名图标文件到多个位置
    icon_paths = [
        "AppDir/vsa.png",  # 根目录
        "AppDir/usr/share/icons/hicolor/256x256/apps/vsa.png"  # 标准位置
    ]
    for icon_path in icon_paths:
        shutil.copy("icons/benzene-ring.png", icon_path)
    
    # 创建 desktop 文件
    desktop_entry = f'''[Desktop Entry]\nName=VSA视觉方案助手\nExec=vsa_app\nIcon=vsa\nType=Application\nCategories=Utility;\nComment=视觉方案助手\nVersion=1.0\nTerminal=false'''
    # 在两个位置都创建 desktop 文件
    desktop_paths = [
        "AppDir/vsa.desktop",  # 根目录
        "AppDir/usr/share/applications/vsa.desktop"  # 标准位置
    ]
    for desktop_path in desktop_paths:
        with open(desktop_path, "w", encoding="utf-8") as f:
            f.write(desktop_entry)
    
    # 创建 AppRun
    apprun_content = """#!/bin/sh
cd "${APPDIR}/usr/bin"
exec "${APPDIR}/usr/bin/vsa_app" "$@"
"""
    apprun_path = "AppDir/AppRun"
    with open(apprun_path, "w", encoding="utf-8") as f:
        f.write(apprun_content)
    
    # 设置权限
    os.chmod(apprun_path, 0o755)
    os.chmod("AppDir/usr/bin/vsa_app", 0o755)
    
    # 下载 appimagetool
    if not os.path.exists("appimagetool-x86_64.AppImage"):
        print("正在下载 appimagetool...")
        subprocess.run([
            "wget", "-c",
            "https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage"
        ], check=True)
        print("appimagetool-x86_64.AppImage 下载完成。")
    else:
        print("本地已存在 appimagetool-x86_64.AppImage，跳过下载。")
    os.chmod("appimagetool-x86_64.AppImage", 0o755)
    
    # 创建 AppImage
    print("正在创建 AppImage...")
    appimage_name = "VSA_VisionSolutionAssistant-x86_64.AppImage"
    subprocess.run([
        "./appimagetool-x86_64.AppImage",
        "--verbose",
        "AppDir",
        appimage_name
    ], check=True)
    
    print("AppImage 构建完成！")
    print(f"输出文件: {appimage_name}")

if __name__ == "__main__":
    try:
        build_appimage()
    except subprocess.CalledProcessError as e:
        print(f"构建过程中出现错误: {str(e)}")
        sys.exit(1)
    except Exception as e:
        print(f"发生未知错误: {str(e)}")
        sys.exit(1) 