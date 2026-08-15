# yomigana-desktop

Windows GUI 桌面应用，为 [yomigana-ebook](../README.md) 提供图形界面。

## 功能

- 拖拽或选择多个 `.epub` 文件批量转换
- 可选“过滤非日语段落”（对应 CLI 的 `-f`）
- 可指定输出目录；留空时输出到源文件同目录
- 实时显示当前文件进度和日志
- 复用核心库的 `process_ebook` 并行 HTML 处理能力

## 开发运行

在项目根目录：

```bash
uv sync --group test
uv run python -m unidic download   # 首次必须
uv run --project desktop-app yomigana-desktop
```

或者：

```bash
cd desktop-app
uv run yomigana-desktop
# 或
uv run python -m yomigana_desktop
```

> 依赖 Python 3.11（与根项目一致）。
> 如果 UniDic 词典不在默认位置，可通过环境变量 `YOMIGANA_UNIDIC_DIR` 指定 `dicdir` 目录。

## 打包 Windows 可执行文件

项目使用 PyInstaller。由于 UniDic 词典较大，推荐使用 `--onedir` 方式，并把
**依赖库**和 **UniDic 词典**分开存放：

```text
dist/yomigana-desktop/
├── yomigana-desktop.exe   # 主程序
├── _internal/             # 依赖库（PySide6、fugashi 等）
└── unidic/dicdir/         # UniDic 词典（外置在 exe 旁边）
```

在项目根目录执行：

```powershell
powershell -ExecutionPolicy Bypass -File desktop-app/build.ps1
```

辅助脚本默认会以“词典外置”方式构建，并自动把 UniDic 词典复制到
`dist/yomigana-desktop/unidic/dicdir/`。

如果希望把词典也打进 `_internal`（单目录分发），可以设置环境变量后手动构建：

```powershell
$env:YOMIGANA_BUNDLE_UNICID = "1"
uv run --project desktop-app pyinstaller desktop-app/yomigana_desktop.spec
```

产物在 `dist/yomigana-desktop/`。

## 目录结构

```text
desktop-app/
├── pyproject.toml
├── README.md
├── yomigana_desktop.spec
└── yomigana_desktop/
    ├── __init__.py
    ├── app.py            # 入口：词典检查 + QApplication
    ├── dictionary.py     # UniDic 词典查找与 YOMIGANA_UNIDIC_DIR 配置
    ├── main_window.py    # 主窗口 UI
    └── worker.py         # 后台转换线程
```
