import sys
import os
from pathlib import Path
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                                QHBoxLayout, QPushButton, QLineEdit, QFileDialog,
                                QTreeView, QSplitter, QLabel, QStatusBar, QStackedWidget,
                                QFileSystemModel, QTextEdit)
from PySide6.QtCore import Qt, QThread, Signal


class FileCounterThread(QThread):
    count_finished = Signal(int, int)
    
    def __init__(self, folder_path):
        super().__init__()
        self.folder_path = folder_path
        self._is_running = True
    
    def run(self):
        folder_count = 0
        file_count = 0
        
        try:
            path = Path(self.folder_path)
            for item in path.rglob('*'):
                if not self._is_running:
                    return
                if item.is_dir():
                    folder_count += 1
                elif item.is_file():
                    file_count += 1
        except Exception as e:
            pass
        
        if self._is_running:
            self.count_finished.emit(folder_count, file_count)
    
    def stop(self):
        self._is_running = False


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("FileClassify")
        self.setMinimumSize(1024, 800)
        
        self.current_folder = None
        self.counter_thread = None
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(splitter)
        
        left_panel = self.create_left_panel()
        right_panel = self.create_right_panel()
        
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setStretchFactor(0, 2)
        splitter.setStretchFactor(1, 3)
        
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_label = QLabel("文件夹: 0  文件: 0")
        self.status_bar.addWidget(self.status_label)
    
    def create_left_panel(self):
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(0)
        
        header_widget = QWidget()
        header_widget.setMinimumHeight(60)
        header_widget.setStyleSheet("background-color: #f5f5f5; padding: 10px;")
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(10, 10, 10, 10)
        header_layout.setSpacing(10)
        
        self.folder_path_input = QLineEdit()
        self.folder_path_input.setPlaceholderText("选择文件夹路径...")
        self.folder_path_input.setReadOnly(True)
        self.folder_path_input.setMinimumHeight(35)
        
        self.select_folder_btn = QPushButton("选择文件夹")
        self.select_folder_btn.setMinimumHeight(35)
        self.select_folder_btn.setMinimumWidth(100)
        self.select_folder_btn.clicked.connect(self.select_folder)
        
        header_layout.addWidget(self.folder_path_input, 1)
        header_layout.addWidget(self.select_folder_btn)
        
        left_layout.addWidget(header_widget)
        
        self.content_stack = QStackedWidget()
        
        empty_state_widget = QWidget()
        empty_layout = QVBoxLayout(empty_state_widget)
        empty_label = QLabel("请选择文件夹")
        empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        empty_label.setStyleSheet("font-size: 24px; color: #999;")
        empty_layout.addWidget(empty_label)
        
        active_state_widget = QWidget()
        active_layout = QVBoxLayout(active_state_widget)
        active_layout.setContentsMargins(0, 0, 0, 0)
        
        self.file_tree = QTreeView()
        self.file_model = QFileSystemModel()
        self.file_model.setRootPath("")
        self.file_tree.setModel(self.file_model)
        self.file_tree.setColumnWidth(0, 250)
        
        active_layout.addWidget(self.file_tree)
        
        self.content_stack.addWidget(empty_state_widget)
        self.content_stack.addWidget(active_state_widget)
        self.content_stack.setCurrentIndex(0)
        
        left_layout.addWidget(self.content_stack, 1)
        
        return left_widget
    
    def create_right_panel(self):
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(10, 10, 10, 10)
        right_layout.setSpacing(15)
        
        row1_layout = QHBoxLayout()
        row1_label = QLabel("目标文件夹:")
        self.target_folder_input = QLineEdit()
        self.target_folder_input.setPlaceholderText("选择目标文件夹...")
        self.target_folder_input.setReadOnly(True)
        self.target_folder_input.setMinimumHeight(30)
        
        self.select_target_btn = QPushButton("选择...")
        self.select_target_btn.setMinimumHeight(30)
        self.select_target_btn.setMinimumWidth(80)
        self.select_target_btn.clicked.connect(self.select_target_folder)
        
        row1_layout.addWidget(row1_label)
        row1_layout.addWidget(self.target_folder_input, 1)
        row1_layout.addWidget(self.select_target_btn)
        
        row2_layout = QHBoxLayout()
        self.instruction_input = QLineEdit()
        self.instruction_input.setPlaceholderText("在此输入指令...")
        self.instruction_input.setMinimumHeight(30)
        
        self.start_convert_btn = QPushButton("开始转换")
        self.start_convert_btn.setMinimumHeight(30)
        self.start_convert_btn.setMinimumWidth(100)
        self.start_convert_btn.clicked.connect(self.start_convert)
        
        row2_layout.addWidget(self.instruction_input, 1)
        row2_layout.addWidget(self.start_convert_btn)
        
        self.preview_area = QTextEdit()
        self.preview_area.setReadOnly(True)
        self.preview_area.setPlaceholderText("文件移动建议将显示在此处...")
        
        right_layout.addLayout(row1_layout)
        right_layout.addLayout(row2_layout)
        right_layout.addWidget(self.preview_area, 1)
        
        return right_widget
    
    def select_target_folder(self):
        folder_path = QFileDialog.getExistingDirectory(
            self,
            "选择目标文件夹",
            "",
            QFileDialog.Option.ShowDirsOnly
        )
        
        if folder_path:
            self.target_folder_input.setText(folder_path)
    
    def start_convert(self):
        print("Start clicked")
    
    def select_folder(self):
        folder_path = QFileDialog.getExistingDirectory(
            self,
            "选择文件夹",
            self.current_folder if self.current_folder else "",
            QFileDialog.Option.ShowDirsOnly
        )
        
        if folder_path:
            self.load_folder(folder_path)
    
    def load_folder(self, folder_path):
        self.current_folder = folder_path
        self.folder_path_input.setText(folder_path)
        
        self.content_stack.setCurrentIndex(1)
        
        index = self.file_model.setRootPath(folder_path)
        self.file_tree.setRootIndex(index)
        
        self.start_counting(folder_path)
    
    def start_counting(self, folder_path):
        if self.counter_thread and self.counter_thread.isRunning():
            self.counter_thread.stop()
            self.counter_thread.wait()
        
        self.status_label.setText("正在统计...")
        
        self.counter_thread = FileCounterThread(folder_path)
        self.counter_thread.count_finished.connect(self.update_count)
        self.counter_thread.start()
    
    def update_count(self, folder_count, file_count):
        self.status_label.setText(f"文件夹: {folder_count}  文件: {file_count}")
    
    def closeEvent(self, event):
        if self.counter_thread and self.counter_thread.isRunning():
            self.counter_thread.stop()
            self.counter_thread.wait()
        event.accept()


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()