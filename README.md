# 工业视觉辅助系统

这是一个基于PyQt5的工业视觉辅助系统，用于生成包含图片分析的PPT报告。系统提供了直观的图片处理界面，支持区域选择和细节放大功能。

## 主要特性

- 批量导入图片文件
- 图片细节区域选择和放大
- 自动生成PPT报告
- 支持评估意见编辑
- 可调节的界面布局
- 实时预览裁剪效果

## 系统要求

- Python 3.6+
- PyQt5
- python-pptx
- Pillow

## 安装步骤

1. 克隆仓库：
```bash
git clone https://github.com/yourusername/industrial-vision-assistant.git
cd industrial-vision-assistant
```

2. 安装依赖：
```bash
pip install -r requirements.txt
```

## 使用方法

1. 运行程序：
```bash
python Slide_generation.py
```

2. 使用步骤：
   - 点击"选择图片文件夹"导入图片
   - 在左侧列表选择要处理的图片
   - 编辑PPT标题
   - 在原图区域拖动鼠标选择要放大的细节部分
   - 在可行性分析区域输入评估意见
   - 点击"生成PPT"按钮生成演示文稿

## 界面说明

- 左侧面板：图片文件列表
- 右侧上方：PPT标题编辑区
- 右侧中间：原图显示和细节图显示区（可拖动分隔条调整大小）
- 右侧下方：评估意见输入区
- 底部：生成PPT按钮

## 注意事项

- 支持的图片格式：jpg、jpeg、png
- 生成的PPT文件将保存在程序运行目录下
- 裁剪区域会自动保持纵横比
- 界面布局支持自由调整

## 开发环境

- Python 3.8+
- PyQt5 5.15.0
- Windows/MacOS/Linux

## 许可证

MIT License

## 贡献

欢迎提交Issue和Pull Request。