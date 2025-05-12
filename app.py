import argparse  # 新增导入
import importlib
import sys
import tkinter as tk

print("运行时路径:", sys.path)  # 验证运行时模块搜索路径
from tkinter import ttk

import pywinstyles

# 创建选择窗口
class UISelector(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("选择UI框架")
        self.geometry("300x185")

        pywinstyles.apply_style(self, "mica")
        
        ttk.Button(self, text="Tkinter", command=self.select_tk).pack(pady=5)
        ttk.Button(self, text="PySide6", command=self.select_pyside6).pack(pady=5)
        ttk.Button(self, text="wxPython", command=self.select_wx).pack(pady=5)
        self.selection = None
    
    def select_tk(self):
        self.selection = 'tk'
        self.destroy()
    
    def select_pyside6(self):
        self.selection = 'pyside6'
        self.destroy()

    def select_wx(self):
        self.selection = 'wx'
        self.destroy()

# 解析命令行参数
parser = argparse.ArgumentParser(description='JMeter JMX Parser')
parser.add_argument('--ui', type=str, default=None, choices=['tk', 'pyside6', 'wx'],
                    help='选择UI类型 (tk, pyside6, wx)')
args = parser.parse_args()

# 优先使用参数选择，否则弹出选择窗口
if args.ui:
    ui_type = args.ui
else:
    selector = UISelector()
    selector.mainloop()
    ui_type = selector.selection

# 动态导入对应的UI模块
if ui_type == 'pyside6':
    try:
        from PySide6.QtWidgets import QApplication
        ui_module = importlib.import_module('ui.pyside6_main_window')
    except ImportError:
        print("错误：未找到 PySide6 库，请先安装")
        sys.exit(1)
elif ui_type == 'wx':
    try:
        import wx
        ui_module = importlib.import_module('ui.wx_main_window')
    except ImportError:
        print("错误：未找到 wxPython 库，请先安装")
        sys.exit(1)
else:
    import tkinter as tk
    ui_module = importlib.import_module('ui.main_window')

# 创建并运行应用
if __name__ == "__main__":
    if ui_type == 'pyside6':
        app = QApplication(sys.argv)  # 使用原始sys.argv保持PySide6兼容性
        window = ui_module.App()
        window.show()
        sys.exit(app.exec())
    elif ui_type == 'wx':
        import wx
        app = wx.App(False)
        window = ui_module.App()
        app.MainLoop()
    else:
        root = tk.Tk()
        app = ui_module.App(root)
        root.mainloop()