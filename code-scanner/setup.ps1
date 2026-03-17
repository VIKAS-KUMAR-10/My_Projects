# codeScanner Setup Script for Windows
# This script automates the creation of a virtual environment and installation of dependencies.

Write-Host "Starting codeScanner setup..." -ForegroundColor Cyan

# Check for Python
$pythonCmd = $null
foreach ($cmd in @("python", "python3", "py")) {
    if (Get-Command $cmd -ErrorAction SilentlyContinue) {
        $pythonCmd = $cmd
        break
    }
}

if ($null -eq $pythonCmd) {
    Write-Error "Python is not installed or not in PATH. Please install Python 3.8+ from https://www.python.org/downloads/"
    exit 1
}

$pythonVersion = & $pythonCmd --version 2>&1
Write-Host "Found: $pythonVersion" -ForegroundColor Green

# Create virtual environment
if (Test-Path ".venv") {
    Write-Host "Removing old virtual environment..." -ForegroundColor Yellow
    Remove-Item -Recurse -Force ".venv"
}

Write-Host "Creating virtual environment..." -ForegroundColor Green
& $pythonCmd -m venv .venv

if ($LASTEXITCODE -ne 0) {
    Write-Error "Failed to create virtual environment. Please check your Python installation."
    exit 1
}

# Verify the venv was created correctly
if (!(Test-Path ".venv\Scripts\python.exe")) {
    Write-Error "Virtual environment created but python.exe not found inside it. Try running: $pythonCmd -m venv .venv manually."
    exit 1
}

Write-Host "Virtual environment created successfully." -ForegroundColor Green

# Upgrade pip
Write-Host "Upgrading pip..." -ForegroundColor Green
& .\.venv\Scripts\python.exe -m pip install --upgrade pip
if ($LASTEXITCODE -ne 0) {
    Write-Error "Failed to upgrade pip."
    exit 1
}

# Install project
Write-Host "Installing codeScanner and its dependencies..." -ForegroundColor Green
& .\.venv\Scripts\python.exe -m pip install -e .
if ($LASTEXITCODE -ne 0) {
    Write-Error "Failed to install codeScanner. Check the requirements.txt or pyproject.toml."
    exit 1
}

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
