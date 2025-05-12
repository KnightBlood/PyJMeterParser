import os
import re

import pywinstyles
import wx
import wx.lib.agw.flatnotebook as fnb

from ui.base_app import BaseApp


class App(BaseApp, wx.Frame):
    def __init__(self, master=None):
        BaseApp.__init__(self)
        wx.Frame.__init__(self, master, title="JMeter JMX Parser", size=(800, 600))
        self.replacement_frames = []  

        # 使用py-window-styles统一美化
        pywinstyles.apply_style(self, "mica")

        # 主面板和布局
        panel = wx.Panel(self)
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        panel.SetSizer(main_sizer)

        # 保存 panel 为实例属性
        self.panel = panel  # 👈 新增这一行

        # 添加状态栏
        self.status_bar = self.CreateStatusBar(2)
        self.status_bar.SetStatusWidths([-2, -1])
        self.SetStatusText("就绪", 0)
        
        # 文件路径输入框
        file_frame = wx.BoxSizer(wx.HORIZONTAL)
        
        self.label = wx.StaticText(panel, label="选择 JMX 文件或文件夹:", size=(150, -1))
        file_frame.Add(self.label, 0, wx.ALL, 5)
        
        self.file_path = wx.TextCtrl(panel, size=(-1, 30))  # 统一控件高度
        file_frame.Add(self.file_path, 1, wx.EXPAND | wx.ALL, 5)
        
        btn_size = (100, 30)  # 统一按钮尺寸
        self.browse_file_btn = wx.Button(panel, label="选择文件", size=btn_size)
        self.browse_file_btn.Bind(wx.EVT_BUTTON, self.browse_file)
        file_frame.Add(self.browse_file_btn, 0, wx.ALL, 5)
        
        self.browse_folder_btn = wx.Button(panel, label="选择文件夹", size=btn_size)
        self.browse_folder_btn.Bind(wx.EVT_BUTTON, self.browse_folder)
        file_frame.Add(self.browse_folder_btn, 0, wx.ALL, 5)
        
        main_sizer.Add(file_frame, 0, wx.EXPAND | wx.ALL, 5)
        
        # 参数输入区域
        param_frame = wx.BoxSizer(wx.HORIZONTAL)
        
        # 字母组合长度输入框
        length_box = wx.BoxSizer(wx.VERTICAL)
        self.length_label = wx.StaticText(panel, label="输入字母组合长度:", size=(150, -1))
        length_box.Add(self.length_label, 0, wx.ALL, 5)
        
        self.length_entry = wx.TextCtrl(panel, value="2", size=(50, 30))
        length_box.Add(self.length_entry, 0, wx.ALL, 5)
        
        param_frame.Add(length_box, 0, wx.ALL, 5)
        
        # 正则表达式输入框
        regex_box = wx.BoxSizer(wx.VERTICAL)
        self.regex_label = wx.StaticText(panel, label="输入正则表达式:", size=(150, -1))
        regex_box.Add(self.regex_label, 0, wx.ALL, 5)
        
        self.regex_entry = wx.TextCtrl(panel, value=r"http://\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}", size=(-1, 30))
        regex_box.Add(self.regex_entry, 0, wx.ALL | wx.EXPAND, 5)
        
        param_frame.Add(regex_box, 1, wx.ALL | wx.EXPAND, 5)
        
        main_sizer.Add(param_frame, 0, wx.EXPAND | wx.ALL, 5)
        
        # 复选框区域
        self.remove_header_cb = wx.CheckBox(panel, label="是否移除请求的Header")
        main_sizer.Add(self.remove_header_cb, 0, wx.ALL, 5)

        # 按钮区域
        button_frame = wx.BoxSizer(wx.HORIZONTAL)
        
        btn_def_size = (100, 30)  # 统一操作按钮尺寸
        self.add_replace_btn = wx.Button(panel, label="增加替换项", size=btn_def_size)
        self.add_replace_btn.Bind(wx.EVT_BUTTON, self.add_replacement_frame)
        button_frame.Add(self.add_replace_btn, 0, wx.ALL, 5)
        
        self.del_replace_btn = wx.Button(panel, label="删除替换项", size=btn_def_size)
        self.del_replace_btn.Bind(wx.EVT_BUTTON, self.remove_replacement_frame)
        button_frame.Add(self.del_replace_btn, 0, wx.ALL, 5)
        
        self.parse_btn = wx.Button(panel, label="解析 JMX", size=btn_def_size)
        self.parse_btn.Bind(wx.EVT_BUTTON, self.parse_jmx)
        button_frame.Add(self.parse_btn, 0, wx.ALL, 5)
        
        self.save_btn = wx.Button(panel, label="保存 JMX", size=btn_def_size)
        self.save_btn.Bind(wx.EVT_BUTTON, self.save_jmx)
        button_frame.Add(self.save_btn, 0, wx.ALL, 5)
        
        self.save_all_btn = wx.Button(panel, label="批量保存 JMX", size=btn_def_size)
        self.save_all_btn.Bind(wx.EVT_BUTTON, self.save_all_jmx)
        button_frame.Add(self.save_all_btn, 0, wx.ALL, 5)
        
        main_sizer.Add(button_frame, 0, wx.EXPAND | wx.ALL, 5)
        
        # Notebook组件
        self.notebook = fnb.FlatNotebook(panel, style=fnb.FNB_NO_X_BUTTON)
        main_sizer.Add(self.notebook, 1, wx.EXPAND | wx.ALL, 5)

        # 进度条
        self.progress = wx.Gauge(panel, range=100, size=(-1, 25))
        main_sizer.Add(self.progress, 0, wx.EXPAND | wx.ALL, 5)

        # 替换内容输入区域
        self.replacement_container = wx.BoxSizer(wx.VERTICAL)
        self.add_replacement_frame()
        main_sizer.Add(self.replacement_container, 0, wx.EXPAND | wx.ALL, 5)

        
        # 确保布局正确更新
        panel.Layout()  # {{ 新增：确保面板布局正确更新 }}
        self.Layout()
        self.Show()
        
        self.parsers = {}

    def get_file_path(self) -> str:
        return self.file_path.GetValue()

    def set_file_path(self, path: str):
        self.file_path.SetValue(path)

    def show_error(self, message: str):
        wx.MessageBox(message, "错误", wx.OK | wx.ICON_ERROR)

    def get_replacement_entries(self) -> list[tuple[str, str]]:
        return [(entry1.GetValue(), entry2.GetValue()) for _, entry1, entry2 in self.replacement_frames]

    def clear_tabs(self):
        self.notebook.DeleteAllPages()

    def add_tab(self, title: str, content: str):
        text_ctrl = wx.TextCtrl(self.notebook, style=wx.TE_MULTILINE | wx.TE_READONLY)
        text_ctrl.SetValue(content)
        self.notebook.AddPage(text_ctrl, title)

    def get_selected_file(self) -> str:
        selected_index = self.notebook.GetSelection()
        if selected_index == -1:
            return None
        tab_text = self.notebook.GetPageText(selected_index)
        return next((file for file in self.parsers if f"解析结果 - {os.path.basename(file)}" == tab_text), None)

    def update_status(self, message: str):
        self.SetStatusText(message, 0)

    def get_length_entry(self) -> int:
        return int(self.length_entry.GetValue())

    def get_regex_entry(self) -> str:
        return self.regex_entry.GetValue()

    def is_remove_header_checked(self) -> bool:
        return self.remove_header_cb.IsChecked()

    def set_progress(self, value: int, maximum: int):
        self.progress.SetRange(maximum)
        self.progress.SetValue(value)

    def get_progress_value(self) -> int:
        return self.progress.GetValue()

    def ask_save_file(self) -> str:
        with wx.FileDialog(self, "保存 JMX 文件", wildcard="JMX files (*.jmx)|*.jmx",
                          style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT) as dlg:
            if dlg.ShowModal() == wx.ID_OK:
                return dlg.GetPath()
        return ""

    def ask_save_directory(self) -> str:
        with wx.DirDialog(self, "选择输出文件夹") as dlg:
            if dlg.ShowModal() == wx.ID_OK:
                return dlg.GetPath()
        return ""

    def show_info(self, message: str):
        wx.MessageBox(message, "提示", wx.OK | wx.ICON_INFORMATION)

    def add_replacement_frame(self, event=None):
        frame = wx.BoxSizer(wx.HORIZONTAL)
        
        # 确保使用 self.panel 作为父对象
        label1 = wx.StaticText(self.panel, label="被替换内容:", size=(100, -1))  # 👈 使用 self.panel 作为父窗口
        entry1 = wx.TextCtrl(self.panel, size=(200, 30))  # 👈 使用 self.panel 作为父窗口
        
        label2 = wx.StaticText(self.panel, label="替换内容:", size=(100, -1))  # 👈 使用 self.panel 作为父窗口
        entry2 = wx.TextCtrl(self.panel, size=(200, 30))  # 👈 使用 self.panel 作为父窗口
        
        frame.Add(label1, 0, wx.ALL, 5)
        frame.Add(entry1, 0, wx.ALL, 5)
        frame.Add(label2, 0, wx.ALL, 5)
        frame.Add(entry2, 0, wx.ALL, 5)
        
        self.replacement_container.Add(frame, 0, wx.EXPAND | wx.ALL, 5)
        self.replacement_frames.append((frame, entry1, entry2))
        
        # 确保布局正确更新
        self.replacement_container.Layout()  # {{ 新增：确保 replacement_container 布局正确更新 }}
        self.panel.Layout()  # {{ 新增：确保面板布局正确更新 }}
        self.Layout()

    def remove_replacement_frame(self, event=None):
        if self.replacement_frames:
            # 修改：解包三个值（第一个值为占位符）
            frame, entry1, entry2 = self.replacement_frames.pop()
            frame.Destroy()
            entry1.Destroy()
            entry2.Destroy()

            children = self.replacement_container.GetChildren()
            if children:
                # 获取最后一个 sizer item 的索引
                last_index = len(children) - 1
                # 使用索引代替窗口对象进行 Detach
                self.replacement_container.Detach(last_index)

                # 重新计算布局
                self.replacement_container.Layout()
                self.panel.Layout()
                self.Layout()

    def browse_file(self, event):
        with wx.FileDialog(self, "选择 JMX 文件", wildcard="JMX files (*.jmx)|*.jmx",
                          style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as dlg:
            if dlg.ShowModal() == wx.ID_OK:
                self.file_path.SetValue(dlg.GetPath())
    
    def browse_folder(self, event):
        with wx.DirDialog(self, "选择文件夹") as dlg:
            if dlg.ShowModal() == wx.ID_OK:
                self.file_path.SetValue(dlg.GetPath())
    
    def parse_jmx(self, event):
        super().parse_jmx()

    def on_length_text_changed(self, event):
        # 输入验证：只允许正整数
        value = self.length_entry.GetValue()
        if not value.isdigit() or int(value) < 1:
            self.length_entry.SetBackgroundColour(wx.Colour(255, 100, 100))
            self.SetStatusText("警告：请输入有效的字母组合长度（大于0的整数）", 0)
        else:
            self.length_entry.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOW))
            self.SetStatusText("就绪", 0)
        event.Skip()

    def on_regex_text_changed(self, event):
        # 正则表达式格式验证
        try:
            re.compile(self.regex_entry.GetValue())
            self.regex_entry.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOW))
            self.SetStatusText("就绪", 0)
        except re.error:
            self.regex_entry.SetBackgroundColour(wx.Colour(255, 100, 100))
            self.SetStatusText("警告：正则表达式格式错误", 0)
        event.Skip()

    def on_remove_header_checked(self, event):
        self.SetStatusText(f"头部移除状态：{'启用' if self.remove_header_cb.IsChecked() else '禁用'}", 0)
        event.Skip()

    def on_progress_update(self, value, event):
        """更新状态栏进度显示"""
        self.SetStatusText(f"处理进度：{value}%", 1)
        event.Skip()

    def save_jmx(self, event):
        super().save_jmx()

    def save_all_jmx(self, event):
        super().save_all_jmx()
