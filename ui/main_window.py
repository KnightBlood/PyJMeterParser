import logging
import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

import pywinstyles

from ui.base_app import BaseApp


class App(BaseApp):
    def __init__(self, master):
        BaseApp.__init__(self)
        self.master = master
        master.title("JMeter JMX Parser")
        master.geometry("800x600")

        # 使用py-window-styles统一美化
        pywinstyles.apply_style(master, "mica")

        # 创建主框架（使用grid布局替代pack）
        main_frame = ttk.Frame(master, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建状态栏
        self.status_bar = ttk.Label(master, text="就绪", relief=tk.SUNKEN)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        # 配置网格列权重
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_rowconfigure(4, weight=1)
        
        # 文件路径输入框
        file_frame = ttk.Frame(main_frame)
        file_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        
        self.label = ttk.Label(file_frame, text="选择 JMX 文件或文件夹:", width=20)
        self.label.pack(side=tk.LEFT, padx=(0, 10))
        
        self.file_path = ttk.Entry(file_frame, width=50)
        self.file_path.pack(side=tk.LEFT, padx=(0, 10), fill=tk.X, expand=True)
        
        self.browse_file_button = ttk.Button(file_frame, text="选择文件", command=self.browse_file, width=10)
        self.browse_file_button.pack(side=tk.LEFT, padx=(0, 5))
        
        self.browse_folder_button = ttk.Button(file_frame, text="选择文件夹", command=self.browse_folder, width=10)
        self.browse_folder_button.pack(side=tk.LEFT, padx=(0, 5))
        
        # 参数输入区域
        param_frame = ttk.Frame(main_frame)
        param_frame.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        
        # 字母组合长度输入框
        length_frame = ttk.Frame(param_frame)
        length_frame.pack(side=tk.LEFT, padx=(0, 20))
        
        self.length_label = ttk.Label(length_frame, text="输入字母组合长度:", width=20)
        self.length_label.pack(side=tk.LEFT)
        
        self.length_entry = ttk.Entry(length_frame, width=5)
        self.length_entry.insert(0, "2")
        self.length_entry.pack(side=tk.LEFT, padx=(5, 0))
        
        # 正则表达式输入框
        regex_frame = ttk.Frame(param_frame)
        regex_frame.pack(side=tk.LEFT, expand=True, fill=tk.X)
        
        self.regex_label = ttk.Label(regex_frame, text="输入正则表达式:", width=20)
        self.regex_label.pack(side=tk.LEFT)
        
        self.regex_entry = ttk.Entry(regex_frame, width=50)
        self.regex_entry.insert(0, r"http://\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}")
        self.regex_entry.pack(side=tk.LEFT, padx=(5, 0), fill=tk.X, expand=True)
        
        # 复选框区域
        checkbox_frame = ttk.Frame(main_frame)
        checkbox_frame.grid(row=2, column=0, sticky="ew", pady=(0, 10))
        
        self.remove_header_var = tk.BooleanVar(value=False)
        remove_header_checkbox = ttk.Checkbutton(checkbox_frame, text="是否移除请求的Header", variable=self.remove_header_var)
        remove_header_checkbox.pack(side=tk.LEFT)

        # 按钮区域
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, sticky="ew", pady=(0, 10))
        
        button_container = ttk.Frame(button_frame)
        button_container.pack(side=tk.LEFT)
        
        self.add_replacement_button = ttk.Button(button_container, text="增加替换项", command=self.add_replacement_frame)
        self.add_replacement_button.pack(side=tk.LEFT, padx=(0, 5))
        
        self.remove_replacement_button = ttk.Button(button_container, text="删除替换项", command=self.remove_replacement_frame)
        self.remove_replacement_button.pack(side=tk.LEFT, padx=(0, 5))
        
        self.parse_button = ttk.Button(button_container, text="解析 JMX", command=self.parse_jmx)
        self.parse_button.pack(side=tk.LEFT, padx=(0, 5))
        
        self.save_button = ttk.Button(button_container, text="保存 JMX", command=self.save_jmx)
        self.save_button.pack(side=tk.LEFT, padx=(0, 5))
        
        self.save_all_button = ttk.Button(button_container, text="批量保存 JMX", command=self.save_all_jmx)
        self.save_all_button.pack(side=tk.LEFT, padx=(0, 5))
        
        # Notebook组件
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.grid(row=4, column=0, sticky="nsew")

        # 进度条
        progress_frame = ttk.Frame(main_frame)
        progress_frame.grid(row=5, column=0, sticky="ew", pady=(10, 0))
        
        self.progress = ttk.Progressbar(progress_frame, orient="horizontal", length=300, mode="determinate")
        self.progress.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # 替换内容输入区域
        self.replacement_frames = []
        self.add_replacement_frame()
        
    def get_file_path(self) -> str:
        return self.file_path.get()

    def set_file_path(self, path: str):
        self.file_path.delete(0, tk.END)
        self.file_path.insert(0, path)

    def show_error(self, message: str):
        messagebox.showerror("错误", message)

    def get_replacement_entries(self) -> list[tuple[str, str]]:
        return [(entry1.get(), entry2.get()) for _, entry1, entry2 in self.replacement_frames]

    def add_tab(self, title: str, content: str):
        new_tab = tk.Text(self.notebook, height=15, width=60)
        new_tab.insert(tk.END, content)
        new_tab.pack(fill=tk.BOTH, expand=True)
        self.notebook.add(new_tab, text=title)

    def clear_tabs(self):
        while self.notebook.index("end") > 0:
            self.notebook.forget(0)

    def get_selected_file(self) -> str:
        selected_tab = self.notebook.select()
        tab_text = self.notebook.tab(selected_tab, "text")
        return next((file for file in self.parsers if f"解析结果 - {os.path.basename(file)}" == tab_text), None)

    def update_status(self, message: str):
        self.status_bar.config(text=message)

    def get_length_entry(self) -> int:
        return int(self.length_entry.get())

    def get_regex_entry(self) -> str:
        return self.regex_entry.get()

    def is_remove_header_checked(self) -> bool:
        return self.remove_header_var.get()

    def set_progress(self, value: int, maximum: int):
        self.progress["maximum"] = maximum
        self.progress["value"] = value

    def get_progress_value(self) -> int:
        return self.progress["value"]

    def ask_save_file(self) -> str:
        root = tk.Tk()
        root.withdraw()
        file_path = filedialog.asksaveasfilename(defaultextension=".jmx", filetypes=[("JMX files", "*.jmx")])
        root.destroy()
        return file_path

    def ask_save_directory(self) -> str:
        root = tk.Tk()
        root.withdraw()
        folder_path = filedialog.askdirectory()
        root.destroy()
        return folder_path

    def show_info(self, message: str):
        messagebox.showinfo("提示", message)

    def add_replacement_frame(self):
        frame = ttk.Frame(self.master)
        frame.pack(fill=tk.X, pady=(0, 10))
        
        label1 = ttk.Label(frame, text="被替换内容:")
        label1.pack(side=tk.LEFT, padx=(0, 10))
        
        entry1 = ttk.Entry(frame, width=30)
        entry1.pack(side=tk.LEFT, padx=(0, 10))
        
        label2 = ttk.Label(frame, text="替换内容:")
        label2.pack(side=tk.LEFT, padx=(0, 10))
        
        entry2 = ttk.Entry(frame, width=30)
        entry2.pack(side=tk.LEFT, padx=(0, 10))
        
        self.replacement_frames.append((frame, entry1, entry2))
        
    def remove_replacement_frame(self):
        if self.replacement_frames:
            frame, entry1, entry2 = self.replacement_frames.pop()
            frame.destroy()

    def browse_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("JMX files", "*.jmx")])
        if file_path:
            self.set_file_path(file_path)
    
    def browse_folder(self):
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.set_file_path(folder_path)
    
    def parse_jmx(self):
        super().parse_jmx()

    # 解析单个文件
    def parse_single_file(self, jmx_file, length, remove_header, pattern):
        super().parse_single_file(jmx_file, length, remove_header, pattern)
        replacement_frames = [(entry1.get(), entry2.get()) for _, entry1, entry2 in self.replacement_frames]

    # 解析目录中的所有JMX文件
    def parse_directory(self, directory, length, remove_header, pattern):
        jmx_files = [os.path.join(directory, f) for f in os.listdir(directory) if f.endswith('.jmx')]
        total_files = len(jmx_files)
        self.progress["maximum"] = total_files
        self.progress["value"] = 0  # 初始化进度条
        
        for file in jmx_files:
            try:
                self.parse_single_file(file, length, remove_header, pattern)
                self.progress["value"] += 1  # 更新进度条
                self.master.update_idletasks()  # 确保界面更新
            except Exception as e:
                logging.error(f"处理 {file} 时出错: {e}")
                messagebox.showerror("错误", f"处理 {file} 时出错: {e}")
        
        messagebox.showinfo("完成", "所有文件解析完成")
        
    # 批量保存所有解析后的JMX文件
    def save_all_jmx(self):
        if not self.parsers:
            messagebox.showerror("错误", "请先解析一个 JMX 文件")
            return
        
        output_dir = filedialog.askdirectory()
        if not output_dir:
            return
        
        total_files = len(self.parsers)
        self.progress["maximum"] = total_files
        self.progress["value"] = 0  # 初始化进度条
        
        for jmx_file, parser in self.parsers.items():
            try:
                output_file = os.path.join(output_dir, os.path.basename(jmx_file))
                success = parser.save_jmx(output_file)
                if success:
                    self.progress["value"] += 1  # 更新进度条
                    self.master.update_idletasks()  # 确保界面更新
                else:
                    logging.error(f"保存 {jmx_file} 时出错")
                    messagebox.showerror("错误", f"保存 {jmx_file} 时出错")
            except Exception as e:
                logging.error(f"保存 {jmx_file} 时出错: {e}")
                messagebox.showerror("错误", f"保存 {jmx_file} 时出错")
        
        messagebox.showinfo("成功", f"所有 JMX 文件已保存到 {output_dir}")
        
    # 保存JMX文件
    def save_jmx(self):
        if not self.parsers:
            messagebox.showerror("错误", "请先解析一个 JMX 文件")
            return
        
        selected_tab = self.notebook.select()
        tab_text = self.notebook.tab(selected_tab, "text")
        jmx_file = next((file for file, parser in self.parsers.items() if f"解析结果 - {os.path.basename(file)}" == tab_text), None)
        
        if not jmx_file:
            messagebox.showerror("错误", "无法确定要保存的 JMX 文件")
            return
        
        output_file = filedialog.asksaveasfilename(defaultextension=".jmx", filetypes=[("JMX files", "*.jmx")])
        if output_file:
            parser = self.parsers[jmx_file]
            success = parser.save_jmx(output_file)
            if success:
                messagebox.showinfo("成功", f"JMX 文件已保存到 {output_file}")
            else:
                logging.error("保存 JMX 文件时出错")
                messagebox.showerror("错误", "保存 JMX 文件时出错")
