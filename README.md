# Face Analysis Studio 🎬

A modern, AI-powered face detection and emotion analysis tool with a beautiful React frontend. Identify specific individuals in photos, analyze their emotions, and generate stunning videos with audio.

## ✨ Features

- **🤖 Advanced AI Detection**: RetinaFace + DeepFace for accurate face detection and emotion analysis
- **👤 Person Tracking**: Upload reference photos to track specific individuals across multiple images
- **🎭 Emotion Analysis**: Real-time emotion detection with confidence scores
- **🎥 Video Generation**: Create beautiful HD videos with generated audio
- **⚛️ Modern React UI**: Sleek, responsive interface with drag-and-drop uploads
- **🎵 Audio Integration**: Automatically generated ambient audio for videos
- **📱 Mobile Friendly**: Works perfectly on desktop and mobile devices
- **🚀 Real-time Preview**: Preview videos before downloading

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- npm or yarn

### Installation

1. **Clone the repository:**
```bash
git clone https://github.com/akshaychikhalkar/face-mood-analyzer.git
cd face-mood-analyzer
```

2. **Install Python dependencies:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. **Install Node.js dependencies:**
```bash
npm install
```

4. **Start the development servers:**
```bash
python run_dev.py
```

This will start both the Flask backend (port 5000) and React frontend (port 3000).

### Alternative: Manual Start

**Terminal 1 - Backend:**
```bash
python app.py
```

**Terminal 2 - Frontend:**
```bash
npm run dev
```

## 🎯 How to Use

1. **Upload Reference Photos** 📸
   - Drag and drop clear photos of the person you want to track
   - Multiple reference photos improve accuracy

2. **Upload Photos to Analyze** 🔍
   - Add photos where you want to find and analyze the person
   - Supports batch upload of multiple images

3. **Start Analysis** 🧠
   - Click "Start Analysis" to begin AI processing
   - The system will detect faces and analyze emotions

4. **Preview & Download** 🎬
   - Preview the generated video with audio
   - Download marked photos or the complete video

## 🏗️ Project Structure

```
face-analysis-studio/
├── 🐍 Backend (Flask)
│   ├── app.py                 # Main Flask application
│   ├── emotion_analyzer.py    # AI analysis engine
│   ├── music_generator.py     # Audio generation
│   └── requirements.txt       # Python dependencies
├── ⚛️ Frontend (React)
│   ├── src/
│   │   ├── components/        # React components
│   │   ├── App.jsx           # Main React app
│   │   └── main.jsx          # Entry point
│   ├── package.json          # Node dependencies
│   └── vite.config.js        # Vite configuration
├── 📁 Data Directories
│   └── uploads/
│       ├── reference/        # Reference photos
│       ├── photos/          # Photos to analyze
│       └── output/          # Results & videos
└── 🛠️ Configuration
    ├── tailwind.config.js    # Tailwind CSS config
    └── run_dev.py           # Development server runner
```

## 🔧 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/upload_reference` | Upload reference photos |
| `POST` | `/upload_photos` | Upload photos to analyze |
| `POST` | `/analyze` | Start AI analysis |
| `POST` | `/generate_video` | Generate video with audio |
| `GET` | `/preview_video/<filename>` | Stream video for preview |
| `GET` | `/download/<filename>` | Download results |
| `POST` | `/clear` | Clear uploaded data |

## 🎨 UI Features

- **Glassmorphism Design**: Modern glass-effect UI elements
- **Drag & Drop**: Intuitive file upload experience
- **Real-time Feedback**: Live progress indicators and status updates
- **Responsive Layout**: Works on all screen sizes
- **Dark Mode Ready**: Prepared for dark theme implementation
- **Smooth Animations**: Polished transitions and micro-interactions

## 🔧 Technical Stack

### Backend
- **Flask**: Web framework
- **DeepFace**: Face recognition and emotion analysis
- **RetinaFace**: Advanced face detection
- **OpenCV**: Image processing
- **MoviePy**: Video generation
- **SciPy**: Audio generation

### Frontend
- **React 18**: Modern React with hooks
- **Vite**: Fast build tool and dev server
- **Tailwind CSS**: Utility-first CSS framework
- **Lucide React**: Beautiful icons
- **React Dropzone**: File upload component
- **Axios**: HTTP client
- **React Hot Toast**: Elegant notifications

## 🎵 Audio Features

The system automatically generates ambient audio for videos based on:
- **Emotion Analysis**: Audio tone matches detected emotions
- **Duration Matching**: Audio perfectly syncs with video length
- **Fade Effects**: Smooth fade-in and fade-out
- **Multiple Frequencies**: Rich harmonic content

## 🚀 Performance Optimizations

- **Batch Processing**: Efficient handling of multiple images
- **Caching**: LRU cache for face detection results
- **Streaming**: Video streaming for instant preview
- **Lazy Loading**: Components load as needed
- **Error Boundaries**: Graceful error handling

## 📱 Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👨‍💻 Author

**Akshay Chikhalkar**
- GitHub: [@akshaychikhalkar](https://github.com/akshaychikhalkar)

## 🙏 Acknowledgments

- DeepFace team for the amazing face analysis library
- RetinaFace for robust face detection
- React team for the excellent frontend framework
- Tailwind CSS for the beautiful styling system

---

<div align="center">
  <p>Made with ❤️ and AI</p>
  <p>⭐ Star this repo if you found it helpful!</p>
</div>