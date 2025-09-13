#!/usr/bin/env python3
"""
Development server runner for Face Analysis Studio
Runs both Flask backend and React frontend
"""

import subprocess
import sys
import os
import time
import threading
from pathlib import Path
import signal

# Global variables to track processes
flask_process = None
react_process = None

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    print("\n🛑 Shutting down development servers...")
    
    if flask_process:
        flask_process.terminate()
        print("✅ Flask server stopped")
    
    if react_process:
        react_process.terminate()
        print("✅ React server stopped")
    
    print("✅ Development servers stopped")
    sys.exit(0)

def run_flask():
    """Run Flask backend server"""
    global flask_process
    print("🚀 Starting Flask backend server...")
    try:
        flask_process = subprocess.Popen([sys.executable, "app.py"])
        flask_process.wait()
    except Exception as e:
        print(f"❌ Flask server error: {e}")

def run_react():
    """Run React frontend development server"""
    global react_process
    print("⚛️  Starting React frontend server...")
    try:
        # Check if node_modules exists
        if not Path("node_modules").exists():
            print("📦 Installing npm dependencies...")
            subprocess.run(["npm", "install"], check=True)
        
        # Check if we're on Windows
        npm_cmd = "npm.cmd" if os.name == 'nt' else "npm"
        react_process = subprocess.Popen([npm_cmd, "run", "dev"])
        react_process.wait()
    except Exception as e:
        print(f"❌ React server error: {e}")

def check_dependencies():
    """Check if required dependencies are available"""
    try:
        # Check Python dependencies
        import flask
        import flask_cors
        print("✅ Python dependencies found")
    except ImportError as e:
        print(f"❌ Missing Python dependency: {e}")
        print("💡 Run: pip install -r requirements.txt")
        return False
    
    try:
        # Check if npm is available
        subprocess.run(["npm", "--version"], capture_output=True, check=True)
        print("✅ npm found")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ npm not found! Please install Node.js")
        return False
    
    return True

def main():
    print("🎬 Face Analysis Studio - Development Server")
    print("=" * 50)
    
    # Set up signal handler for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    
    # Check if we have the required files
    if not Path("app.py").exists():
        print("❌ app.py not found!")
        return
    
    if not Path("package.json").exists():
        print("❌ package.json not found!")
        return
    
    # Check dependencies
    if not check_dependencies():
        return
    
    print("🔧 Starting development servers...")
    print("📍 Flask backend will run on: http://localhost:5000")
    print("📍 React frontend will run on: http://localhost:3000")
    print("\n💡 Use Ctrl+C to stop both servers")
    print("-" * 50)
    
    # Start Flask in a separate thread
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    
    # Give Flask a moment to start
    time.sleep(3)
    
    # Start React (this will block until Ctrl+C)
    try:
        run_react()
    except KeyboardInterrupt:
        signal_handler(signal.SIGINT, None)

if __name__ == "__main__":
    main()