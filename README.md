# 工业视觉检测办公助手

这是一个专门为工业视觉检测工程师设计的办公自动化工具，用于简化日常工作流程，提高工作效率。

## 主要功能

### 图片处理
- 批量图片导入与管理
- 智能ROI（感兴趣区域）提取
- 图像细节放大与分析
- 自动化缺陷检测与标注

### 报告生成
- 自动生成PPT报告
- 智能排版与布局
- 批次化处理与组织

### 配置管理
- 相机参数配置
- 检测参数管理
- 系统设置

## 技术栈

- Python 3.8+
- PyQt5 - GUI框架
- OpenCV - 图像处理
- python-pptx - PPT生成
- Pillow - 图像处理
- scikit-image - 图像分析

## 安装说明

1. 克隆仓库
```bash
git clone https://github.com/yourusername/industrial-vision-assistant.git
cd industrial-vision-assistant
```

2. 安装依赖
```bash
pip install -r requirements.txt
```

3. 运行程序
```bash
python main.py
```

## 使用说明

1. 启动程序后，通过顶部菜单栏访问各项功能
2. 在左侧面板选择并导入图片
3. 在原图区域通过鼠标拉框选择ROI
4. 在右侧查看放大的细节
5. 在底部添加分析评价
6. 使用导出功能生成报告

## 项目结构

```
industrial-vision-assistant/
├── src/
│   ├── image_import/
│   │   └── image_processor.py
│   └── splash_screen.py
├── resources/
│   └── README.md
├── main.py
├── requirements.txt
└── README.md
```

## 开发计划

- [ ] 添加批量处理功能
- [ ] 实现自动缺陷检测
- [ ] 添加数据库支持
- [ ] 优化用户界面
- [ ] 添加配置导出功能

## 贡献指南

欢迎提交 Pull Request 或创建 Issue。

## 许可证

MIT License