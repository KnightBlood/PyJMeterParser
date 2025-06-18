# PyJMeter

## 📌 项目简介
基于Python实现的JMeter扩展工具，提供多框架UI支持（Tkinter/NiceGUI/PySide6/Flet），支持JMX文件解析与可视化操作

## 📄 功能特性
- ✅ 多UI框架支持：tk/nicegui/flet/pyside6/wx
- ✅ JMX文件解析与可视化编辑
- ✅ 自定义参数配置系统
- ✅ 跨平台运行支持（Windows/macOS/Linux）
- ✅ PyWebView集成（NiceGUI专属）

## 📁 目录结构
```
├── business/        # 核心业务逻辑（JMX解析引擎）
├── java_implementation/ # Java实现的扩展模块
├── package/         # 第三方依赖包管理
├── ui/              # 多框架UI实现
│   ├── main_window.py       # Tkinter基础实现
│   ├── nicegui_main_window.py # NiceGUI专用实现
│   ├── flet_main_window.py    # Flet专用实现
│   └── pyside6_main_window.py # PySide6专用实现
├── utils/           # 工具类库
├── app.py           # 主程序入口
├── requirements.txt # 核心依赖列表
└── README.md        # 项目文档
```

## 🛠️ 安装指南
```bash
# 安装核心依赖
pip install -r requirements.txt

# 安装NiceGUI扩展支持（可选）
pip install nicegui pywebview

# 安装Flet扩展支持（可选）
pip install flet
```

## 🚀 快速启动
```bash
# 默认启动（弹出UI选择窗口）
python app.py

# 指定UI框架启动
python app.py --ui tk          # 启动Tkinter版本
python app.py --ui nicegui     # 启动NiceGUI版本
python app.py --ui pyside6     # 启动PySide6版本
python app.py --ui flet        # 启动Flet版本
```

## ⚙️ 特性配置
### NiceGUI专用配置
- 窗口大小：通过JavaScript动态控制（800x600）
- 服务器端口：8080（可修改）
- 热重载：已禁用（生产环境优化）

## 📌 注意事项
1. **Python版本要求**：NiceGUI版本需要Python 3.12+
2. **信号处理异常**：请始终在主进程中启动应用
3. **窗口大小控制**：修改ui/nicegui_main_window.py中的JavaScript脚本
4. **跨平台兼容性**：Windows/Mac/Linux通用，推荐使用虚拟环境

## 🤝 贡献指南
1. Fork仓库并创建开发分支
2. 提交PR时请包含完整测试
3. 遵循PEP8代码规范
4. 添加类型提示（Type Hints）

## 🛠️ 开发环境
```bash
# 推荐使用虚拟环境
python -m venv .venv
source .venv/bin/activate  # Windows使用 .venv\Scripts\activate

# 安装所有开发依赖
pip install -r requirements.txt -r dev-requirements.txt
```

## 🐞 问题排查
### 常见问题
- **信号处理错误**：确保通过`if __name__ == "__main__"`保护启动代码
- **依赖缺失**：使用`pip install <package> --no-cache-dir`强制重新安装
- **窗口显示异常**：检查防火墙设置是否阻止本地端口通信

## 📜 开源协议
[MIT License](https://opensource.org/licenses/MIT)