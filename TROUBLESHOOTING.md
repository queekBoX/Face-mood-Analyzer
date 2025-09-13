# Troubleshooting Guide

## Common Issues and Solutions

### React Server Issues

#### 1. "Module not found" errors
```bash
# Delete node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

#### 2. Port already in use
```bash
# Kill processes on ports 3000 and 5000
# On Windows:
netstat -ano | findstr :3000
taskkill /PID <PID> /F

# On Mac/Linux:
lsof -ti:3000 | xargs kill -9
lsof -ti:5000 | xargs kill -9
```

#### 3. Vite build errors
```bash
# Clear Vite cache
rm -rf node_modules/.vite
npm run dev
```

### Python/Flask Issues

#### 1. Import errors
```bash
# Reinstall Python dependencies
pip install -r requirements.txt --force-reinstall
```

#### 2. Audio generation fails
```bash
# Install scipy separately
pip install scipy==1.11.1
```

#### 3. Video generation issues
```bash
# Install OpenCV with full features
pip uninstall opencv-python-headless
pip install opencv-python
```

### Audio Issues

#### 1. No audio in generated videos
- Check if scipy is installed: `pip show scipy`
- Ensure MoviePy is working: `pip install moviepy --upgrade`
- Check system audio codecs

#### 2. Audio quality issues
- The system generates emotion-based ambient music
- Longer videos (30+ seconds) have better audio quality
- Audio fades in/out for professional quality

### General Issues

#### 1. CORS errors
- Make sure Flask server is running on port 5000
- Check that flask-cors is installed
- Restart both servers

#### 2. File upload issues
- Check upload folder permissions
- Ensure supported file formats: JPG, JPEG, PNG, BMP
- Maximum file size depends on your system

#### 3. Analysis takes too long
- Reduce batch size in emotion_analyzer.py
- Use fewer reference photos
- Ensure GPU acceleration if available

## Performance Tips

1. **Use clear reference photos** - Better quality = faster processing
2. **Limit photo batch size** - Process 10-20 photos at a time
3. **Close other applications** - Free up system resources
4. **Use SSD storage** - Faster file I/O operations

## Getting Help

If you're still having issues:

1. Check the console logs in both terminal windows
2. Look for error messages in the browser developer tools
3. Ensure all dependencies are correctly installed
4. Try restarting both servers

## System Requirements

- **Python**: 3.8 or higher
- **Node.js**: 16 or higher
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 2GB free space for dependencies
- **OS**: Windows 10+, macOS 10.15+, or Linux

## Quick Reset

If everything is broken, try this complete reset:

```bash
# Stop all servers
# Delete all generated files
rm -rf node_modules venv uploads/photos/* uploads/reference/* uploads/output/*

# Reinstall everything
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
npm install

# Start fresh
python run_dev.py
```