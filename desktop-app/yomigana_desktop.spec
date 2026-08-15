# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec for yomigana-desktop.

Build with (from repo root):

    uv run --project desktop-app pyinstaller desktop-app/yomigana_desktop.spec

The output is a folder (onedir) at desktop-app/dist/yomigana-desktop/.
UniDic dictionary data is included in the bundle; if you prefer a smaller
distribution, remove the dicdir entry below and place the dictionary next to
the executable as unidic/dicdir (or set YOMIGANA_UNICID_DIR).
"""

import os
from pathlib import Path

import unidic
from PyInstaller.utils.hooks import collect_dynamic_libs

dicdir = Path(unidic.DICDIR)

# Set YOMIGANA_BUNDLE_UNIDIC=0 to keep the dictionary outside the bundle.
# The app will then look for unidic/dicdir next to the executable or in
# _internal/unidic/dicdir (or use YOMIGANA_UNICID_DIR).
bundle_unidic = os.environ.get("YOMIGANA_BUNDLE_UNIDIC", "1") == "1"
datas = []
if bundle_unidic:
    datas.append((str(dicdir), os.path.join("unidic", "dicdir")))
binaries = collect_dynamic_libs("fugashi")

a = Analysis(
    ["desktop-app/yomigana_desktop/app.py"],
    pathex=["desktop-app"],
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
