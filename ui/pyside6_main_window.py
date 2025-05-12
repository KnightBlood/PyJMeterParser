import os

import pywinstyles
from PySide6.QtGui import Qt
from PySide6.QtWidgets import (QWidget, QMainWindow, QVBoxLayout, QPushButton, QLineEdit, QFileDialog, QApplication,
                               QTextEdit,
                               QTabWidget, QProgressBar, QLabel, QFrame, QHBoxLayout, QCheckBox, QFormLayout,
                               QMessageBox, QSizePolicy)

from ui.base_app import BaseApp


class App(BaseApp, QMainWindow):
    def __init__(self, master=None):
        QMainWindow.__init__(self, master)
        BaseApp.__init__(self)
        self.parsers = {}
        self.setWindowTitle("JMeter JMX Parser")
        self.setGeometry(100, 100, 800, 600)
        
        # 使用py-window-styles统一美化
        pywinstyles.apply_style(self, "mica")

        # 主框架
        main_frame = QWidget()
        self.setCentralWidget(main_frame)
        
        # 初始化状态栏
        self.statusBar().showMessage("就绪")

        # 创建主布局
        main_layout = QVBoxLayout(main_frame)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # 文件路径输入框
        file_frame = QFrame()
        file_layout = QHBoxLayout(file_frame)
        file_layout.setSpacing(10)
        file_layout.setContentsMargins(0, 0, 0, 0)
        
        self.label = QLabel("选择 JMX 文件或文件夹:")
        self.label.setFixedWidth(150)
        file_layout.addWidget(self.label)
        
        self.file_path = QLineEdit()
        file_layout.addWidget(self.file_path, 1)
        
        self.browse_file_button = QPushButton("选择文件")
        self.browse_file_button.setFixedWidth(100)
        self.browse_file_button.clicked.connect(self.browse_file)
        file_layout.addWidget(self.browse_file_button)
        
        self.browse_folder_button = QPushButton("选择文件夹")
        self.browse_folder_button.setFixedWidth(100)
        self.browse_folder_button.clicked.connect(self.browse_folder)
        file_layout.addWidget(self.browse_folder_button)
        
        main_layout.addWidget(file_frame)
        
        # 参数输入区域
        param_frame = QFrame()
        param_layout = QHBoxLayout(param_frame)
        param_layout.setSpacing(20)
        param_layout.setContentsMargins(0, 0, 0, 0)
        
        # 字母组合长度输入框
        length_frame = QFrame()
        length_layout = QFormLayout(length_frame)
        length_layout.setSpacing(10)
        
        self.length_label = QLabel("输入字母组合长度:")
        self.length_label.setFixedWidth(150)
        length_input = QWidget()
        length_input_layout = QHBoxLayout(length_input)
        length_input_layout.setContentsMargins(0, 0, 0, 0)
        
        self.length_entry = QLineEdit("2")
        self.length_entry.setFixedWidth(50)
        length_input_layout.addWidget(self.length_entry)
        
        length_layout.addRow(self.length_label, length_input)
        
        # 正则表达式输入框
        regex_frame = QFrame()
        regex_layout = QFormLayout(regex_frame)
        regex_layout.setSpacing(10)
        
        self.regex_label = QLabel("输入正则表达式:")
        self.regex_label.setFixedWidth(150)
        regex_input = QWidget()
        regex_input_layout = QHBoxLayout(regex_input)
        regex_input_layout.setContentsMargins(0, 0, 0, 0)
        
        self.regex_entry = QLineEdit(r"http://\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}")
        regex_input_layout.addWidget(self.regex_entry, 1)  # 1表示可扩展
        
        regex_layout.addRow(self.regex_label, regex_input)
        
        # 将参数框架添加到主布局
        param_layout.addWidget(length_frame, 1)
        param_layout.addWidget(regex_frame, 2)  # 2表示占两倍宽度
        main_layout.addWidget(param_frame)
        
        # 复选框
        self.remove_header_var = QCheckBox("是否移除请求的Header")
        self.remove_header_var.setFixedWidth(200)
        main_layout.addWidget(self.remove_header_var)

        # 按钮框架
        button_frame = QFrame()
        button_layout = QHBoxLayout(button_frame)
        button_layout.setSpacing(10)
        button_layout.setContentsMargins(0, 0, 0, 0)
        
        self.add_replacement_button = QPushButton("增加替换项")
        self.add_replacement_button.setFixedWidth(100)
        self.add_replacement_button.clicked.connect(self.add_replacement_frame)
        button_layout.addWidget(self.add_replacement_button)
        
        self.remove_replacement_button = QPushButton("删除替换项")
        self.remove_replacement_button.setFixedWidth(100)
        self.remove_replacement_button.clicked.connect(self.remove_replacement_frame)
        button_layout.addWidget(self.remove_replacement_button)
        
        self.parse_button = QPushButton("解析 JMX")
        self.parse_button.setFixedWidth(100)
        self.parse_button.clicked.connect(self.parse_jmx)
        button_layout.addWidget(self.parse_button)
        
        self.save_button = QPushButton("保存 JMX")
        self.save_button.setFixedWidth(100)
        self.save_button.clicked.connect(self.save_jmx)
        button_layout.addWidget(self.save_button)
        
        self.save_all_button = QPushButton("批量保存 JMX")
        self.save_all_button.setFixedWidth(100)
        self.save_all_button.clicked.connect(self.save_all_jmx)
        button_layout.addWidget(self.save_all_button)
        
        main_layout.addWidget(button_frame)
        
        # Notebook组件
        self.notebook = QTabWidget()
        main_layout.addWidget(self.notebook)

        # 进度条
        self.progress = QProgressBar()
        self.progress.setFixedHeight(20)
        self.progress.setTextVisible(True)
        self.progress.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.progress)

        # 替换内容输入框
        self.replacement_frames = []
        self.add_replacement_frame()

    def get_file_path(self) -> str:
        return self.file_path.text()

    def set_file_path(self, path: str):
        self.file_path.setText(path)

    def show_error(self, message: str):
        QMessageBox.critical(self, "错误", message)

    def get_replacement_entries(self) -> list[tuple[str, str]]:
        return [(entry1.text(), entry2.text()) for _, entry1, entry2 in self.replacement_frames]

    def clear_tabs(self):
        self.notebook.clear()

    def add_tab(self, title: str, content: str):
        new_tab = QWidget()
        layout = QVBoxLayout(new_tab)
        text_edit = QTextEdit()
        text_edit.setPlainText(content)
        layout.addWidget(text_edit)
        self.notebook.addTab(new_tab, title)

    def get_selected_file(self) -> str:
        tab_text = self.notebook.tabText(self.notebook.currentIndex())
        return next((file for file in self.parsers if f"解析结果 - {os.path.basename(file)}" == tab_text), None)

    def update_status(self, message: str):
        self.statusBar().showMessage(message)

    def get_length_entry(self) -> int:
        return int(self.length_entry.text())

    def get_regex_entry(self) -> str:
        return self.regex_entry.text()

    def is_remove_header_checked(self) -> bool:
        return self.remove_header_var.isChecked()

    def set_progress(self, value: int, maximum: int):
        self.progress.setMaximum(maximum)
        self.progress.setValue(value)

    def get_progress_value(self) -> int:
        return self.progress.value()

    def ask_save_file(self) -> str:
        file_path, _ = QFileDialog.getSaveFileName(self, "保存 JMX 文件", "", "JMX files (*.jmx)")
        return file_path

    def ask_save_directory(self) -> str:
        folder_path = QFileDialog.getExistingDirectory(self, "选择输出文件夹")
        return folder_path

    def show_info(self, message: str):
        QMessageBox.information(self, "提示", message)

    def add_replacement_frame(self):
        frame = QFrame()
        frame.setObjectName("replacement_frame")
        layout = QHBoxLayout(frame)
        layout.setSpacing(10)
        layout.setContentsMargins(0, 0, 0, 0)
        
        label1 = QLabel("被替换内容:")
        label1.setFixedWidth(100)
        layout.addWidget(label1)
        
        entry1 = QLineEdit()
        entry1.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        layout.addWidget(entry1)
        
        label2 = QLabel("替换内容:")
        label2.setFixedWidth(100)
        layout.addWidget(label2)
        
        entry2 = QLineEdit()
        entry2.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        layout.addWidget(entry2)
        
        self.replacement_frames.append((frame, entry1, entry2))
        
        # 将框架添加到主布局
        self.centralWidget().layout().addWidget(frame)

    def remove_replacement_frame(self):
        if self.replacement_frames:
            frame, _, _ = self.replacement_frames.pop()
            frame.setParent(None)
            frame.deleteLater()
        
    def browse_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "选择 JMX 文件", "", "JMX files (*.jmx)")
        if file_path:
            self.file_path.setText(file_path)
        
    def browse_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, "选择文件夹")
        if folder_path:
            self.file_path.setText(folder_path)
        
    def parse_jmx(self):
        super().parse_jmx()

    def parse_single_file(self, jmx_file, length, remove_header, pattern):
        super().parse_single_file(jmx_file, length, remove_header, pattern)
        
    def parse_directory(self, directory, length, remove_header, pattern):
        jmx_files = [os.path.join(directory, f) for f in os.listdir(directory) if f.endswith('.jmx')]
        total_files = len(jmx_files)
        self.progress.setMaximum(total_files)
        self.progress.setValue(0)
        
        for file in jmx_files:
            try:
                self.parse_single_file(file, length, remove_header, pattern)
                self.progress.setValue(self.progress.value() + 1)
                QApplication.processEvents()
            except Exception as e:
                QMessageBox.critical(self, "错误", f"处理 {file} 时出错: {e}")
        
        QMessageBox.information(self, "完成", "所有文件解析完成")
        
    def save_jmx(self):
        if not self.parsers:
            QMessageBox.critical(self, "错误", "请先解析一个 JMX 文件")
            return
        
        selected_index = self.notebook.currentIndex()
        if selected_index == -1:
            QMessageBox.critical(self, "错误", "请选择一个标签页")
            return
        
        tab_text = self.notebook.tabText(selected_index)
        jmx_file = next((file for file, parser in self.parsers.items() if f"解析结果 - {os.path.basename(file)}" == tab_text), None)
        
        if not jmx_file:
            QMessageBox.critical(self, "错误", "无法确定要保存的 JMX 文件")
            return
        
        output_file, _ = QFileDialog.getSaveFileName(self, "保存 JMX 文件", "", "JMX files (*.jmx)")
        if output_file:
            parser = self.parsers[jmx_file]
            success = parser.save_jmx(output_file)
            if success:
                QMessageBox.information(self, "成功", f"JMX 文件已保存到 {output_file}")
            else:
                QMessageBox.critical(self, "错误", "保存 JMX 文件时出错")
        
    def save_all_jmx(self):
        if not self.parsers:
            QMessageBox.critical(self, "错误", "请先解析一个 JMX 文件")
            return
        
        output_dir = QFileDialog.getExistingDirectory(self, "选择输出文件夹")
        if not output_dir:
            return
        
        total_files = len(self.parsers)
        self.progress.setMaximum(total_files)
        self.progress.setValue(0)
        
        for jmx_file, parser in self.parsers.items():
            try:
                output_file = os.path.join(output_dir, os.path.basename(jmx_file))
                success = parser.save_jmx(output_file)
                if success:
                    self.progress.setValue(self.progress.value() + 1)
                    QApplication.processEvents()
                else:
                    QMessageBox.critical(self, "错误", f"保存 {jmx_file} 时出错")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"保存 {jmx_file} 时出错: {e}")
        
        QMessageBox.information(self, "成功", f"所有 JMX 文件已保存到 {output_dir}")