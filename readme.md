# 🌟 FocusAI Tracker

A comprehensive Windows desktop application that helps users understand and improve their computer usage habits through AI-powered insights, productivity tracking, and intelligent parental controls.

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Installation](#installation)
- [Development Setup](#development-setup)
- [Usage](#usage)
- [API Integration](#api-integration)
- [Contributing](#contributing)
- [License](#license)

## 🎯 Overview

FocusAI Tracker combines the power of AI with comprehensive activity monitoring to provide users with actionable insights about their computer usage. Whether you're a professional looking to boost productivity or a parent wanting to ensure safe computer use for your children, FocusAI Tracker has you covered.

### Key Benefits
- **📊 Deep Insights**: Understand exactly how you spend time on your PC
- **🤖 AI-Powered**: Get personalized recommendations for improvement
- **👨‍👩‍👧‍👦 Family-Friendly**: Comprehensive parental controls with Kids Mode
- **🔒 Privacy-First**: All data stored locally with encryption
- **📈 Productivity Focus**: Reduce distractions and maximize focus time

## ✨ Features

### 🎯 Core Tracking Features
- **Real-time Activity Monitoring**: Track active windows, applications, and usage duration
- **AI Activity Classification**: Automatically categorize activities as Productive, Neutral, or Distracting
- **Screenshot Capture**: Periodic screenshots with configurable intervals and retention
- **Idle Time Detection**: Accurate tracking of active vs. idle computer usage
- **Focus Mode**: Block or warn about distracting applications during work sessions

### 📊 Reporting & Analytics
- **Interactive Dashboard**: Visual summaries of daily, weekly, and monthly usage
- **Trend Analysis**: Identify patterns and changes in computer usage over time
- **Export Capabilities**: Generate PDF and Excel reports for deeper analysis
- **Custom Categories**: Create and manage personalized activity categories

### 🤖 AI-Powered Insights
- **Smart Recommendations**: Daily, weekly, and monthly improvement suggestions
- **Usage Pattern Analysis**: Identify productivity peaks and distraction triggers
- **Goal Setting**: AI-assisted productivity goal creation and tracking
- **Habit Formation**: Personalized strategies for building better computer habits

### 👶 Kids Mode (Parental Control)
- **Smart Content Filtering**: AI-powered detection of inappropriate content
- **Screen Time Management**: Configurable daily and weekly time limits
- **Schedule Control**: Set allowed computer usage hours
- **Educational Focus**: Promote educational app usage with intelligent recommendations
- **Safety Alerts**: Real-time notifications for inappropriate activity detection
- **Parent Dashboard**: Comprehensive oversight of child's computer usage

## 🏗️ Architecture

FocusAI Tracker uses a hybrid architecture combining a Python Flask backend with a React/Electron frontend for optimal performance and user experience.

### Technology Stack

**Frontend:**
- **Electron**: Desktop application shell
- **React**: Component-based UI library (TypeScript)
- **Tailwind CSS**: Utility-first CSS framework
- **Chart.js** & **react-chartjs-2**: Data visualization
- **Lucide-react**, **date-fns**, **axios**, **@headlessui/react**

**Backend:**
- **Python 3.9+**: Core application logic
- **Flask**: RESTful API framework
- **Flask-SQLAlchemy**: ORM for database
- **Flask-Migrate**: Database migrations
- **Flask-CORS**: CORS support
- **Flask-RESTful**: API structure
- **SQLite**: Local database
- **Cryptography**: Data encryption
- **psutil**, **pywin32**, **pillow**, **schedule**, **requests**

**AI/ML Integration (Planned/Optional):**
- **Google Gemini Flash API**: Advanced activity classification and advice generation (planned)
- **TensorFlow Lite**, **scikit-learn**: Optional for local ML models (future)

### Project Structure
```
FocusAI-Tracker/
├── backend/
│   ├── app/
│   │   ├── api/              # Flask API routes (activity, dashboard, settings, kids_mode, etc.)
│   │   ├── core/             # Core config and logic
│   │   ├── models/           # Database models
│   │   ├── services/         # Business services
│   │   ├── tracking/         # Activity tracking modules
│   │   └── utils/            # Utility functions
│   ├── ai/                   # (Planned) AI/ML modules
│   ├── scripts/              # Utility scripts
│   ├── tests/                # Backend tests
│   ├── instance/             # Flask instance folder
│   ├── tracking/             # (Legacy/extra tracking modules)
│   ├── requirements.txt
│   ├── requirements-dev.txt
│   └── run.py                # Backend entrypoint
├── frontend/
│   ├── src/
│   │   ├── components/       # React components
│   │   ├── pages/            # Application pages
│   │   ├── services/         # API communication
│   │   ├── utils/            # Frontend utilities
│   │   ├── assets/           # Static assets
│   │   ├── styles/           # Tailwind and custom CSS
│   │   ├── contexts/         # React contexts
│   │   ├── hooks/            # Custom hooks
│   │   └── layouts/          # Layout components
│   ├── public/               # Static files for Electron/React
│   ├── app/                  # (If used for Electron preload)
│   ├── main.js               # Electron main process
│   ├── package.json
│   ├── tailwind.config.js
│   ├── tsconfig.json
│   └── postcss.config.js
├── shared/
│   ├── config/               # Shared configuration
│   └── schemas/              # Shared data schemas
├── docs/                     # Documentation
├── template/                 # (If used for templates)
├── docker-compose.yml        # (If used for deployment)
├── LICENSE
├── .gitignore
└── readme.md
```

## 🚀 Installation

### Prerequisites
- **Windows 10/11** (64-bit)
- **Python 3.9+**
- **Node.js 16+**
- **npm**

### Quick Install (End Users)
1. Download the latest release from [Releases](https://github.com/yourusername/focusai-tracker/releases)
2. Run the installer (`FocusAI-Tracker-Setup.exe`)
3. Follow the installation wizard
4. Launch FocusAI Tracker from Start Menu or Desktop

### Manual Installation
```bash
# Clone the repository
git clone https://github.com/yourusername/focusai-tracker.git
cd focusai-tracker

# Install Python dependencies
cd backend
pip install -r requirements.txt

# Install Node.js dependencies
cd ../frontend
npm install

# Build the frontend (for production)
npm run build
```

## 💻 Development Setup

### 1. Environment Setup
```bash
# Clone the repository
git clone https://github.com/yourusername/focusai-tracker.git
cd focusai-tracker

# Create Python virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Install backend dependencies
cd backend
pip install -r requirements.txt
pip install -r requirements-dev.txt  # Development dependencies

# Install frontend dependencies
cd ../frontend
npm install
```

### 2. Configuration
```bash
# Copy environment template (if available)
cp .env.example .env

# Edit .env with your settings (see backend/app/core/config.py for options)
# DATABASE_URL=sqlite:///focusai.db
# GEMINI_API_KEY=your_gemini_api_key_here
# DEBUG=true
# SECRET_KEY=your-secret-key
```

### 3. Development Servers
```bash
# Terminal 1: Start Python backend (Flask)
cd backend
python run.py

# Terminal 2: Start React frontend (for web)
cd frontend
npm start

# Terminal 3: Start Electron desktop app (after React dev server is running)
cd frontend
npm run electron-dev
```

### 4. Database Setup
- The database is auto-created on first run (SQLite by default).
- For migrations, use Flask-Migrate (see scripts or docs for details).

## 📖 Usage

### First-Time Setup
1. **Launch Application**: Open FocusAI Tracker from your desktop or start menu
2. **Initial Configuration**: Set up basic preferences and screenshot settings
3. **AI Setup**: Optionally configure Gemini API key for advanced features (future)
4. **Kids Mode**: Enable and configure parental controls if needed

### Daily Usage
- **Automatic Tracking**: The app runs in the background, tracking your activity
- **Review Dashboard**: Check daily progress and AI recommendations
- **Focus Sessions**: Use Focus Mode to block distractions during work
- **Weekly Reviews**: Analyze trends and adjust productivity strategies

### Kids Mode Setup
1. **Enable Kids Mode**: Navigate to Settings > Kids Mode
2. **Set PIN**: Create a secure PIN for parental access
3. **Configure Limits**: Set daily screen time and allowed hours
4. **Content Filtering**: Adjust AI sensitivity for content detection
5. **Monitor Progress**: Review child's usage through parent dashboard

## 🔗 API Integration

### Gemini Flash API Setup (Planned)
```python
# Configuration in .env file
GEMINI_API_KEY=your_api_key_here
GEMINI_MODEL=gemini-flash

# Usage in code (planned)
# from app.services.ai_service import AIService
# ai_service = AIService()
# advice = ai_service.generate_daily_advice(user_activity_data)
```

### Custom AI Models (Planned)
```python
# Add custom classification models (future)
# from app.ai.custom_classifier import CustomClassifier
# classifier = CustomClassifier()
# classifier.train(training_data)
# activity_type = classifier.classify(window_title, app_name)
```

## 🤝 Contributing

We welcome contributions from the community! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

### Development Workflow
1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

### Code Standards
- **Python**: Follow PEP 8 guidelines, use type hints
- **JavaScript/TypeScript**: Use ESLint and Prettier for code formatting
- **Testing**: Write unit tests for new features
- **Documentation**: Update documentation for API changes

## 🛡️ Privacy & Security

- **Local Storage**: All data stored locally with AES-256 encryption
- **Minimal API Calls**: Only essential data sent to external services
- **Opt-in Features**: All cloud features require explicit user consent
- **Screen Capture**: Screenshots encrypted and auto-deleted per user settings
- **Kids Mode**: PIN-protected with secure session management

## 📊 Roadmap

### Version 1.0 (Current)
- [x] Basic activity tracking
- [x] AI classification (basic)
- [x] Simple reporting
- [x] Kids Mode foundation

### Version 1.1 (Next Release)
- [ ] Advanced AI recommendations
- [ ] Browser extension integration
- [ ] Productivity gamification
- [ ] Enhanced Kids Mode features

### Version 2.0 (Future)
- [ ] Multi-device synchronization
- [ ] Team collaboration features
- [ ] Advanced machine learning models
- [ ] Mobile companion app

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Google Gemini**: AI-powered insights and recommendations (planned)
- **Electron Community**: Cross-platform desktop application framework
- **Python Community**: Robust backend development ecosystem
- **Contributors**: All developers who help improve FocusAI Tracker

## 📞 Support

- **Documentation**: [Wiki](https://github.com/yourusername/focusai-tracker/wiki)
- **Issues**: [GitHub Issues](https://github.com/yourusername/focusai-tracker/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/focusai-tracker/discussions)
- **Email**: support@focusai-tracker.com

---

**Made with ❤️ by [Your Name]**

*Empowering productivity through intelligent computer usage insights*