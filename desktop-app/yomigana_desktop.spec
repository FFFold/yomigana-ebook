# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec for yomigana-desktop.

Build with (from repo root):

    uv run --project desktop-app pyinstaller desktop-app/yomigana_desktop.spec

The output is a folder (onedir) at dist/yomigana-desktop/.
By default the UniDic dictionary data is included in the bundle. Set
YOMIGANA_BUNDLE_UNICID=0 to keep it external; the app then looks for
unidic/dicdir next to the executable (or in _internal/unidic/dicdir), or uses
the YOMIGANA_UNIDIC_DIR environment variable.
"""

import os
from pathlib import Path

import unidic
from PyInstaller.utils.hooks import collect_dynamic_libs

desktop_root = Path(SPECPATH).resolve()
dicdir = Path(unidic.DICDIR)
icon_svg = desktop_root / "assets" / "yomigana.svg"
icon_ico = desktop_root / "assets" / "yomigana.ico"

# Set YOMIGANA_BUNDLE_UNICID=0 to keep the dictionary outside the bundle.
bundle_unidic = os.environ.get("YOMIGANA_BUNDLE_UNICID", "1") == "1"
datas = [
    (str(icon_svg), "assets"),
    (str(icon_ico), "assets"),
]
if bundle_unidic:
    datas.append((str(dicdir), os.path.join("unidic", "dicdir")))
binaries = collect_dynamic_libs("fugashi")

a = Analysis(
    [str(desktop_root / "yomigana_desktop" / "app.py")],
    pathex=[str(desktop_root)],
    binaries=binaries,
    datas=datas,
    hiddenimports=[
        "unidic",
        "fugashi",
        "bs4",
        "lxml",
        "yomigana_ebook",
        "yomigana_ebook.cli",
        "yomigana_ebook.process_ebook",
        "yomigana_ebook.yomituki",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)

# PyInstaller tends to include unidic/dicdir automatically because it lives
# inside the installed unidic package. When the user asks for an external
# dictionary, strip it from the bundle so the distribution stays small.
def _is_unidic_data(entry):
    return any(
        "unidic/dicdir" in str(value).replace("\\", "/") for value in entry[:2]
    )


if not bundle_unidic:
    a.datas = [entry for entry in a.datas if not _is_unidic_data(entry)]

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="yomigana-desktop",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(icon_ico),
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="yomigana-desktop",
)
