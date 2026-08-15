"""Main window for the yomigana-ebook desktop GUI."""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt, QUrl, Signal
from PySide6.QtGui import QCloseEvent, QDragEnterEvent, QDragMoveEvent, QDropEvent
from PySide6.QtWidgets import (
    QCheckBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QPlainTextEdit,
    QProgressBar,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from yomigana_desktop.worker import ConvertWorker


class DropListWidget(QListWidget):
    """A list widget that accepts dragged-in EPUB files."""

    files_dropped = Signal(list)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        if self._has_epub_urls(event.mimeData().urls()):
            event.acceptProposedAction()
        else:
            super().dragEnterEvent(event)

    def dragMoveEvent(self, event: QDragMoveEvent) -> None:
        if self._has_epub_urls(event.mimeData().urls()):
            event.acceptProposedAction()
        else:
            super().dragMoveEvent(event)

    def dropEvent(self, event: QDropEvent) -> None:
        paths = [
            url.toLocalFile()
            for url in event.mimeData().urls()
            if url.isLocalFile()
            and url.toLocalFile().lower().endswith(".epub")
        ]
        if paths:
            self.files_dropped.emit(paths)
            event.acceptProposedAction()
        else:
            super().dropEvent(event)

    @staticmethod
    def _has_epub_urls(urls: list[QUrl]) -> bool:
        return any(
            url.isLocalFile()
            and url.toLocalFile().lower().endswith(".epub")
            for url in urls
        )


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("yomigana ebook - Windows GUI")
        self.resize(720, 560)

        self._worker: ConvertWorker | None = None
        self._succeeded_count = 0
        self._failed_count = 0

        self._build_ui()

    def _build_ui(self) -> None:
        central = QWidget(self)
        layout = QVBoxLayout(central)

        # File selection area
        file_label = QLabel("EPUB 文件（可拖拽多个）", central)
        layout.addWidget(file_label)

        self.file_list = DropListWidget(central)
        self.file_list.files_dropped.connect(self._add_paths)
        layout.addWidget(self.file_list, 1)

        file_buttons = QHBoxLayout()
        self.add_button = QPushButton("添加 EPUB…", central)
        self.remove_button = QPushButton("移除选中", central)
        self.clear_button = QPushButton("清空", central)
        self.add_button.clicked.connect(self._choose_files)
        self.remove_button.clicked.connect(self._remove_selected)
        self.clear_button.clicked.connect(self.file_list.clear)
        file_buttons.addWidget(self.add_button)
        file_buttons.addWidget(self.remove_button)
        file_buttons.addWidget(self.clear_button)
        file_buttons.addStretch(1)
        layout.addLayout(file_buttons)

        # Output directory
        output_layout = QHBoxLayout()
        output_label = QLabel("输出目录：", central)
        self.output_edit = QLineEdit(central)
        self.output_edit.setPlaceholderText("留空 = 与源 EPUB 同目录")
        self.output_button = QPushButton("浏览…", central)
        self.output_clear_button = QPushButton("重置", central)
        self.output_button.clicked.connect(self._choose_output_dir)
        self.output_clear_button.clicked.connect(self.output_edit.clear)
        output_layout.addWidget(output_label)
        output_layout.addWidget(self.output_edit, 1)
        output_layout.addWidget(self.output_button)
        output_layout.addWidget(self.output_clear_button)
        layout.addLayout(output_layout)

        # Options
        options_layout = QHBoxLayout()
        self.filter_checkbox = QCheckBox("过滤非日语段落（-f）", central)
        options_layout.addWidget(self.filter_checkbox)
        options_layout.addStretch(1)
        layout.addLayout(options_layout)

        # Action row
        action_layout = QHBoxLayout()
        self.start_button = QPushButton("开始转换", central)
        self.stop_button = QPushButton("停止", central)
        self.stop_button.setEnabled(False)
        self.start_button.clicked.connect(self._start_conversion)
        self.stop_button.clicked.connect(self._stop_conversion)
        action_layout.addWidget(self.start_button)
        action_layout.addWidget(self.stop_button)
        action_layout.addStretch(1)
        layout.addLayout(action_layout)

        # Progress
        self.progress_bar = QProgressBar(central)
        self.progress_bar.setRange(0, 1)
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)

        self.status_label = QLabel("就绪", central)
        layout.addWidget(self.status_label)

        # Log
        log_label = QLabel("日志：", central)
        layout.addWidget(log_label)

        self.log_view = QPlainTextEdit(central)
        self.log_view.setReadOnly(True)
        layout.addWidget(self.log_view, 2)

        self.setCentralWidget(central)

    def _add_paths(self, paths: list[str]) -> None:
        existing = {
            self.file_list.item(i).data(Qt.ItemDataRole.UserRole)
            for i in range(self.file_list.count())
        }
        for path in paths:
            normalized = str(Path(path).resolve())
            if normalized in existing:
                continue
            item = QListWidgetItem(Path(path).name)
            item.setData(Qt.ItemDataRole.UserRole, normalized)
            item.setToolTip(normalized)
            self.file_list.addItem(item)
            existing.add(normalized)

    def _choose_files(self) -> None:
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "选择 EPUB 文件",
            "",
            "EPUB 文件 (*.epub);;所有文件 (*.*)",
        )
        if files:
            self._add_paths(files)

    def _remove_selected(self) -> None:
        for item in self.file_list.selectedItems():
            self.file_list.takeItem(self.file_list.row(item))

    def _choose_output_dir(self) -> None:
        directory = QFileDialog.getExistingDirectory(self, "选择输出目录")
        if directory:
            self.output_edit.setText(directory)

    def _collect_paths(self) -> list[Path]:
        return [
            Path(self.file_list.item(i).data(Qt.ItemDataRole.UserRole))
            for i in range(self.file_list.count())
        ]

    def _start_conversion(self) -> None:
        paths = self._collect_paths()
        if not paths:
            QMessageBox.information(self, "提示", "请先添加至少一个 EPUB 文件。")
            return

        output_text = self.output_edit.text().strip()
        output_dir = Path(output_text) if output_text else None

        self._succeeded_count = 0
        self._failed_count = 0
        self.log_view.clear()
        self._set_running(True)

        worker = ConvertWorker(
            paths,
            output_dir,
            filter_non_japanese=self.filter_checkbox.isChecked(),
            parent=self,
        )
        worker.progress.connect(self._on_progress)
        worker.log.connect(self._append_log)
        worker.book_succeeded.connect(self._on_book_succeeded)
        worker.book_failed.connect(self._on_book_failed)
        worker.all_done.connect(self._on_all_done)
        self._worker = worker
        worker.start()

    def _stop_conversion(self) -> None:
        if self._worker is not None:
            self._worker.request_stop()
            self.stop_button.setEnabled(False)
            self._append_log("[info] 正在停止，当前文件处理完会停止……")

    def _set_running(self, running: bool) -> None:
        self.start_button.setEnabled(not running)
        self.add_button.setEnabled(not running)
        self.remove_button.setEnabled(not running)
        self.clear_button.setEnabled(not running)
        self.output_edit.setEnabled(not running)
        self.output_button.setEnabled(not running)
        self.output_clear_button.setEnabled(not running)
        self.filter_checkbox.setEnabled(not running)
        self.stop_button.setEnabled(running)
        self.progress_bar.setRange(0, 1)
        self.progress_bar.setValue(0)
        self.status_label.setText("正在转换…" if running else "就绪")

    def _on_progress(self, book_index: int, book_count: int, done: int, total: int) -> None:
        if total <= 0:
            self.progress_bar.setRange(0, 0)
            self.status_label.setText(f"正在处理第 {book_index}/{book_count} 本书…")
            return

        self.progress_bar.setRange(0, total)
        self.progress_bar.setValue(done)
        self.status_label.setText(
            f"正在处理第 {book_index}/{book_count} 本书：HTML {done}/{total}"
        )

    def _append_log(self, message: str) -> None:
        self.log_view.appendPlainText(message)

    def _on_book_succeeded(
        self, _input_path: str, output_path: str, elapsed: float
    ) -> None:
        self._succeeded_count += 1
        self.status_label.setText(
            f"已完成 {self._succeeded_count} 本，输出：{output_path}（{elapsed:.2f} 秒）"
        )

    def _on_book_failed(self, input_path: str, _error: str) -> None:
        self._failed_count += 1
        self.status_label.setText(f"转换失败：{Path(input_path).name}")

    def _on_all_done(self, succeeded: int, failed: int) -> None:
        self._worker = None
        self._set_running(False)
        self.status_label.setText(f"全部完成：成功 {succeeded} 本，失败 {failed} 本")
        self.progress_bar.setRange(0, 1)
        self.progress_bar.setValue(1 if failed == 0 and succeeded > 0 else 0)
        if failed:
            QMessageBox.warning(
                self,
                "转换完成",
                f"成功 {succeeded} 本，失败 {failed} 本。请查看日志。",
            )
        else:
            QMessageBox.information(self, "转换完成", f"全部 {succeeded} 本转换成功。")

    def closeEvent(self, event: QCloseEvent) -> None:  # noqa: N802
        if self._worker is not None and self._worker.isRunning():
            answer = QMessageBox.question(
                self,
                "确认退出",
                "转换仍在进行中，确定要退出吗？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )
            if answer != QMessageBox.StandardButton.Yes:
                event.ignore()
                return
            self._worker.request_stop()
            self._worker.wait()
        event.accept()
