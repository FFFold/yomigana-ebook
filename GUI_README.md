# Yomigana Ebook GUI 版本

## 功能特点

- **图形化界面**: 直观的拖拽操作，无需命令行
- **批量处理**: 支持一次转换多个EPUB文件
- **自动词典管理**: 自动检测和下载unidic词典
- **转换选项**: 支持过滤非日文段落（适用于中日文混合排版）
- **进度显示**: 实时显示转换进度和日志

## 安装和运行

### 方法一：直接运行Python脚本（开发模式）

1. 确保在 yomigana conda 环境中：
   ```bash
   conda activate yomigana
   ```

2. 安装GUI依赖：
   ```bash
   pip install PySide6
   ```

3. 运行GUI程序：
   ```bash
   python gui.py
   ```

### 方法二：打包成独立可执行文件

1. 确保在 yomigana conda 环境中：
   ```bash
   conda activate yomigana
   ```

2. 运行打包脚本：
   ```bash
   build_gui.bat
   ```

3. 打包完成后，在 `dist\` 目录中找到 `YomiganaEbook.exe`

## 首次使用

### 自动下载词典

1. 首次运行程序时，会自动检测unidic词典
2. 如果未安装词典，会弹出对话框询问是否下载
3. 点击"Yes"开始下载（约500MB，需要几分钟）
4. 下载完成后即可正常使用

### 手动安装词典

如果自动下载失败，可以手动安装：

```bash
conda activate yomigana
python -m unidic download
```

## 使用说明

### 主界面功能

1. **文件选择区域**
   - 拖拽EPUB文件到窗口
   - 或点击"选择文件"按钮选择多个文件
   - 支持批量选择多个EPUB文件

2. **转换选项**
   - **过滤非日文段落**: 勾选后只对包含日文假名的段落添加注音
   - 适用于中日文混合排版的电子书

3. **转换按钮**
   - 点击"开始转换"开始处理
   - 转换过程中显示进度条
   - 实时显示转换日志

4. **输出文件**
   - 转换后的文件保存在原文件同目录
   - 文件名格式: `with-yomigana_原文件名.epub`

### 注意事项

- 词典文件（约500MB）不会打包在exe中，以减小文件体积
- 词典会被下载到Python的site-packages目录
- 打包后的exe文件约50-80MB（不含词典）
- 支持Windows 10/11系统

## 故障排除

### 问题：程序无法启动，提示缺少DLL

**解决方案**: 确保在yomigana conda环境中运行，或使用打包后的exe文件

### 问题：转换失败，提示词典错误

**解决方案**: 
1. 检查词典是否已下载：运行 `python -m unidic download`
2. 重新启动程序

### 问题：打包失败

**解决方案**:
1. 确保在yomigana conda环境中
2. 检查是否已安装PyInstaller: `pip install pyinstaller`
3. 清理旧的构建文件后重试

## 技术说明

### 打包配置

- 使用PyInstaller打包，生成单个exe文件
- 不包含unidic词典（约500MB），运行时自动下载
- 使用PySide6构建原生GUI界面
- 支持多进程并行处理，提高转换速度

### 文件结构

```
yomigana-ebook/
├── gui.py              # GUI主程序
├── gui.spec            # PyInstaller配置
├── build_gui.bat       # Windows打包脚本
├── yomigana_ebook/     # 核心库
│   ├── checking.py     # 词典检测功能
│   ├── ...
└── dist/               # 打包输出目录
    └── YomiganaEbook.exe
```

## 许可证

MIT License - 同主项目
