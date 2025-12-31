# AIDA Quick Start Script
# This script activates the virtual environment and starts the Flask application

Write-Host "🚀 Starting AIDA Application..." -ForegroundColor Cyan
Write-Host ""

# Check if virtual environment exists
if (-Not (Test-Path ".\AIDA\Scripts\Activate.ps1")) {
    Write-Host "❌ Virtual environment not found at .\AIDA\Scripts\" -ForegroundColor Red
    Write-Host "Please create virtual environment first:" -ForegroundColor Yellow
    Write-Host "  python -m venv AIDA" -ForegroundColor Yellow
    exit 1
}

# Activate virtual environment
Write-Host "📦 Activating virtual environment..." -ForegroundColor Green
& .\AIDA\Scripts\Activate.ps1

# Check if aida.py exists
if (-Not (Test-Path ".\aida.py")) {
    Write-Host "❌ aida.py not found in current directory" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Virtual environment activated" -ForegroundColor Green
Write-Host ""
Write-Host "🌐 Starting Flask server..." -ForegroundColor Cyan
Write-Host "   Access the application at: http://localhost:5000" -ForegroundColor Yellow
Write-Host ""
Write-Host "💡 Tips:" -ForegroundColor Magenta
Write-Host "   - Main UI: http://localhost:5000" -ForegroundColor White
Write-Host "   - Agent Space: http://localhost:5000/agent_space.html" -ForegroundColor White
Write-Host "   - Press Ctrl+C to stop the server" -ForegroundColor White
Write-Host ""

# Start the application
python .\aida.py
