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
    Write-Host ""
    Write-Host "Options:" -ForegroundColor Yellow
    Write-Host "  1. Install Python from: https://www.python.org/downloads/" -ForegroundColor Yellow
    Write-Host "     (check 'Add Python to PATH' during install)" -ForegroundColor Yellow
    Write-Host "  2. If using MSYS2: pacman -S mingw-w64-ucrt-x86_64-python" -ForegroundColor Yellow
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
# Step 3: Verify venv
# ─────────────────────────────────────────────
$venvPython = $null
foreach ($p in @(".venv\Scripts\python.exe", ".venv\Scripts\python3.exe")) {
    if (Test-Path $p) { $venvPython = $p; break }
}

$venvPip = $null
foreach ($p in @(".venv\Scripts\pip.exe", ".venv\Scripts\pip3.exe")) {
    if (Test-Path $p) { $venvPip = $p; break }
}

if ($null -eq $venvPython -and $null -eq $venvPip) {
    Write-Error "Virtual environment is incomplete."
    exit 1
}

Write-Host "Virtual environment ready." -ForegroundColor Green

# ─────────────────────────────────────────────
# Step 4: Install dependencies
# ─────────────────────────────────────────────
$runner = if ($venvPython) { $venvPython } else { $venvPip }

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
Write-Host "Activate the virtual environment:" -ForegroundColor White
Write-Host "    .\.venv\Scripts\Activate.ps1" -ForegroundColor Yellow
Write-Host ""
Write-Host "Then run:" -ForegroundColor White
Write-Host "    codescanner --help" -ForegroundColor Yellow
Write-Host ""
