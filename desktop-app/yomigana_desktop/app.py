"""Entry point for the yomigana-ebook Windows GUI."""

from __future__ import annotations

import multiprocessing
import sys

from PySide6.QtWidgets import QApplication, QMessageBox

from yomigana_desktop.dictionary import configure_unidic_dir


def main() -> int:
    # Required for ProcessPoolExecutor inside process_ebook when the app is
    # frozen with PyInstaller on Windows.
    multiprocessing.freeze_support()

    dicdir = configure_unidic_dir()
    if dicdir is None:
        app = QApplication(sys.argv)
        QMessageBox.critical(
            None,
            "UniDic 词典缺失",
            "未找到 UniDic 词典。\n\n"
            "请先在项目目录执行以下命令下载词典：\n"
            "  uv run python -m unidic download\n\n"
            "如果使用打包版，请将 unidic/dicdir 目录放在程序旁边，"
            "或设置 YOMIGANA_UNICID_DIR 环境变量指向词典目录。",
        )
        return 1

    app = QApplication(sys.argv)
    app.setApplicationName("yomigana ebook")

    # Import after the dictionary is configured so the lazy worker import and
    # child processes see the correct YOMIGANA_UNICID_DIR.
    from yomigana_desktop.main_window import MainWindow

    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
