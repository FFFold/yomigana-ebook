import sys
import os
from pathlib import Path
from typing import Optional, List
from io import BytesIO

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QTextEdit, QFileDialog, QCheckBox,
    QProgressBar, QMessageBox, QGroupBox
)
from PySide6.QtCore import Qt, QThread, Signal, QMimeData
from PySide6.QtGui import QDragEnterEvent, QDropEvent

from yomigana_ebook.process_ebook import process_ebook
from yomigana_ebook.checking import check_unidic_dictionary


class DictionaryManager:
    """词典管理器，负责检测和下载unidic词典"""
    
    @staticmethod
    def is_dictionary_installed() -> bool:
        """检测词典是否已安装"""
        try:
            return check_unidic_dictionary()
        except:
            return False
    
    @staticmethod
    def download_dictionary(parent=None) -> bool:
        """下载词典"""
        try:
            msg_box = QMessageBox(parent)
            msg_box.setWindowTitle("下载词典")
            msg_box.setText("未检测到unidic词典，需要下载吗？\n\n词典大小约500MB，可能需要几分钟时间。")
            msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            msg_box.setDefaultButton(QMessageBox.Yes)
            
            if msg_box.exec() == QMessageBox.Yes:
                from yomigana_ebook.checking import download_unidic_dictionary
                
                progress = QMessageBox(parent)
                progress.setWindowTitle("下载中")
                progress.setText("正在下载unidic词典，请稍候...")
                progress.setStandardButtons(QMessageBox.Cancel)
                progress.show()
                
                download_unidic_dictionary()
                
                progress.close()
                
                if DictionaryManager.is_dictionary_installed():
                    QMessageBox.information(parent, "成功", "词典下载完成！")
                    return True
                else:
                    QMessageBox.critical(parent, "失败", "词典下载失败，请检查网络连接或手动安装。")
                    return False
            return False
        except Exception as e:
            QMessageBox.critical(parent, "错误", f"下载词典时出错：{str(e)}")
            return False


class ConversionThread(QThread):
    """后台转换线程"""
    progress = Signal(str)
    finished = Signal(str)
    error = Signal(str)
    
    def __init__(self, input_path: str, output_path: str, filter_japanese: bool):
        super().__init__()
        self.input_path = input_path
        self.output_path = output_path
        self.filter_japanese = filter_japanese
    
    def run(self):
        try:
            self.progress.emit(f"开始处理: {os.path.basename(self.input_path)}")
            
            with open(self.input_path, "rb") as reader, open(self.output_path, "wb") as writer:
                process_ebook(reader, writer, self.filter_japanese)
            
            self.finished.emit(self.output_path)
        except Exception as e:
            self.error.emit(str(e))


