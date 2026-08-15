"""Background conversion worker for the desktop GUI."""

from __future__ import annotations

from pathlib import Path
from time import time

from PySide6.QtCore import QObject, QThread, Signal


class ConvertWorker(QThread):
    """Convert a list of EPUB files sequentially in a background thread.

    ``process_ebook`` already parallelizes the HTML files inside one EPUB, so
    processing multiple books one at a time keeps CPU usage predictable while
    still giving per-book progress updates.
    """

    # book_index (1-based), book_count, html_done, html_total
    progress = Signal(int, int, int, int)
    log = Signal(str)
    book_succeeded = Signal(str, str, float)
    book_failed = Signal(str, str)
    all_done = Signal(int, int)

    def __init__(
        self,
        ebook_paths: list[Path],
        output_dir: Path | None,
        filter_non_japanese: bool = False,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self._ebook_paths = ebook_paths
        self._output_dir = output_dir
        self._filter_non_japanese = filter_non_japanese
        self._stop_requested = False

    def request_stop(self) -> None:
        """Ask the worker to stop after the current book finishes."""
        self._stop_requested = True

    def run(self) -> None:  # noqa: D102
        # Import lazily so the GUI can set YOMIGANA_UNICID_DIR before the
        # module-level MeCab tagger is created.
        from yomigana_ebook.process_ebook import process_ebook

        total = len(self._ebook_paths)
        succeeded = 0
        failed = 0

        for index, ebook_path in enumerate(self._ebook_paths, start=1):
            if self._stop_requested:
                self.log.emit("[info] 已请求停止，跳过剩余文件")
                break

            input_path = Path(ebook_path)
            if not input_path.is_file():
                failed += 1
                self.book_failed.emit(str(input_path), "文件不存在")
                self.log.emit(f"[error] 文件不存在: {input_path}")
                continue

            output_path = self._build_output_path(input_path)
            if output_path is None:
                failed += 1
                self.book_failed.emit(str(input_path), "无法创建输出目录")
                continue

            self.log.emit(f"[start] ({index}/{total}) 正在处理: {input_path.name}")
            start_time = time()

            def on_progress(done: int, html_total: int) -> None:
                self.progress.emit(index, total, done, html_total)

            try:
                with input_path.open("rb") as reader, output_path.open("wb") as writer:
                    process_ebook(
                        reader,
                        writer,
                        self._filter_non_japanese,
                        progress_callback=on_progress,
                    )
            except Exception as exc:  # noqa: BLE001 - report any conversion failure in GUI
                failed += 1
                elapsed = time() - start_time
                self.book_failed.emit(str(input_path), str(exc))
                self.log.emit(
                    f"[error] ({index}/{total}) {input_path.name} 转换失败: {exc}"
                )
                self.log.emit(f"[done] 失败耗时 {elapsed:.2f} 秒")
                continue

            elapsed = time() - start_time
            succeeded += 1
            self.book_succeeded.emit(str(input_path), str(output_path), elapsed)
            self.log.emit(f"[done] ({index}/{total}) 输出: {output_path}")
            self.log.emit(f"[done] 耗时 {elapsed:.2f} 秒")

        self.all_done.emit(succeeded, failed)

    def _build_output_path(self, input_path: Path) -> Path | None:
        output_name = f"with-yomigana_{input_path.name}"
        if self._output_dir is None:
            return input_path.parent / output_name

        output_dir = Path(self._output_dir)
        try:
            output_dir.mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            self.log.emit(f"[error] 无法创建输出目录 {output_dir}: {exc}")
            return None
        return output_dir / output_name
