# 🚀 FocusAI Tracker - Initial Setup Guide

Let's get your development environment up and running step by step.

## 📁 Step 1: Create Project Structure

First, let's create the complete project directory structure:

```bash
# Create main project directory
mkdir focusai-tracker
cd focusai-tracker

# Create backend structure
mkdir -p backend/app/{api,core,models,services,utils}
mkdir -p backend/{tracking,ai,scripts,tests}

# Create frontend structure
mkdir -p frontend/src/{components,pages,services,utils,assets}
mkdir -p frontend/public

# Create shared and docs directories
mkdir -p shared/{config,schemas}
mkdir -p docs

# Create root configuration files
touch .env.example
touch .gitignore
touch docker-compose.yml
```

## 🐍 Step 2: Backend Setup (Python)

### Create Backend Files:

**backend/requirements.txt**
```txt
flask==3.0.0
flask-sqlalchemy==3.1.1
flask-migrate==4.0.5
flask-cors==4.0.0
flask-restful==0.3.10
sqlalchemy==2.0.23
psutil==5.9.6
pillow==10.1.0
cryptography==41.0.7
python-dotenv==1.0.0
requests==2.31.0
schedule==1.2.0
threading==0.0.1
pywin32==306; sys_platform == "win32"
```

**backend/requirements-dev.txt**
```txt
pytest==7.4.3
pytest-asyncio==0.21.1
black==23.11.0
flake8==6.1.0
mypy==1.7.1
pre-commit==3.5.0
```

**backend/app/__init__.py**
```python
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from app.core.config import Config

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    
    # Enable CORS for Electron frontend
    CORS(app, origins=["http://localhost:3000", "file://"])
    
    # Register blueprints
    from app.api.activity import bp as activity_bp
    from app.api.dashboard import bp as dashboard_bp
    from app.api.settings import bp as settings_bp
    from app.api.kids_mode import bp as kids_bp
    
    app.register_blueprint(activity_bp, url_prefix='/api/activity')
    app.register_blueprint(dashboard_bp, url_prefix='/api/dashboard')
    app.register_blueprint(settings_bp, url_prefix='/api/settings')
    app.register_blueprint(kids_bp, url_prefix='/api/kids')
    
    # Basic routes
    @app.route('/')
    def index():
        return {"message": "FocusAI Tracker API is running!"}
    
    @app.route('/health')
    def health():
        return {"status": "healthy", "version": "1.0.0"}
    
    return app
```

**backend/run.py**
```python
from app import create_app, db
from app.tracking.monitor import ActivityMonitor
import threading
import time

app = create_app()

def start_activity_monitoring():
    """Start the activity monitoring in a separate thread"""
    monitor = ActivityMonitor()
    monitor.start_monitoring()

if __name__ == '__main__':
    # Create database tables
    with app.app_context():
        db.create_all()
    
    # Start activity monitoring in background thread
    monitor_thread = threading.Thread(target=start_activity_monitoring, daemon=True)
    monitor_thread.start()
    
    # Start Flask app
    app.run(debug=True, host='0.0.0.0', port=8000)
```

**backend/app/core/config.py**
```python
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Database
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///focusai.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # API Keys
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    
    # App Settings
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    SCREENSHOT_INTERVAL = int(os.getenv('SCREENSHOT_INTERVAL', 300))  # 5 minutes
    SCREENSHOT_RETENTION_DAYS = int(os.getenv('SCREENSHOT_RETENTION_DAYS', 7))
    
    # Security
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-change-this')
    
    # Paths
    DATA_DIR = os.path.join(os.path.expanduser('~'), 'FocusAI')
    SCREENSHOTS_DIR = os.path.join(DATA_DIR, 'screenshots')
    LOGS_DIR = os.path.join(DATA_DIR, 'logs')
```

## ⚛️ Step 3: Frontend Setup (Electron + React)

### Create Frontend Files:

