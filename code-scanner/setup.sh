#!/bin/bash
# codeScanner Setup Script for Linux/macOS
# This script automates the creation of a virtual environment and installation of dependencies.

set -e

echo "Starting codeScanner setup..."

# Check for Python 3.8+
PYTHON_CMD=""
for cmd in python3 python; do
    if command -v "$cmd" &> /dev/null; then
        PYTHON_CMD="$cmd"
        break
    fi
done

if [ -z "$PYTHON_CMD" ]; then
    echo "Error: Python 3.8+ is not installed or not in PATH."
    echo "Please install it from https://www.python.org/downloads/"
    exit 1
fi

echo "Found: $($PYTHON_CMD --version)"

# Remove old venv if it exists to ensure a clean install
if [ -d ".venv" ]; then
    echo "Removing old virtual environment..."
    rm -rf .venv
fi

# Create virtual environment
echo "Creating virtual environment..."
$PYTHON_CMD -m venv .venv

# Verify the venv was created
if [ ! -f ".venv/bin/python" ]; then
    echo "Error: Virtual environment creation failed. Check your Python installation."
    exit 1
fi

echo "Virtual environment created successfully."

# Upgrade pip
echo "Upgrading pip..."
./.venv/bin/python -m pip install --upgrade pip

# Install project
echo "Installing codeScanner and its dependencies..."
./.venv/bin/python -m pip install -e .

echo ""
echo "============================================"
echo "  Setup Complete!"
echo "============================================"
echo ""
echo "Activate the virtual environment:"
echo "    source .venv/bin/activate"
echo ""
echo "Then run:"
echo "    codescanner --help"
echo ""
