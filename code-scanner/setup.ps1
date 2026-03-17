# codeScanner Setup Script for Windows
# Handles standard Python, Windows Store Python, and MSYS2/MinGW Python

Write-Host "Starting codeScanner setup..." -ForegroundColor Cyan

# ─────────────────────────────────────────────
# Step 1: Find a REAL working Python executable
# (skip Windows Store stubs)
# ─────────────────────────────────────────────
$pythonCmd = $null

# Known real Python paths to check first (bypasses Store alias)
$knownPaths = @(
    "C:\msys64\ucrt64\bin\python.exe",
    "C:\msys64\usr\bin\python3.exe",
    "C:\Python312\python.exe",
    "C:\Python311\python.exe",
    "C:\Python310\python.exe",
    "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe",
    "$env:LOCALAPPDATA\Programs\Python\Python311\python.exe",
    "$env:LOCALAPPDATA\Programs\Python\Python310\python.exe"
)

foreach ($path in $knownPaths) {
    if (Test-Path $path) {
        $ver = & $path --version 2>&1
        if ($ver -match "Python 3") {
            $pythonCmd = $path
            Write-Host "Found: $ver (at $path)" -ForegroundColor Green
            break
        }
    }
}

# Fallback: try py launcher, then python (if not Store stub)
if ($null -eq $pythonCmd) {
    foreach ($cmd in @("py", "python3")) {
        try {
            $ver = & $cmd --version 2>&1
            if ($LASTEXITCODE -eq 0 -and $ver -match "Python 3") {
                $pythonCmd = $cmd
                Write-Host "Found: $ver (using '$cmd')" -ForegroundColor Green
                break
            }
        } catch {}
    }
}

if ($null -eq $pythonCmd) {
    Write-Error "No valid Python 3.8+ found."
    Write-Host "Options: Install Python from https://www.python.org/downloads/ (check 'Add Python to PATH')" -ForegroundColor Yellow
    exit 1
}

# ─────────────────────────────────────────────
# Step 2: Create Virtual Environment
# ─────────────────────────────────────────────
if (Test-Path ".venv") {
    Write-Host "Removing old virtual environment..." -ForegroundColor Yellow
    Remove-Item -Recurse -Force ".venv"
}

Write-Host "Creating virtual environment..." -ForegroundColor Green
& $pythonCmd -m venv .venv 2>&1

if ($LASTEXITCODE -ne 0) {
    Write-Error "Failed to create virtual environment."
    exit 1
}

# ─────────────────────────────────────────────
# Step 3: Verify venv (handle Windows vs Unix/MSYS2 structure)
# ─────────────────────────────────────────────
$venvPython = $null
$venvBinDir = $null

# Search for python executable in both Scripts (Win) and bin (Unix/MSYS2)
foreach ($dir in @("Scripts", "bin")) {
    foreach ($exe in @("python.exe", "python3.exe", "python")) {
        $path = Join-Path ".venv" (Join-Path $dir $exe)
        if (Test-Path $path) {
            $venvPython = $path
            $venvBinDir = Join-Path ".venv" $dir
            break
        }
    }
    if ($venvPython) { break }
}

if ($null -eq $venvPython) {
    Write-Error "Virtual environment is incomplete. Python executable not found in .venv/Scripts or .venv/bin."
    Write-Host "Structure of .venv:" -ForegroundColor Gray
    Get-ChildItem -Path ".venv" -Recurse | Select-Object -First 20 | ForEach-Object { Write-Host "  $($_.FullName)" -ForegroundColor Gray }
    exit 1
}

Write-Host "Virtual environment ready at $venvBinDir" -ForegroundColor Green

# ─────────────────────────────────────────────
# Step 4: Install dependencies
# ─────────────────────────────────────────────
Write-Host "Upgrading pip..." -ForegroundColor Green
& $venvPython -m pip install --upgrade pip

Write-Host "Installing codeScanner..." -ForegroundColor Green
& $venvPython -m pip install -e .

if ($LASTEXITCODE -ne 0) {
    Write-Error "Installation failed."
    exit 1
}

# ─────────────────────────────────────────────
# Done
# ─────────────────────────────────────────────
Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  Setup Complete!" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "To use codeScanner, activate the environment:" -ForegroundColor White
if (Test-Path (Join-Path $venvBinDir "Activate.ps1")) {
    Write-Host "    $venvBinDir\Activate.ps1" -ForegroundColor Yellow
} elseif (Test-Path (Join-Path $venvBinDir "activate")) {
    Write-Host "    source $venvBinDir/activate" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Then run:" -ForegroundColor White
Write-Host "    codescanner --help" -ForegroundColor Yellow
Write-Host ""
