@echo off
echo 🎬 Face Analysis Studio - Development Server
echo ==================================================

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found! Please install Python 3.8+
    pause
    exit /b 1
)

REM Check if npm is available
npm --version >nul 2>&1
if errorlevel 1 (
    echo ❌ npm not found! Please install Node.js
    pause
    exit /b 1
)

REM Install Python dependencies if needed
if not exist "venv" (
    echo 📦 Creating virtual environment...
    python -m venv venv
)

echo 🔧 Activating virtual environment...
call venv\Scripts\activate.bat

echo 📦 Installing Python dependencies...
pip install -r requirements.txt

REM Install npm dependencies if needed
if not exist "node_modules" (
    echo 📦 Installing npm dependencies...
    npm install
)

echo 🚀 Starting development servers...
echo 📍 Flask backend will run on: http://localhost:5000
echo 📍 React frontend will run on: http://localhost:3000
echo.
echo 💡 Use Ctrl+C to stop both servers
echo --------------------------------------------------

REM Start Flask backend in background
start "Flask Backend" cmd /c "python app.py"

REM Wait a moment for Flask to start
timeout /t 3 /nobreak >nul

REM Start React frontend
echo ⚛️  Starting React frontend server...
npm run dev

pause