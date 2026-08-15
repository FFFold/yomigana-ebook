# Build the Windows GUI with PyInstaller.
# Run from anywhere:
#   powershell -ExecutionPolicy Bypass -File desktop-app/build.ps1
#
# The default output keeps dependencies and UniDic dictionary separate:
#   dist/yomigana-desktop/yomigana-desktop.exe
#   dist/yomigana-desktop/_internal/          <- dependencies only
#   dist/yomigana-desktop/unidic/dicdir/      <- UniDic dictionary
#
# Set YOMIGANA_BUNDLE_UNICID=1 to instead bundle the dictionary into _internal.

$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$oldBundleUnidic = $env:YOMIGANA_BUNDLE_UNICID

Push-Location $repoRoot
try {
    Remove-Item -Recurse -Force build, dist -ErrorAction SilentlyContinue

    $env:YOMIGANA_BUNDLE_UNICID = "0"

    uv run --project desktop-app pyinstaller `
        --noconfirm `
        --clean `
        desktop-app/yomigana_desktop.spec

    $dicdir = (& uv run --project desktop-app python -c "import unidic; print(unidic.DICDIR)").Trim()
    $dictTarget = "dist\yomigana-desktop\unidic\dicdir"
    New-Item -ItemType Directory -Force -Path $dictTarget | Out-Null
    Copy-Item -Path (Join-Path $dicdir "*") -Destination $dictTarget -Recurse -Force

    Write-Host ""
    Write-Host "Build finished: dist/yomigana-desktop/yomigana-desktop.exe"
    Write-Host "Dependencies:   dist/yomigana-desktop/_internal"
    Write-Host "UniDic dict:    dist/yomigana-desktop/unidic/dicdir"
}
finally {
    if ($null -eq $oldBundleUnidic) {
        Remove-Item Env:YOMIGANA_BUNDLE_UNICID -ErrorAction SilentlyContinue
    }
    else {
        $env:YOMIGANA_BUNDLE_UNICID = $oldBundleUnidic
    }
    Pop-Location
}
