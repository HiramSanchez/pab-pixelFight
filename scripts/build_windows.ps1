$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $PSScriptRoot

Push-Location $ProjectRoot
try {
    python -m PyInstaller --noconfirm --clean packaging/windows/PixelFight.spec
    if ($LASTEXITCODE -ne 0) {
        throw "PyInstaller build failed."
    }

    python scripts/validate_distribution.py dist/PixelFight
    if ($LASTEXITCODE -ne 0) {
        throw "Distribution validation failed."
    }

    python scripts/smoke_test_executable.py dist/PixelFight/PixelFight.exe
    if ($LASTEXITCODE -ne 0) {
        throw "Packaged startup failed."
    }

    $Archive = Join-Path $ProjectRoot "dist/PixelFight-windows-x64.zip"
    Compress-Archive -Path "dist/PixelFight/*" -DestinationPath $Archive -Force
    Write-Host "Created $Archive"
}
finally {
    Pop-Location
}
