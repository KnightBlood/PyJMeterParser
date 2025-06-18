import flet as ft
from ui.base_app import BaseApp
import os

class App(BaseApp):
    def __init__(self, page: ft.Page):
        BaseApp.__init__(self)
        self.page = page
        page.title = "JMeter JMX Parser"
        page.window_width = 800
        page.window_height = 600
        
        # 文件选择器
        self.file_picker = ft.FilePicker()
        page.overlay.append(self.file_picker)
        
        # 状态栏
        self.status_bar = ft.Text("就绪", size=14)
        status_container = ft.Container(
            content=self.status_bar,
            padding=ft.padding.all(8),
            bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.ON_SURFACE_VARIANT),
            border_radius=ft.border_radius.all(4),
            margin=ft.margin.only(top=10)
        )
        
        # 文件路径输入框
        self.file_path = ft.TextField(expand=True, read_only=True, height=40)
        self.browse_file_button = ft.ElevatedButton(
            "选择文件", 
            on_click=lambda _: self.file_picker.pick_files(allow_multiple=False)
        )
        self.browse_folder_button = ft.ElevatedButton(
            "选择文件夹", 
            on_click=lambda _: self.file_picker.get_directory_path()
        )
        
        file_row = ft.Row([
            ft.Text("选择 JMX 文件或文件夹:", width=200),
            self.file_path,
            self.browse_file_button,
            self.browse_folder_button
        ], spacing=10, vertical_alignment=ft.CrossAxisAlignment.START)
        
        # 参数输入区域
        self.length_entry = ft.TextField(value="2", width=50, height=40)
        self.regex_entry = ft.TextField(
            value=r"http://\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}", 
            expand=True,
            height=40
        )
        
        param_row = ft.Row([
            ft.Text("输入字母组合长度:", width=200),
            self.length_entry,
            ft.Text("输入正则表达式:", width=150),
            self.regex_entry
        ], spacing=10, vertical_alignment=ft.CrossAxisAlignment.START)
        
        # 复选框
        self.remove_header_checkbox = ft.Checkbox(label="是否移除请求的Header")
        
        # 按钮区域
        self.add_replacement_button = ft.ElevatedButton("增加替换项", on_click=self.add_replacement_frame)
        self.remove_replacement_button = ft.ElevatedButton("删除替换项", on_click=self.remove_replacement_frame)
        self.parse_button = ft.ElevatedButton("解析 JMX", on_click=self.parse_jmx)
        self.save_button = ft.ElevatedButton("保存 JMX", on_click=self.save_jmx)
        self.save_all_button = ft.ElevatedButton("批量保存 JMX", on_click=self.save_all_jmx)
        
        button_row = ft.Row([
            self.add_replacement_button,
            self.remove_replacement_button,
            self.parse_button,
            self.save_button,
            self.save_all_button
        ], spacing=10)
        
        # 替换项容器
        self.replacement_container = ft.Column(spacing=10)
        
        # 进度条
        self.progress = ft.ProgressBar(width=page.window_width-200, value=0, height=20, color=ft.Colors.PRIMARY)
        progress_container = ft.Container(
            content=ft.Column([
                ft.Text("进度:"),
                self.progress
            ]),
            padding=ft.padding.all(10)
        )
        
        # Notebook（使用TabView代替）
        self.notebook = ft.Tabs()
        
        # 主内容
        main_content = ft.Column([
            file_row,
            param_row,
            self.remove_header_checkbox,
            button_row,
            ft.Text("替换内容设置:", size=16, weight=ft.FontWeight.BOLD),
            self.replacement_container,
            progress_container,
            ft.Divider(),
            ft.Text("解析结果:", size=16, weight=ft.FontWeight.BOLD),
            self.notebook
        ], spacing=20, scroll=ft.ScrollMode.AUTO)
        
        # 将文件选择器回调绑定到页面
        self.file_picker.on_result = self.handle_file_picker_result
        
        # 主布局
        page.add(
            ft.Container(
                content=ft.ListView(
                    controls=[main_content],
                    padding=20
                ),
                expand=True
            ),
            status_container
        )
        
        # 初始化替换项
        self.replacement_frames = []
        self.add_replacement_frame()

    def handle_file_picker_result(self, e: ft.FilePickerResultEvent):
        if e.path:
            self.set_file_path(e.path)
        elif e.files:
            if e.files:
                self.set_file_path(e.files[0].path)

    def set_file_path(self, path: str):
        self.file_path.value = path
        self.page.update()

    def show_error(self, message: str):
        self.page.dialog = ft.AlertDialog(title=ft.Text("错误"), content=ft.Text(message))
        self.page.dialog.open = True
        self.page.update()

    def get_replacement_entries(self) -> list[tuple[str, str]]:
        return [(entry1.value, entry2.value) for _, entry1, entry2 in self.replacement_frames]

    def add_tab(self, title: str, content: str):
        self.notebook.tabs.append(ft.Tab(text=title, content=ft.Markdown(content)))
        self.page.update()

    def clear_tabs(self):
        self.notebook.tabs.clear()
        self.page.update()

    def get_selected_file(self) -> str:
        if not self.notebook.tabs or not self.notebook.tabs:
            return None
        selected_index = self.notebook.selected_index
        if selected_index < 0:
            return None
        tab_text = self.notebook.tabs[selected_index].text
        return next((file for file in self.parsers if f"解析结果 - {os.path.basename(file)}" == tab_text), None)

    def update_status(self, message: str):
        self.status_bar.value = message
        self.page.update()

    def get_length_entry(self) -> int:
        try:
            return int(self.length_entry.value)
        except ValueError:
            raise ValueError("请输入有效的数字")

    def get_regex_entry(self) -> str:
        return self.regex_entry.value

    def is_remove_header_checked(self) -> bool:
        return self.remove_header_checkbox.value

    def set_progress(self, value: int, maximum: int):
        self.progress.value = value / maximum if maximum > 0 else 0
        self.page.update()

    def get_progress_value(self) -> int:
        return int(self.progress.value * 100) if self.progress.value else 0

    def ask_save_file(self) -> str:
        # Flet不支持直接弹出文件对话框，需要通过网页功能实现
        # 这里简化处理，实际应使用file_picker
        return "output.jmx"

    def ask_save_directory(self) -> str:
        # 同上，简化处理
        return "."

    def show_info(self, message: str):
        self.page.dialog = ft.AlertDialog(title=ft.Text("提示"), content=ft.Text(message))
        self.page.dialog.open = True
        self.page.update()

    def add_replacement_frame(self):
        entry1 = ft.TextField(hint_text="被替换内容", expand=True)
        entry2 = ft.TextField(hint_text="替换内容", expand=True)
        frame = ft.Row([
            entry1,
            entry2
        ], spacing=10)
        self.replacement_container.controls.append(frame)
        self.replacement_frames.append((frame, entry1, entry2))
        self.page.update()

    def remove_replacement_frame(self):
        if self.replacement_frames:
            frame, _, _ = self.replacement_frames.pop()
            self.replacement_container.controls.remove(frame)
            self.page.update()

    def parse_jmx(self, e):
        super().parse_jmx()

    def save_jmx(self, e):
        if not self.parsers:
            self.show_error("请先解析一个 JMX 文件")
            return

        selected_tab = self.notebook.selected_index
        if selected_tab < 0:
            self.show_error("请选择要保存的文件")
            return

        tab_text = self.notebook.tabs[selected_tab].text
        jmx_file = next((file for file, parser in self.parsers.items() if f"解析结果 - {os.path.basename(file)}" == tab_text), None)
        
        if not jmx_file:
            self.show_error("无法确定要保存的 JMX 文件")
            return

        # 简化保存逻辑
        output_file = "output.jmx"
        parser = self.parsers[jmx_file]
        success = parser.save_jmx(output_file)
        if success:
            self.show_info(f"JMX 文件已保存到 {output_file}")
        else:
            self.show_error("保存 JMX 文件时出错")

    def save_all_jmx(self, e):
        if not self.parsers:
            self.show_error("请先解析一个 JMX 文件")
            return

        output_dir = "."  # 实际应使用文件选择器
        total_files = len(self.parsers)
        self.progress.value = 0
        self.progress.max = total_files
        
        for i, (jmx_file, parser) in enumerate(self.parsers.items()):
            try:
                output_file = os.path.join(output_dir, os.path.basename(jmx_file))
                success = parser.save_jmx(output_file)
                if success:
                    self.progress.value += 1
                    self.page.update()
                else:
                    self.show_error(f"保存 {jmx_file} 时出错")
            except Exception as e:
                self.show_error(f"保存 {jmx_file} 时出错: {e}")
        
        self.show_info(f"所有 JMX 文件已保存到 {output_dir}")

    def browse_file(self, e):
        # 简化文件选择
        self.set_file_path("selected_file.jmx")

    def browse_folder(self, e):
        self.set_file_path("selected_folder")