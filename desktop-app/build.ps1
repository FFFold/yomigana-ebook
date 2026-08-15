# Build the Windows GUI with PyInstaller.
# Run from the repository root:
#   powershell -ExecutionPolicy Bypass -File desktop-app/build.ps1

$ErrorActionPreference = "Stop"

uv run --project desktop-app pyinstaller `
    --noconfirm `
    --clean `
    desktop-app/yomigana_desktop.spec

Write-Host ""
Write-Host "Build finished: desktop-app/dist/yomigana-desktop/yomigana-desktop.exe"