**frontend/package.json**
```json
{
  "name": "focusai-tracker-frontend",
  "version": "1.0.0",
  "description": "FocusAI Tracker Desktop Application",
  "main": "public/electron.js",
  "scripts": {
    "start": "react-scripts start",
    "build": "react-scripts build",
    "electron": "electron .",
    "electron-dev": "concurrently \"npm start\" \"wait-on http://localhost:3000 && electron .\"",
    "dist": "npm run build && electron-builder",
    "pack": "electron-builder --dir"
  },
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.8.0",
    "axios": "^1.6.0",
    "chart.js": "^4.4.0",
    "react-chartjs-2": "^5.2.0",
    "lucide-react": "^0.294.0",
    "date-fns": "^2.30.0",
    "@headlessui/react": "^1.7.17"
  },
  "devDependencies": {
    "react-scripts": "5.0.1",
    "electron": "^27.1.0",
    "electron-builder": "^24.6.4",
    "concurrently": "^8.2.2",
    "wait-on": "^7.2.0",
    "tailwindcss": "^3.3.6",
    "autoprefixer": "^10.4.16",
    "postcss": "^8.4.32"
  },
  "homepage": "./",
  "browserslist": {
    "production": [
      ">0.2%",
      "not dead",
      "not op_mini all"
    ],
    "development": [
      "last 1 chrome version",
      "last 1 firefox version",
      "last 1 safari version"
    ]
  }
}
```

**frontend/public/electron.js**
```javascript
const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');
const isDev = require('electron-is-dev');

let mainWindow;

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false,
      enableRemoteModule: true,
    },
    icon: path.join(__dirname, 'icon.png'),
    show: false,
  });

  mainWindow.loadURL(
    isDev
      ? 'http://localhost:3000'
      : `file://${path.join(__dirname, '..', 'build', 'index.html')}`
  );

  mainWindow.once('ready-to-show', () => {
    mainWindow.show();
  });

  if (isDev) {
    mainWindow.webContents.openDevTools();
  }

  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

app.whenReady().then(createWindow);

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    createWindow();
  }
});
```

## 🔧 Step 4: Configuration Files

**.env.example**
```env
# Database
DATABASE_URL=sqlite:///./focusai.db

# API Keys
GEMINI_API_KEY=your_gemini_api_key_here

# App Settings
DEBUG=true
SCREENSHOT_INTERVAL=300
SCREENSHOT_RETENTION_DAYS=7

# Security
SECRET_KEY=your-super-secret-key-change-this-in-production
```

**.gitignore**
```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual Environment
venv/
env/
ENV/

# Database
*.db
*.sqlite3

# Environment variables
.env

# Node.js
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# React
build/
.DS_Store
.env.local
.env.development.local
.env.test.local
.env.production.local

# Electron
dist/
out/

# IDE
.vscode/
.idea/
*.swp
*.swo

# Screenshots and logs
screenshots/
logs/
*.log
```

## 🏃‍♂️ Step 5: Initial Setup Commands

Run these commands in order:

```bash
# 1. Create virtual environment for Python
python -m venv venv

# 2. Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
# source venv/bin/activate

# 3. Install Python dependencies
cd backend
pip install -r requirements.txt
pip install -r requirements-dev.txt

# 4. Install Node.js dependencies
cd ../frontend
npm install

# 5. Create environment file
cd ..
cp .env.example .env
# Edit .env file with your settings

# 6. Initialize git repository
git init
git add .
git commit -m "Initial project setup"
```

## 🧪 Step 6: Test the Setup

### Test Backend:
```bash
cd backend
python run.py
# Should see: "Running on http://0.0.0.0:8000" and activity monitoring starting
```

### Test Frontend:
```bash
cd frontend
npm start
# Should open React app in browser at http://localhost:3000
```

### Test Electron:
```bash
cd frontend
npm run electron-dev
# Should open Electron window with React app
```

## 🎯 Next Steps

Once the setup is complete, we'll implement:

1. **Activity Tracking Module** - Monitor windows and applications  
2. **Basic Dashboard** - Display tracked data
3. **Database Models** - SQLAlchemy models for data storage
4. **AI Classification** - Basic activity categorization
5. **Screenshots** - Periodic screen capture functionality

Ready to proceed? Let me know if you encounter any issues with the setup!