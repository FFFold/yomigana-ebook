@echo off
REM Windows打包脚本 - 为Yomigana Ebook创建独立GUI可执行文件

echo ============================================
echo Yomigana Ebook GUI 打包工具
echo ============================================
echo.

REM 检查是否在conda环境中
if "%CONDA_DEFAULT_ENV%"=="" (
    echo 错误: 请在 yomigana conda 环境中运行此脚本
    echo 请先运行: conda activate yomigana
    exit /b 1
)

if not "%CONDA_DEFAULT_ENV%"=="yomigana" (
    echo 错误: 请在 yomigana conda 环境中运行此脚本
    echo 当前环境: %CONDA_DEFAULT_ENV%
    echo 请先运行: conda activate yomigana
    exit /b 1
)

echo 当前conda环境: %CONDA_DEFAULT_ENV%
echo.

REM 检查依赖
echo 检查依赖...
pip show PySide6 >nul 2>&1
if errorlevel 1 (
    echo 安装 PySide6...
    pip install PySide6
)

pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo 安装 PyInstaller...
    pip install pyinstaller
)

echo.
echo 开始打包...
echo.

REM 清理旧的构建文件
if exist build (
    echo 清理旧的构建文件...
    rmdir /s /q build
)

if exist dist (
    echo 清理旧的输出文件...
    rmdir /s /q dist
)

REM 使用spec文件打包
echo 正在打包GUI应用程序...
pyinstaller gui.spec

if errorlevel 1 (
    echo.
    echo 打包失败！
    exit /b 1
)

echo.
echo ============================================
echo 打包完成！
echo ============================================
echo.
echo 可执行文件位置: dist\YomiganaEbook.exe
echo.
echo 首次运行说明:
echo 1. 运行 YomiganaEbook.exe
echo 2. 程序会自动检测词典
echo 3. 如果未安装词典，会提示下载（约500MB）
echo 4. 也可以手动安装: python -m unidic download
echo.
echo 注意事项:
echo - 词典文件不会打包在exe中，以减小文件体积
echo - 词典会被下载到用户目录下的unidic文件夹
echo - 打包后的exe文件约50-80MB（不含词典）
echo ============================================

pause
