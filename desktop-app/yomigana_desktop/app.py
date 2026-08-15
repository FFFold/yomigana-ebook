"""Entry point for the yomigana-ebook Windows GUI."""

from __future__ import annotations

import multiprocessing
import sys
from pathlib import Path

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication, QMessageBox

from yomigana_desktop.dictionary import configure_unidic_dir


def _icon_path() -> Path | None:
    """Return the app icon (ICO preferred, SVG fallback) or None."""
    if getattr(sys, "frozen", False):
        base_candidates = [
            Path(sys._MEIPASS) / "assets",
            Path(sys.executable).resolve().parent / "assets",
        ]
    else:
        base_candidates = [Path(__file__).resolve().parent.parent / "assets"]

    for base in base_candidates:
        for name in ("yomigana.ico", "yomigana.svg"):
            candidate = base / name
            if candidate.is_file():
                return candidate
    return None


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
            "或设置 YOMIGANA_UNIDIC_DIR 环境变量指向词典目录。",
        )
        return 1

    app = QApplication(sys.argv)
    app.setApplicationName("yomigana ebook")

    icon_path = _icon_path()
    if icon_path is not None:
        app.setWindowIcon(QIcon(str(icon_path)))

    # Import after the dictionary is configured so the lazy worker import and
    # child processes see the correct YOMIGANA_UNIDIC_DIR.
    from yomigana_desktop.main_window import MainWindow

    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
