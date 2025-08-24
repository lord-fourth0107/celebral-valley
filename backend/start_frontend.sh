#!/bin/bash

echo "🚀 Starting Collateral Management Frontend..."
echo "=============================================="

# Check if Python is available
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
else
    echo "❌ Python not found. Please install Python 3.7+"
    exit 1
fi

# Check if pip is available
if command -v pip3 &> /dev/null; then
    PIP_CMD="pip3"
elif command -v pip &> /dev/null; then
    PIP_CMD="pip"
else
    echo "❌ pip not found. Please install pip"
    exit 1
fi

echo "🐍 Python: $($PYTHON_CMD --version)"
echo "📦 pip: $($PIP_CMD --version)"

# Install Flask if not available
echo "📥 Installing Flask dependencies..."
$PIP_CMD install -r frontend_requirements.txt

# Check if Flask is installed
if ! $PYTHON_CMD -c "import flask" 2>/dev/null; then
    echo "❌ Flask installation failed"
    exit 1
fi

echo "✅ Flask installed successfully"

# Start the frontend
echo "🌐 Starting Flask frontend on http://localhost:5001"
echo "📡 Backend URL: http://localhost:8000"
echo "🔗 Dashboard: http://localhost:5001"
echo "📸 Create Collateral: http://localhost:5001/collateral/create"
echo "📋 View Collaterals: http://localhost:5001/collateral/list"
echo ""
echo "Press Ctrl+C to stop the server"
echo "=============================================="

$PYTHON_CMD frontend.py
