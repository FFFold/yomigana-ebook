"""Generate a multi-size ICO from the SVG placeholder icon.

Run from the repository root:

    uv run --project desktop-app python desktop-app/generate_icon.py
"""

from __future__ import annotations

import struct
import sys
from pathlib import Path

from PySide6.QtCore import QBuffer, QIODevice, Qt
from PySide6.QtGui import QGuiApplication, QImage, QPainter
from PySide6.QtSvg import QSvgRenderer

ICON_SIZES = (16, 24, 32, 48, 64, 128, 256)


def render_png(svg_path: Path, size: int) -> bytes:
    renderer = QSvgRenderer(str(svg_path))
    image = QImage(size, size, QImage.Format.Format_ARGB32)
    image.fill(Qt.GlobalColor.transparent)
    painter = QPainter(image)
    renderer.render(painter)
    painter.end()

    buffer = QBuffer()
    buffer.open(QIODevice.OpenModeFlag.WriteOnly)
    image.save(buffer, "PNG")
    return bytes(buffer.data())


def build_ico(pngs: list[tuple[int, bytes]]) -> bytes:
    header = struct.pack("<HHH", 0, 1, len(pngs))
    entries = bytearray()
    offset = 6 + 16 * len(pngs)

    for size, png in pngs:
        width = 0 if size >= 256 else size
        height = 0 if size >= 256 else size
        entries.extend(
            struct.pack(
                "<BBBBHHII",
                width,
                height,
                0,
                0,
                1,
                32,
                len(png),
                offset,
            )
        )
        offset += len(png)

    return header + bytes(entries) + b"".join(png for _, png in pngs)


def main() -> int:
    app = QGuiApplication([])  # noqa: F841 - required for QSvgRenderer with text

    svg_path = Path(__file__).resolve().parent / "assets" / "yomigana.svg"
    ico_path = Path(__file__).resolve().parent / "assets" / "yomigana.ico"

    pngs = [(size, render_png(svg_path, size)) for size in ICON_SIZES]
    ico_path.write_bytes(build_ico(pngs))
    print(f"Generated {ico_path} with sizes {ICON_SIZES}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
