from nicegui import ui
import os
from .base_app import BaseApp
import logging

# 在__init__方法中初始化日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='app.log'
)

class App(BaseApp):
    def __init__(self):
        BaseApp.__init__(self)
        self.ui = ui
        
        # 状态栏
        self.status_bar = ui.label('就绪').classes('text-sm').style('width: 100%')
        with ui.row().classes('w-full justify-between items-center bg-surface-variant rounded-lg p-2 mt-2'):
            ui.label('状态:').classes('text-sm font-medium')
            self.status_bar

        # 文件选择区域
        with ui.row().classes('w-full items-center gap-4 py-4'):
            ui.label('选择 JMX 文件或文件夹:').classes('w-40 text-sm font-medium')
            self.file_path = ui.input().classes('flex-grow').props('readonly')
            self.browse_file_button = ui.button('选择文件', on_click=self.browse_file).classes('ml-2')
            self.browse_folder_button = ui.button('选择文件夹', on_click=self.browse_folder).classes('ml-2')

        # 参数输入区域
        with ui.row().classes('w-full items-center gap-4 py-4'):
            ui.label('输入字母组合长度:').classes('w-40 text-sm font-medium')
            self.length_entry = ui.input(value='2').classes('w-20')
            ui.label('输入正则表达式:').classes('w-40 text-sm font-medium')
            self.regex_entry = ui.input(value=r'http://\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}').classes('flex-grow')

        # 复选框
        with ui.row().classes('w-full items-center gap-4 py-4'):
            self.remove_header_checkbox = ui.checkbox('是否移除请求的Header')

        # 按钮区域
        with ui.row().classes('w-full gap-4 py-4'):
            ui.button('增加替换项', on_click=self.add_replacement_frame).classes('ml-2')
            ui.button('删除替换项', on_click=self.remove_replacement_frame).classes('ml-2')
            ui.button('解析 JMX', on_click=self.parse_jmx).classes('ml-2')
            ui.button('保存 JMX', on_click=self.save_jmx).classes('ml-2')
            ui.button('批量保存 JMX', on_click=self.save_all_jmx).classes('ml-2')

        # 替换项容器
        self.replacement_container = ui.column().classes('w-full gap-4')
        
        # 进度条
        with ui.row().classes('w-full items-center gap-4 py-4'):
            ui.label('进度:').classes('w-20 text-sm font-medium')
            self.progress = ui.linear_progress(value=0).classes('flex-grow')

        # Notebook（使用Tab组件）
        self.notebook = ui.tabs().classes('w-full')
        self.notebook_content = ui.tab_panels().classes('w-full')
        
        # 初始化替换项
        self.replacement_frames = []
        self.add_replacement_frame()

    def set_file_path(self, path: str):
        self.file_path.set_value(path)

    def show_error(self, message: str):
        ui.notify(message, type='error')

    def get_replacement_entries(self) -> list[tuple[str, str]]:
        return [(entry1.value, entry2.value) for _, entry1, entry2 in self.replacement_frames]

    def add_tab(self, title: str, content: str):
        with self.notebook_content:
            with ui.tab_panel(title):
                ui.markdown(content).classes('w-full')
        self.notebook.update()

    def clear_tabs(self):
        self.notebook_content.clear()
        self.notebook.update()

    def get_selected_file(self) -> str:
        # NiceGUI暂不支持直接获取选中标签页
        return next(iter(self.parsers), None) if self.parsers else None

    def update_status(self, message: str):
        self.status_bar.set_text(message)

    def get_length_entry(self) -> int:
        try:
            return int(self.length_entry.value)
        except ValueError:
            raise ValueError('请输入有效的数字')

    def get_regex_entry(self) -> str:
        return self.regex_entry.value

    def is_remove_header_checked(self) -> bool:
        return self.remove_header_checkbox.value

    def set_progress(self, value: int, maximum: int):
        self.progress.set_value(value / maximum if maximum > 0 else 0)

    def get_progress_value(self) -> int:
        return int(self.progress.value * 100) if self.progress.value else 0

    def ask_save_file(self) -> str:
        # NiceGUI暂不支持原生文件对话框
        return 'output.jmx'

    def ask_save_directory(self) -> str:
        return '.'

    def show_info(self, message: str):
        ui.notify(message)

    def add_replacement_frame(self):
        with self.replacement_container:
            # 创建行容器并保存引用
            row = ui.row().classes('w-full gap-4')
            with row:
                entry1 = ui.input(placeholder='被替换内容').classes('flex-grow')
                entry2 = ui.input(placeholder='替换内容').classes('flex-grow')
                # 保存行容器和输入框的引用
                self.replacement_frames.append((row, entry1, entry2))

    def remove_replacement_frame(self):
        if self.replacement_frames:
            frame, entry1, entry2 = self.replacement_frames.pop()
            frame.delete()

    def parse_jmx(self):
        super().parse_jmx()

    def save_jmx(self):
        if not self.parsers:
            self.show_error('请先解析一个 JMX 文件')
            return

        selected_tab = self.notebook.selected_index
        if selected_tab < 0:
            self.show_error('请选择要保存的文件')
            return

        jmx_file = next(iter(self.parsers))
        
        output_file = self.ask_save_file()
        if output_file:
            parser = self.parsers[jmx_file]
            success = parser.save_jmx(output_file)
            if success:
                self.show_info(f'JMX 文件已保存到 {output_file}')
            else:
                self.show_error('保存 JMX 文件时出错')

    def save_all_jmx(self):
        if not self.parsers:
            self.show_error('请先解析一个 JMX 文件')
            return

        output_dir = self.ask_save_directory()
        if not output_dir:
            return

        total_files = len(self.parsers)
        self.progress.set_value(0)
        
        for i, (jmx_file, parser) in enumerate(self.parsers.items()):
            try:
                output_file = os.path.join(output_dir, os.path.basename(jmx_file))
                success = parser.save_jmx(output_file)
                if success:
                    self.progress.set_value((i+1)/total_files)
                else:
                    self.show_error(f'保存 {jmx_file} 时出错')
            except Exception as e:
                self.show_error(f'保存 {jmx_file} 时出错: {e}')
        
        self.show_info(f'所有 JMX 文件已保存到 {output_dir}')

    def browse_file(self):
        # 创建文件选择对话框
        with ui.dialog() as dialog, ui.card():
            ui.label('选择 JMX 文件')
            file_picker = ui.file_picker('*.jmx', multiple=False)
            result = [None]
            
            def handle_upload(file):
                result[0] = file.name
                dialog.close()
            
            ui.upload(on_upload=handle_upload).props('accept=.jmx')
            
        if result[0]:
            self.file_path.set_value(result[0])
            self.update_status(f'已选择文件: {result[0]}')

    def browse_folder(self):
        # 创建文件夹选择对话框（通过选择任意文件触发）
        with ui.dialog() as dialog, ui.card():
            ui.label('选择包含JMX文件的文件夹')
            folder_picker = ui.file_picker('*', directory=True, multiple=False)
            result = [None]
            
            def handle_upload(folder):
                result[0] = folder.name
                dialog.close()
            
            ui.upload(on_upload=handle_upload).props('directory webkitdirectory')
            
        if result[0]:
            self.file_path.set_value(result[0])
            self.update_status(f'已选择文件夹: {result[0]}')