class DragDropWidget(QLabel):
    """拖拽文件区域"""
    files_dropped = Signal(list)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAlignment(Qt.AlignCenter)
        self.setText("拖拽EPUB文件到此处\n或点击选择文件")
        self.setStyleSheet("""
            QLabel {
                border: 2px dashed #aaa;
                border-radius: 8px;
                padding: 40px;
                background-color: #f5f5f5;
                color: #666;
                font-size: 14px;
            }
            QLabel:hover {
                background-color: #e8e8e8;
                border-color: #999;
            }
        """)
        self.setAcceptDrops(True)
    
    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
    
    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
    
    def dropEvent(self, event: QDropEvent):
        files = []
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            if file_path.lower().endswith('.epub'):
                files.append(file_path)
        
        if files:
            self.files_dropped.emit(files)
        else:
            QMessageBox.warning(self, "提示", "请拖拽EPUB格式的文件")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Yomigana Ebook - EPUB日文注音工具")
        self.setMinimumSize(700, 600)
        
        # 检查词典
        self._check_dictionary()
        
        # 初始化UI
        self._init_ui()
        
        # 当前处理文件列表
        self.files_to_process: List[str] = []
        self.current_thread: Optional[ConversionThread] = None
    
    def _check_dictionary(self):
        """检查词典状态"""
        if not DictionaryManager.is_dictionary_installed():
            reply = QMessageBox.question(
                self,
                "词典未安装",
                "未检测到unidic日文字典。\n\n"
                "您可以选择：\n"
                "  - 立即下载（约500MB，需要几分钟）\n"
                "  - 稍后手动安装（运行: python -m unidic download）\n\n"
                "是否立即下载？",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes
            )
            
            if reply == QMessageBox.Yes:
                if not DictionaryManager.download_dictionary(self):
                    QMessageBox.warning(
                        self,
                        "警告",
                        "程序仍可启动，但无法处理EPUB文件。\n"
                        "请稍后运行: python -m unidic download"
                    )
    
    def _init_ui(self):
        """初始化用户界面"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # 标题
        title_label = QLabel("EPUB日文注音工具")
        title_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #333;")
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        
        # 文件选择区域
        file_group = QGroupBox("选择文件")
        file_layout = QVBoxLayout()
        
        self.file_drop_area = DragDropWidget()
        self.file_drop_area.files_dropped.connect(self._on_files_selected)
        file_layout.addWidget(self.file_drop_area)
        
        btn_layout = QHBoxLayout()
        self.select_btn = QPushButton("选择文件")
        self.select_btn.clicked.connect(self._select_files)
        self.clear_btn = QPushButton("清空列表")
        self.clear_btn.clicked.connect(self._clear_files)
        self.clear_btn.setEnabled(False)
        
        btn_layout.addWidget(self.select_btn)
        btn_layout.addWidget(self.clear_btn)
        file_layout.addLayout(btn_layout)
        
        self.file_label = QLabel("未选择文件")
        self.file_label.setStyleSheet("color: #666; font-size: 12px;")
        file_layout.addWidget(self.file_label)
        
        file_group.setLayout(file_layout)
        main_layout.addWidget(file_group)
        
        # 选项设置
        options_group = QGroupBox("转换选项")
        options_layout = QVBoxLayout()
        
        self.filter_checkbox = QCheckBox("过滤非日文段落（适用于中日文混合排版）")
        self.filter_checkbox.setToolTip("只对包含日文假名的段落添加注音，避免对中文段落添加日文读音")
        options_layout.addWidget(self.filter_checkbox)
        
        options_group.setLayout(options_layout)
        main_layout.addWidget(options_group)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        main_layout.addWidget(self.progress_bar)
        
        # 转换按钮
        self.convert_btn = QPushButton("开始转换")
        self.convert_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 12px;
                font-size: 14px;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:disabled {
                background-color: #ccc;
            }
        """)
        self.convert_btn.clicked.connect(self._start_conversion)
        self.convert_btn.setEnabled(False)
        main_layout.addWidget(self.convert_btn)
        
        # 日志输出
        log_group = QGroupBox("转换日志")
        log_layout = QVBoxLayout()
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(200)
        self.log_text.setStyleSheet("""
            QTextEdit {
                background-color: #f9f9f9;
                font-family: 'Courier New';
                font-size: 12px;
            }
        """)
        log_layout.addWidget(self.log_text)
        
        log_group.setLayout(log_layout)
        main_layout.addWidget(log_group)
        
        # 状态栏
        self.statusBar().showMessage("就绪")
    
    def _select_files(self):
        """选择文件对话框"""
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "选择EPUB文件",
            "",
            "EPUB Files (*.epub)"
        )
        
        if files:
            self._on_files_selected(files)
    
    def _on_files_selected(self, files: List[str]):
        """文件选择回调"""
        self.files_to_process = files
        self.file_label.setText(f"已选择 {len(files)} 个文件: {', '.join(os.path.basename(f) for f in files[:3])}{'...' if len(files) > 3 else ''}")
        self.clear_btn.setEnabled(True)
        self.convert_btn.setEnabled(True)
        self.log(f"已选择 {len(files)} 个文件")
    
    def _clear_files(self):
        """清空文件列表"""
        self.files_to_process = []
        self.file_label.setText("未选择文件")
        self.clear_btn.setEnabled(False)
        self.convert_btn.setEnabled(False)
        self.log("已清空文件列表")
    
    def _start_conversion(self):
        """开始转换"""
        if not self.files_to_process:
            QMessageBox.warning(self, "警告", "请先选择EPUB文件")
            return
        
        if not DictionaryManager.is_dictionary_installed():
            QMessageBox.critical(self, "错误", "未检测到unidic词典，请先下载或安装词典。")
            return
        
        self.convert_btn.setEnabled(False)
        self.select_btn.setEnabled(False)
        self.clear_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, len(self.files_to_process))
        self.progress_bar.setValue(0)
        
        self._process_next_file()
    
    def _process_next_file(self):
        """处理下一个文件"""
        if not self.files_to_process:
            self._conversion_complete()
            return
        
        input_path = self.files_to_process.pop(0)
        output_dir = os.path.dirname(input_path)
        base_name = os.path.basename(input_path)
        output_path = os.path.join(output_dir, f"with-yomigana_{base_name}")
        
        self.log(f"正在处理: {base_name}")
        self.statusBar().showMessage(f"处理中: {base_name}")
        
        self.current_thread = ConversionThread(
            input_path,
            output_path,
            self.filter_checkbox.isChecked()
        )
        self.current_thread.progress.connect(self.log)
        self.current_thread.finished.connect(self._on_file_finished)
        self.current_thread.error.connect(self._on_file_error)
        self.current_thread.start()
    
    def _on_file_finished(self, output_path: str):
        """单个文件处理完成"""
        self.log(f"✓ 完成: {os.path.basename(output_path)}")
        self.progress_bar.setValue(self.progress_bar.value() + 1)
        self._process_next_file()
    
    def _on_file_error(self, error_msg: str):
        """单个文件处理出错"""
        self.log(f"✗ 错误: {error_msg}")
        QMessageBox.critical(self, "转换错误", f"处理文件时出错:\n{error_msg}")
        self._process_next_file()
    
    def _conversion_complete(self):
        """所有文件处理完成"""
        self.progress_bar.setVisible(False)
        self.convert_btn.setEnabled(True)
        self.select_btn.setEnabled(True)
        self.clear_btn.setEnabled(True)
        self.statusBar().showMessage("转换完成")
        self.log("\n=== 所有文件处理完成 ===\n")
        
        QMessageBox.information(self, "完成", "所有文件已处理完成！")
    
    def log(self, message: str):
        """添加日志"""
        self.log_text.append(message)
        self.log_text.verticalScrollBar().setValue(
            self.log_text.verticalScrollBar().maximum()
        )
    
    def closeEvent(self, event):
        """关闭事件"""
        if self.current_thread and self.current_thread.isRunning():
            reply = QMessageBox.question(
                self,
                "确认退出",
                "有任务正在运行，确定要退出吗？",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                self.current_thread.terminate()
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()


def main():
    app = QApplication(sys.argv)
    
    # 设置应用程序样式
    app.setStyle("Fusion")
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
