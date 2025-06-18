import tkinter as tk
import importlib
import sys
import argparse
from tkinter import ttk
import pywinstyles
import webview
from typing import Any, Tuple


# 创建选择窗口
class UISelector(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("选择UI框架")
        self.geometry("300x185")
        pywinstyles.apply_style(self, "mica")

        self.selection = None
        for ui_type in ['Tkinter', 'PySide6', 'wxPython', 'Flet', 'NiceGUI']:
            ttk.Button(self, text=ui_type, command=lambda t=ui_type.lower(): self.select(t)).pack(pady=5)

    def select(self, ui_type: str) -> None:
        self.selection = ui_type
        self.destroy()


# 动态导入UI模块
def load_ui_module(ui_type: str) -> Tuple[Any, Any]:
    try:
        if ui_type == 'pyside6':
            from PySide6.QtWidgets import QApplication
            return importlib.import_module('ui.pyside6_main_window'), QApplication
        elif ui_type == 'wx':
            import wx
            return importlib.import_module('ui.wx_main_window'), wx.App
        elif ui_type == 'nicegui':
            from nicegui import ui
            return importlib.import_module('ui.nicegui_main_window'), ui
        elif ui_type == 'flet':
            import flet as ft
            return importlib.import_module('ui.flet_main_window'), ft.app
        else:  # Default to Tkinter
            import tkinter as tk
            return importlib.import_module('ui.main_window'), tk.Tk
    except ImportError as e:
        print(f"错误：未找到 {ui_type} 库，请先安装。详细信息：{e}")
        sys.exit(1)


# 启动应用
def run_application(ui_type: str, ui_module: Any, app_class: Any) -> None:
    if ui_type == 'pyside6':
        app = app_class(sys.argv)
        window = ui_module.App()
        window.show()
        sys.exit(app.exec())
    elif ui_type == 'wx':
        app = app_class(False)
        window = ui_module.App()
        app.MainLoop()
    elif ui_type == 'nicegui':
        from nicegui import ui

        @ui.page('/')
        def main_page():
            window = ui_module.App()
            ui.add_body_html('<script>window.resizeTo(800, 600)</script>')

        def start_nicegui():
            ui.run(port=8080, show=False, reload=False, title="PyJMeter")

        import threading
        server_thread = threading.Thread(target=start_nicegui, daemon=True)
        server_thread.start()

        import time
        time.sleep(1)

        webview.create_window("PyJMeter", "http://localhost:8080", width=800, height=600)
        webview.start()
    elif ui_type == 'flet':
        app_class(target=lambda page: ui_module.App(page))
    else:  # Tkinter
        root = app_class()
        app = ui_module.App(root)
        root.mainloop()


# 主程序入口
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='JMeter JMX Parser')
    parser.add_argument('--ui', type=str, default=None,
                        choices=['tk', 'pyside6', 'wx', 'nicegui', 'flet'],
                        help='选择UI类型 (tk, pyside6, wx, nicegui, flet)')
    args = parser.parse_args()

    if args.ui:
        ui_type = args.ui
    else:
        selector = UISelector()
        selector.mainloop()
        ui_type = selector.selection

    if not ui_type:
        print("错误：未选择任何UI框架。")
        sys.exit(1)

    ui_module, app_class = load_ui_module(ui_type)
    run_application(ui_type, ui_module, app_class)
