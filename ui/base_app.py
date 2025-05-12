import os

from business.parser import JMeterParser


class BaseApp:
    def __init__(self):
        self.parsers = {}
        self.replacement_frames = []

    def get_file_path(self) -> str:
        raise NotImplementedError("get_file_path must be implemented in subclass")

    def set_file_path(self, path: str):
        raise NotImplementedError("set_file_path must be implemented in subclass")

    def show_error(self, message: str):
        raise NotImplementedError("show_error must be implemented in subclass")

    def get_replacement_entries(self) -> list[tuple[str, str]]:
        raise NotImplementedError("get_replacement_entries must be implemented in subclass")

    def clear_tabs(self):
        raise NotImplementedError("clear_tabs must be implemented in subclass")

    def add_tab(self, title: str, content: str):
        raise NotImplementedError("add_tab must be implemented in subclass")

    def get_selected_file(self) -> str:
        raise NotImplementedError("get_selected_file must be implemented in subclass")

    def update_status(self, message: str):
        raise NotImplementedError("update_status must be implemented in subclass")

    def get_length_entry(self) -> int:
        raise NotImplementedError("get_length_entry must be implemented in subclass")

    def get_regex_entry(self) -> str:
        raise NotImplementedError("get_regex_entry must be implemented in subclass")

    def is_remove_header_checked(self) -> bool:
        raise NotImplementedError("is_remove_header_checked must be implemented in subclass")

    def set_progress(self, value: int, maximum: int):
        raise NotImplementedError("set_progress must be implemented in subclass")

    def parse_jmx(self):
        path = self.get_file_path()
        length_str = self.get_length_entry()
        if not path:
            self.show_error("请先选择一个 JMX 文件或文件夹")
            return

        try:
            length = int(length_str)
            if length < 1:
                raise ValueError
        except ValueError:
            self.show_error("请输入有效的字母组合长度（大于0的整数）")
            return

        pattern = self.get_regex_entry()
        remove_header = self.is_remove_header_checked()

        self.clear_tabs()
        self.parsers.clear()

        try:
            if os.path.isdir(path):
                self.parse_directory(path, length, remove_header, pattern)
            else:
                self.parse_single_file(path, length, remove_header, pattern)
        except Exception as e:
            self.show_error(f"解析 JMX 时出错: {e}")

    def parse_single_file(self, jmx_file, length, remove_header, pattern):
        replacement_frames = self.get_replacement_entries()
        parser = JMeterParser(jmx_file, length, remove_header, pattern, replacement_frames)
        output = "\n".join(f"{element['type']} #{element['number']}: {element['formatted_name']}"
                           for element in parser.test_elements)
        
        file_name = os.path.basename(jmx_file)
        tab_name = f"解析结果 - {file_name}"
        self.add_tab(tab_name, output)
        self.parsers[jmx_file] = parser

    def parse_directory(self, directory, length, remove_header, pattern):
        jmx_files = [os.path.join(directory, f) for f in os.listdir(directory) if f.endswith('.jmx')]
        total_files = len(jmx_files)
        self.set_progress(0, total_files)

        for file in jmx_files:
            try:
                self.parse_single_file(file, length, remove_header, pattern)
                self.set_progress(self.get_progress_value() + 1, total_files)
            except Exception as e:
                self.show_error(f"处理 {file} 时出错: {e}")

    def save_jmx(self):
        if not self.parsers:
            self.show_error("请先解析一个 JMX 文件")
            return

        selected_file = self.get_selected_file()
        if not selected_file:
            self.show_error("请选择一个标签页")
            return

        parser = self.parsers.get(selected_file)
        if not parser:
            self.show_error("无法确定要保存的 JMX 文件")
            return

        output_file = self.ask_save_file()
        if output_file:
            success = parser.save_jmx(output_file)
            if success:
                self.show_info(f"JMX 文件已保存到 {output_file}")
            else:
                self.show_error("保存 JMX 文件时出错")

    def save_all_jmx(self):
        if not self.parsers:
            self.show_error("请先解析一个 JMX 文件")
            return

        output_dir = self.ask_save_directory()
        if not output_dir:
            return

        total_files = len(self.parsers)
        self.set_progress(0, total_files)

        for jmx_file, parser in self.parsers.items():
            try:
                output_file = os.path.join(output_dir, os.path.basename(jmx_file))
                success = parser.save_jmx(output_file)
                if success:
                    self.set_progress(self.get_progress_value() + 1, total_files)
                else:
                    self.show_error(f"保存 {jmx_file} 时出错")
            except Exception as e:
                self.show_error(f"保存 {jmx_file} 时出错: {e}")

        self.show_info("所有 JMX 文件已保存")

    def add_replacement_frame(self):
        # 子类实现
        pass

    def remove_replacement_frame(self):
        # 子类实现
        pass

    def show_info(self, message: str):
        pass

    def get_progress_value(self) -> int:
        return 0

    def ask_save_file(self) -> str:
        return ""

    def ask_save_directory(self) -> str:
        return ""