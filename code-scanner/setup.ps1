# codeScanner Setup Script for Windows
# This script automates the creation of a virtual environment and installation of dependencies.

Write-Host "Starting codeScanner setup..." -ForegroundColor Cyan

# Check for Python
if (!(Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Error "Python is not installed or not in PATH. Please install Python 3.8+."
    exit 1
}

# Create virtual environment if it doesn't exist
if (!(Test-Path ".venv")) {
    Write-Host "Creating virtual environment..." -ForegroundColor Green
    python -m venv .venv
} else {
    Write-Host "Virtual environment already exists." -ForegroundColor Yellow
}

# Install dependencies
Write-Host "Installing dependencies and project in editable mode..." -ForegroundColor Green
& .\.venv\Scripts\python.exe -m pip install --upgrade pip
& .\.venv\Scripts\python.exe -m pip install -e .

Write-Host ""
Write-Host "Setup Complete!" -ForegroundColor Cyan
Write-Host "To use codeScanner, activate the environment with:" -ForegroundColor White
Write-Host "    .\.venv\Scripts\Activate.ps1" -ForegroundColor Yellow
Write-Host "Then run:" -ForegroundColor White
Write-Host "    codescanner --help" -ForegroundColor Yellow
