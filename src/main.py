import sys
import os
from pathlib import Path
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                                QHBoxLayout, QPushButton, QLineEdit, QFileDialog,
                                QTreeWidget, QTreeWidgetItem, QSplitter, QLabel, 
                                QStatusBar, QStackedWidget, QTextEdit, QProgressBar)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QIcon

WHITELIST_EXTENSIONS = {'.pdf', '.docx', '.xlsx', '.pptx', '.txt', '.md'}


class TreeLoaderWorker(QThread):
    data_ready = Signal(list)
    
    def __init__(self, root_path, whitelist_extensions):
        super().__init__()
        self.root_path = root_path
        self.whitelist_extensions = whitelist_extensions
        self._is_running = True
    
    def run(self):
        try:
            data = self.scan_directory(Path(self.root_path))
            if self._is_running:
                self.data_ready.emit(data)
        except Exception as e:
            print(f"Error in TreeLoaderWorker: {e}")
            if self._is_running:
                self.data_ready.emit([])
    
    def scan_directory(self, path):
        items = []
        
        try:
            for item in sorted(path.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower())):
                if not self._is_running:
                    return items
                
                if item.is_file():
                    if item.suffix.lower() in self.whitelist_extensions:
                        try:
                            size = item.stat().st_size
                            items.append({
                                'name': item.name,
                                'type': 'file',
                                'path': str(item),
                                'extension': item.suffix.upper(),
                                'size': size
                            })
                        except:
                            pass
                
                elif item.is_dir():
                    if self.has_valid_files(item):
                        children = self.scan_directory(item)
                        if children or self.has_valid_files(item):
                            items.append({
                                'name': item.name,
                                'type': 'dir',
                                'path': str(item),
                                'children': children
                            })
        except Exception as e:
            pass
        
        return items
    
    def has_valid_files(self, folder_path):
        try:
            for root, dirs, files in os.walk(folder_path):
                if not self._is_running:
                    return False
                for file in files:
                    file_path = Path(root) / file
                    if file_path.suffix.lower() in self.whitelist_extensions:
                        return True
            return False
        except Exception as e:
            return False
    
    def stop(self):
        self._is_running = False


class FileCounterThread(QThread):
    count_finished = Signal(int, int)
    
    def __init__(self, folder_path, whitelist_extensions):
        super().__init__()
        self.folder_path = folder_path
        self.whitelist_extensions = whitelist_extensions
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
                    if item.suffix.lower() in self.whitelist_extensions:
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
        self.loader_worker = None
        
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
        
        self.loading_widget = QWidget()
        loading_layout = QVBoxLayout(self.loading_widget)
        loading_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        loading_label = QLabel("正在扫描文件...")
        loading_label.setStyleSheet("font-size: 16px; color: #666;")
        loading_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.loading_progress = QProgressBar()
        self.loading_progress.setRange(0, 0)
        self.loading_progress.setMaximumWidth(300)
        loading_layout.addWidget(loading_label)
        loading_layout.addWidget(self.loading_progress)
        self.loading_widget.hide()
        
        self.file_tree = QTreeWidget()
        self.file_tree.setHeaderLabels(["名称", "类型", "大小"])
        self.file_tree.setColumnWidth(0, 300)
        self.file_tree.setColumnWidth(1, 100)
        
        active_layout.addWidget(self.loading_widget)
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
        self.instruction_input.setText("类型 >> 年份")
        self.instruction_input.setPlaceholderText("在此输入指令...")
        self.instruction_input.setToolTip("使用 '>>' 创建子文件夹。示例: 类型 >> 年份 >> 月份")
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
        
        self.file_tree.clear()
        self.file_tree.hide()
        self.loading_widget.show()
        
        if self.loader_worker and self.loader_worker.isRunning():
            self.loader_worker.stop()
            self.loader_worker.wait()
        
        self.loader_worker = TreeLoaderWorker(folder_path, WHITELIST_EXTENSIONS)
        self.loader_worker.data_ready.connect(self.on_scan_finished)
        self.loader_worker.start()
        
        self.start_counting(folder_path)
    
    def on_scan_finished(self, data):
        self.loading_widget.hide()
        self.file_tree.show()
        
        style = self.style()
        folder_icon = style.standardIcon(style.StandardPixmap.SP_DirIcon)
        file_icon = style.standardIcon(style.StandardPixmap.SP_FileIcon)
        
        self.populate_tree_from_data(data, self.file_tree, folder_icon, file_icon)
    
    def populate_tree_from_data(self, data, parent, folder_icon, file_icon):
        for item_data in data:
            if item_data['type'] == 'file':
                tree_item = QTreeWidgetItem(parent)
                tree_item.setText(0, item_data['name'])
                tree_item.setText(1, item_data['extension'])
                
                size = item_data['size']
                if size < 1024:
                    size_str = f"{size} B"
                elif size < 1024 * 1024:
                    size_str = f"{size / 1024:.1f} KB"
                else:
                    size_str = f"{size / (1024 * 1024):.1f} MB"
                tree_item.setText(2, size_str)
                
                tree_item.setIcon(0, file_icon)
                tree_item.setData(0, Qt.ItemDataRole.UserRole, item_data['path'])
            
            elif item_data['type'] == 'dir':
                tree_item = QTreeWidgetItem(parent)
                tree_item.setText(0, item_data['name'])
                tree_item.setText(1, "文件夹")
                tree_item.setText(2, "")
                tree_item.setIcon(0, folder_icon)
                tree_item.setData(0, Qt.ItemDataRole.UserRole, item_data['path'])
                
                if 'children' in item_data and item_data['children']:
                    self.populate_tree_from_data(item_data['children'], tree_item, folder_icon, file_icon)
    
    def start_counting(self, folder_path):
        if self.counter_thread and self.counter_thread.isRunning():
            self.counter_thread.stop()
            self.counter_thread.wait()
        
        self.status_label.setText("正在扫描...")
        
        self.counter_thread = FileCounterThread(folder_path, WHITELIST_EXTENSIONS)
        self.counter_thread.count_finished.connect(self.update_count)
        self.counter_thread.start()
    
    def update_count(self, folder_count, file_count):
        self.status_label.setText(f"扫描完成: {folder_count} 个文件夹, {file_count} 个支持的文件")
    
    def closeEvent(self, event):
        if self.loader_worker and self.loader_worker.isRunning():
            self.loader_worker.stop()
            self.loader_worker.wait()
        
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