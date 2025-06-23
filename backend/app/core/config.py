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