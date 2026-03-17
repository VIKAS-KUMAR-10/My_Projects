#!/bin/bash
# codeScanner Setup Script for Linux/macOS
# This script automates the creation of a virtual environment and installation of dependencies.

set -e

echo "🛡️  Starting codeScanner setup..."

# Check for Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: python3 is not installed. Please install Python 3.8+."
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv .venv
else
    echo "✅ Virtual environment already exists."
fi

# Install dependencies
echo "⚙️  Installing dependencies and project in editable mode..."
./.venv/bin/pip install --upgrade pip
./.venv/bin/pip install -e .

echo ""
echo "✨ Setup Complete!"
echo "To use codeScanner, activate the environment with:"
echo "    source .venv/bin/activate"
echo "Then run:"
echo "    codescanner --help"
