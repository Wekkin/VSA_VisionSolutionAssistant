# 视觉方案助手 (Vision Solution Assistant)

一个用于辅助视觉方案设计和管理的桌面应用程序。

## 功能特点

- 项目管理：管理和追踪视觉项目的进度
- POC制作：快速生成视觉方案的概念验证
- 配置记录：记录和管理视觉系统的配置信息
- 集成分析：分析视觉系统的集成方案
- 功能拓展：支持插件式功能扩展

## 技术栈

- Python 3.8+
- PyQt5：用户界面框架
- SQLite：本地数据存储
- Logging：日志记录

## 安装说明

1. 克隆仓库：
```bash
git clone https://github.com/[your-username]/VSA_VisionSolutionAssistant.git
cd VSA_VisionSolutionAssistant
```

2. 创建虚拟环境：
```bash
python -m venv vsa_env
source vsa_env/bin/activate  # Linux/Mac
# 或
vsa_env\Scripts\activate  # Windows
```

3. 安装依赖：
```bash
pip install -e .
```

4. 运行程序：
```bash
python main.py
```

## 项目结构

```
VSA_VisionSolutionAssistant/
├── core/               # 核心业务逻辑
├── UI/                 # 用户界面
├── utils/             # 工具类
├── models/            # 数据模型
├── resources/         # 资源文件
├── logs/              # 日志文件
├── main.py            # 程序入口
├── setup.py           # 安装配置
└── README.md          # 项目说明
```

## 开发说明

- 遵循PEP 8编码规范
- 使用类型提示
- 编写单元测试
- 保持代码文档更新

## 贡献指南

1. Fork 项目
2. 创建特性分支
3. 提交更改
4. 推送到分支
5. 创建 Pull Request

## 许可证

[MIT License](LICENSE)