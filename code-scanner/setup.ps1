# codeScanner Setup Script for Windows
# Handles standard Python installs and Windows Store Python

Write-Host "Starting codeScanner setup..." -ForegroundColor Cyan

# ─────────────────────────────────────────────
# Step 1: Find a working Python executable
# ─────────────────────────────────────────────
$pythonCmd = $null

# Priority: py launcher > python > python3
foreach ($cmd in @("py", "python", "python3")) {
    try {
        $ver = & $cmd --version 2>&1
        if ($LASTEXITCODE -eq 0 -and $ver -match "Python 3") {
            $pythonCmd = $cmd
            Write-Host "Found: $ver (using '$cmd')" -ForegroundColor Green
            break
        }
    } catch {}
}

if ($null -eq $pythonCmd) {
    Write-Error "Python 3.8+ not found. Download from: https://www.python.org/downloads/"
    Write-Host "Tip: During install, check 'Add Python to PATH'" -ForegroundColor Yellow
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
# Step 3: Verify venv (check multiple locations)
# ─────────────────────────────────────────────
$pipExe    = $null
$pythonExe = $null

foreach ($p in @(".venv\Scripts\pip.exe", ".venv\Scripts\pip3.exe")) {
    if (Test-Path $p) { $pipExe = $p; break }
}
foreach ($p in @(".venv\Scripts\python.exe", ".venv\Scripts\python3.exe")) {
    if (Test-Path $p) { $pythonExe = $p; break }
}

if ($null -eq $pipExe -and $null -eq $pythonExe) {
    Write-Error "Virtual environment is incomplete. Your Python may be from the Microsoft Store."
    Write-Host "" 
    Write-Host "Fix: Open 'Manage App Execution Aliases' in Windows Settings" -ForegroundColor Yellow
    Write-Host "     and turn OFF the python.exe / python3.exe Store aliases." -ForegroundColor Yellow
    Write-Host "     Then reinstall Python from https://www.python.org/downloads/" -ForegroundColor Yellow
    exit 1
}

Write-Host "Virtual environment ready." -ForegroundColor Green

# ─────────────────────────────────────────────
# Step 4: Install dependencies
# ─────────────────────────────────────────────
Write-Host "Upgrading pip..." -ForegroundColor Green
if ($pythonExe) {
    & $pythonExe -m pip install --upgrade pip
} else {
    & $pipExe install --upgrade pip
}

Write-Host "Installing codeScanner..." -ForegroundColor Green
if ($pythonExe) {
    & $pythonExe -m pip install -e .
} else {
    & $pipExe install -e .
}

if ($LASTEXITCODE -ne 0) {
    Write-Error "Installation failed. Check requirements.txt or pyproject.toml."
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
