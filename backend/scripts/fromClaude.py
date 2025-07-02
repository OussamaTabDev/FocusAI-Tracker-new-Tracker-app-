# run.py
from app import create_app, socketio

app = create_app()

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)

# ==========================================
# config.py
import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'focusai-tracker-secret-key-2024'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///focusai_tracker.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # WebSocket settings
    SOCKETIO_ASYNC_MODE = 'threading'
    
    # Tracking intervals
    TRACKING_INTERVAL = 5  # seconds
    ANALYSIS_INTERVAL = 300  # 5 minutes
    
    # Session settings
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    
    # CORS settings
    CORS_ORIGINS = ['http://localhost:3000', 'http://localhost:8080']

# ==========================================
# app/__init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO
from flask_cors import CORS
from flask_migrate import Migrate
import logging
from logging.handlers import RotatingFileHandler
import os

# Initialize extensions
db = SQLAlchemy()
socketio = SocketIO()
migrate = Migrate()

def create_app(config_name='Config'):
    app = Flask(__name__)
    app.config.from_object(f'config.{config_name}')
    
    # Initialize extensions
    db.init_app(app)
    socketio.init_app(app, cors_allowed_origins="*", async_mode='threading')
    CORS(app, origins=app.config['CORS_ORIGINS'])
    migrate.init_app(app, db)
    
    # Configure logging
    if not app.debug and not app.testing:
        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = RotatingFileHandler('logs/focusai.log', maxBytes=10240, backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('FocusAI Tracker startup')
    
    # Register blueprints
    from backend.app.api.activtiy.activity import activity_bp
    from app.api.dashboard import dashboard_bp
    from app.api.settings import settings_bp
    from app.api.web_tracking import web_bp
    from app.api.analytics import analytics_bp
    
    app.register_blueprint(activity_bp, url_prefix='/api/activity')
    app.register_blueprint(dashboard_bp, url_prefix='/api/dashboard')
    app.register_blueprint(settings_bp, url_prefix='/api/settings')
    app.register_blueprint(web_bp, url_prefix='/api/web')
    app.register_blueprint(analytics_bp, url_prefix='/api/analytics')
    
    # Create tables
    with app.app_context():
        db.create_all()
    
    return app

# ==========================================
# app/models/activity.py
from app import db
from datetime import datetime
from sqlalchemy.dialects.sqlite import JSON

class ActivitySession(db.Model):
    __tablename__ = 'activity_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(36), unique=True, nullable=False)
    start_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    end_time = db.Column(db.DateTime)
    total_duration = db.Column(db.Integer, default=0)  # in seconds
    productivity_score = db.Column(db.Float, default=0.0)
    focus_score = db.Column(db.Float, default=0.0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    activities = db.relationship('Activity', backref='session', lazy=True, cascade='all, delete-orphan')

class Activity(db.Model):
    __tablename__ = 'activities'
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(36), db.ForeignKey('activity_sessions.session_id'), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # Application data
    app_name = db.Column(db.String(255), nullable=False)
    process_name = db.Column(db.String(255))
    window_title = db.Column(db.Text)
    
    # Activity classification
    category = db.Column(db.String(50))  # productive, social, entertainment, etc.
    subcategory = db.Column(db.String(50))
    productivity_score = db.Column(db.Float, default=0.0)
    
    # Technical details
    duration = db.Column(db.Integer, default=5)  # tracking interval
    idle_time = db.Column(db.Integer, default=0)
    mouse_clicks = db.Column(db.Integer, default=0)
    key_presses = db.Column(db.Integer, default=0)
    
    # Window properties
    window_data = db.Column(JSON)  # position, size, is_maximized, etc.
    
    # Web tracking (if applicable)
    url = db.Column(db.Text)
    domain = db.Column(db.String(255))
    page_title = db.Column(db.Text)
    
    def to_dict(self):
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat(),
            'app_name': self.app_name,
            'process_name': self.process_name,
            'window_title': self.window_title,
            'category': self.category,
            'productivity_score': self.productivity_score,
            'duration': self.duration,
            'url': self.url,
            'domain': self.domain
        }

class WebActivity(db.Model):
    __tablename__ = 'web_activities'
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(36), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # Web-specific data
    url = db.Column(db.Text, nullable=False)
    domain = db.Column(db.String(255), nullable=False)
    page_title = db.Column(db.Text)
    browser = db.Column(db.String(50))
    
    # Time tracking
    time_spent = db.Column(db.Integer, default=0)  # seconds
    tab_switches = db.Column(db.Integer, default=0)
    scroll_depth = db.Column(db.Float, default=0.0)
    
    # Classification
    category = db.Column(db.String(50))
    productivity_score = db.Column(db.Float, default=0.0)
    is_productive = db.Column(db.Boolean, default=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat(),
            'url': self.url,
            'domain': self.domain,
            'page_title': self.page_title,
            'browser': self.browser,
            'time_spent': self.time_spent,
            'category': self.category,
            'productivity_score': self.productivity_score
        }

# ==========================================
# app/services/activity_tracker.py
import threading
import time
import uuid
from datetime import datetime, timedelta
import pygetwindow as gw
import psutil
from pynput import mouse, keyboard
from app import db
from app.models.activity import ActivitySession, Activity
from app.utils.categorizer import AppCategorizer
import logging

class ActivityTracker:
    def __init__(self):
        self.tracking = False
        self.track_thread = None
        self.current_session = None
        self.last_activity_time = datetime.utcnow()
        self.idle_threshold = 300  # 5 minutes
        
        # Activity counters
        self.mouse_clicks = 0
        self.key_presses = 0
        
        # Categorizer
        self.categorizer = AppCategorizer()
        
        # Setup input listeners
        self.mouse_listener = None
        self.keyboard_listener = None
        
        self.logger = logging.getLogger(__name__)
    
    def start_tracking(self):
        """Start activity tracking"""
        if self.tracking:
            return {"status": "already_tracking"}
        
        self.tracking = True
        self.current_session = self._create_new_session()
        
        # Start tracking thread
        self.track_thread = threading.Thread(target=self._track_loop, daemon=True)
        self.track_thread.start()
        
        # Start input listeners
        self._start_input_listeners()
        
        self.logger.info(f"Activity tracking started. Session: {self.current_session.session_id}")
        return {"status": "tracking_started", "session_id": self.current_session.session_id}
    
    def stop_tracking(self):
        """Stop activity tracking"""
        if not self.tracking:
            return {"status": "not_tracking"}
        
        self.tracking = False
        
        # Stop input listeners
        self._stop_input_listeners()
        
        # Finalize current session
        if self.current_session:
            self._finalize_session()
        
        # Wait for thread to finish
        if self.track_thread and self.track_thread.is_alive():
            self.track_thread.join(timeout=5)
        
        self.logger.info("Activity tracking stopped")
        return {"status": "tracking_stopped"}
    
    def _create_new_session(self):
        """Create a new activity session"""
        session = ActivitySession(
            session_id=str(uuid.uuid4()),
            start_time=datetime.utcnow(),
            is_active=True
        )
        db.session.add(session)
        db.session.commit()
        return session
    
    def _track_loop(self):
        """Main tracking loop"""
        while self.tracking:
            try:
                # Check if user is idle
                if self._is_user_idle():
                    time.sleep(10)  # Check less frequently when idle
                    continue
                
                # Capture current activity
                activity_data = self._capture_current_activity()
                
                if activity_data:
                    # Store activity
                    self._store_activity(activity_data)
                    
                    # Reset counters
                    self.mouse_clicks = 0
                    self.key_presses = 0
                
                # Update last activity time
                self.last_activity_time = datetime.utcnow()
                
                # Sleep for tracking interval
                time.sleep(5)  # Track every 5 seconds
                
            except Exception as e:
                self.logger.error(f"Error in tracking loop: {e}")
                time.sleep(5)
    
    def _capture_current_activity(self):
        """Capture current activity data"""
        try:
            # Get active window
            active_window = gw.getActiveWindow()
            if not active_window:
                return None
            
            # Get process info
            process_info = self._get_process_info(active_window)
            
            # Categorize activity
            category_data = self.categorizer.categorize_activity(
                process_info['process_name'],
                active_window.title
            )
            
            activity_data = {
                'app_name': process_info['app_name'],
                'process_name': process_info['process_name'],
                'window_title': active_window.title,
                'category': category_data['category'],
                'subcategory': category_data['subcategory'],
                'productivity_score': category_data['productivity_score'],
                'mouse_clicks': self.mouse_clicks,
                'key_presses': self.key_presses,
                'window_data': {
                    'position': (active_window.left, active_window.top),
                    'size': (active_window.width, active_window.height),
                    'is_maximized': active_window.isMaximized,
                    'is_minimized': active_window.isMinimized
                }
            }
            
            return activity_data
            
        except Exception as e:
            self.logger.error(f"Error capturing activity: {e}")
            return None
    
    def _get_process_info(self, window):
        """Get process information for a window"""
        try:
            # Try to get process name from window
            process_name = "unknown"
            app_name = window.title
            
            # Get all processes and find matching one
            for proc in psutil.process_iter(['pid', 'name', 'exe']):
                try:
                    if proc.info['name'] and proc.info['name'].lower() in window.title.lower():
                        process_name = proc.info['name']
                        break
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            return {
                'app_name': app_name,
                'process_name': process_name
            }
            
        except Exception as e:
            self.logger.error(f"Error getting process info: {e}")
            return {'app_name': 'unknown', 'process_name': 'unknown'}
    
    def _store_activity(self, activity_data):
        """Store activity data in database"""
        try:
            activity = Activity(
                session_id=self.current_session.session_id,
                timestamp=datetime.utcnow(),
                **activity_data
            )
            
            db.session.add(activity)
            db.session.commit()
            
        except Exception as e:
            self.logger.error(f"Error storing activity: {e}")
            db.session.rollback()
    
    def _is_user_idle(self):
        """Check if user is idle based on last activity"""
        time_since_activity = datetime.utcnow() - self.last_activity_time
        return time_since_activity.total_seconds() > self.idle_threshold
    
    def _start_input_listeners(self):
        """Start mouse and keyboard listeners"""
        try:
            self.mouse_listener = mouse.Listener(
                on_click=self._on_mouse_click,
                on_scroll=self._on_mouse_scroll
            )
            self.keyboard_listener = keyboard.Listener(
                on_press=self._on_key_press
            )
            
            self.mouse_listener.start()
            self.keyboard_listener.start()
            
        except Exception as e:
            self.logger.error(f"Error starting input listeners: {e}")
    
    def _stop_input_listeners(self):
        """Stop mouse and keyboard listeners"""
        try:
            if self.mouse_listener:
                self.mouse_listener.stop()
            if self.keyboard_listener:
                self.keyboard_listener.stop()
        except Exception as e:
            self.logger.error(f"Error stopping input listeners: {e}")
    
    def _on_mouse_click(self, x, y, button, pressed):
        """Handle mouse click events"""
        if pressed:
            self.mouse_clicks += 1
            self.last_activity_time = datetime.utcnow()
    
    def _on_mouse_scroll(self, x, y, dx, dy):
        """Handle mouse scroll events"""
        self.last_activity_time = datetime.utcnow()
    
    def _on_key_press(self, key):
        """Handle key press events"""
        self.key_presses += 1
        self.last_activity_time = datetime.utcnow()
    
    def _finalize_session(self):
        """Finalize current session"""
        try:
            if self.current_session:
                self.current_session.end_time = datetime.utcnow()
                self.current_session.is_active = False
                
                # Calculate session metrics
                duration = (self.current_session.end_time - self.current_session.start_time).total_seconds()
                self.current_session.total_duration = int(duration)
                
                # Calculate productivity scores
                self._calculate_session_scores()
                
                db.session.commit()
                
        except Exception as e:
            self.logger.error(f"Error finalizing session: {e}")
            db.session.rollback()
    
    def _calculate_session_scores(self):
        """Calculate productivity and focus scores for session"""
        try:
            activities = Activity.query.filter_by(session_id=self.current_session.session_id).all()
            
            if not activities:
                return
            
            total_score = sum(a.productivity_score for a in activities)
            avg_productivity = total_score / len(activities)
            
            # Simple focus score based on app switching frequency
            unique_apps = len(set(a.app_name for a in activities))
            focus_score = max(0, 100 - (unique_apps * 5))  # Penalize app switching
            
            self.current_session.productivity_score = avg_productivity
            self.current_session.focus_score = focus_score
            
        except Exception as e:
            self.logger.error(f"Error calculating session scores: {e}")
    
    def get_status(self):
        """Get current tracking status"""
        current_activity = None
        
        if self.tracking:
            try:
                active_window = gw.getActiveWindow()
                if active_window:
                    current_activity = {
                        'app_name': active_window.title,
                        'window_title': active_window.title,
                        'is_maximized': active_window.isMaximized
                    }
            except:
                pass
        
        return {
            'is_tracking': self.tracking,
            'session_id': self.current_session.session_id if self.current_session else None,
            'current_activity': current_activity,
            'last_activity_time': self.last_activity_time.isoformat() if self.last_activity_time else None
        }

# ==========================================
# app/utils/categorizer.py
import re
from typing import Dict, Tuple

class AppCategorizer:
    def __init__(self):
        self.categories = {
            'productive': {
                'apps': [
                    'code.exe', 'pycharm', 'atom.exe', 'sublime_text.exe', 
                    'notepad++.exe', 'vim', 'emacs', 'intellij',
                    'word.exe', 'excel.exe', 'powerpoint.exe',
                    'notion.exe', 'obsidian.exe', 'typora.exe'
                ],
                'keywords': [
                    'editor', 'ide', 'development', 'programming',
                    'documentation', 'notes', 'writing'
                ],
                'domains': [
                    'github.com', 'stackoverflow.com', 'docs.python.org',
                    'developer.mozilla.org', 'w3schools.com'
                ],
                'base_score': 90
            },
            'communication': {
                'apps': [
                    'slack.exe', 'teams.exe', 'zoom.exe', 'discord.exe',
                    'outlook.exe', 'thunderbird.exe', 'skype.exe'
                ],
                'keywords': ['meeting', 'email', 'chat', 'conference'],
                'domains': [
                    'mail.google.com', 'outlook.com', 'slack.com',
                    'teams.microsoft.com', 'zoom.us'
                ],
                'base_score': 70
            },
            'research': {
                'apps': ['chrome.exe', 'firefox.exe', 'edge.exe'],
                'keywords': [
                    'research', 'learning', 'tutorial', 'documentation',
                    'how to', 'guide', 'manual'
                ],
                'domains': [
                    'wikipedia.org', 'coursera.org', 'edx.org',
                    'khanacademy.org', 'medium.com'
                ],
                'base_score': 80
            },
            'social': {
                'apps': [],
                'keywords': ['social', 'chat', 'friends'],
                'domains': [
                    'facebook.com', 'twitter.com', 'instagram.com',
                    'linkedin.com', 'reddit.com', 'tiktok.com'
                ],
                'base_score': 30
            },
            'entertainment': {
                'apps': [
                    'spotify.exe', 'vlc.exe', 'netflix.exe',
                    'steam.exe', 'epic games.exe'
                ],
                'keywords': ['game', 'music', 'video', 'movie', 'entertainment'],
                'domains': [
                    'youtube.com', 'netflix.com', 'spotify.com',
                    'twitch.tv', 'steam.com'
                ],
                'base_score': 10
            },
            'system': {
                'apps': [
                    'explorer.exe', 'finder', 'terminal.exe',
                    'cmd.exe', 'powershell.exe'
                ],
                'keywords': ['system', 'settings', 'control panel'],
                'domains': [],
                'base_score': 50
            }
        }
    
    def categorize_activity(self, process_name: str, window_title: str, url: str = None) -> Dict:
        """Categorize an activity based on process name, window title, and URL"""
        
        process_name = process_name.lower() if process_name else ""
        window_title = window_title.lower() if window_title else ""
        url = url.lower() if url else ""
        
        # Check each category
        for category, rules in self.categories.items():
            score = 0
            
            # Check process name
            if any(app in process_name for app in rules['apps']):
                score += 40
            
            # Check window title keywords
            if any(keyword in window_title for keyword in rules['keywords']):
                score += 30
            
            # Check URL domains
            if url and any(domain in url for domain in rules['domains']):
                score += 50
            
            # If we have a match, calculate final score
            if score > 0:
                final_score = min(100, rules['base_score'] + score - 50)
                
                # Determine subcategory
                subcategory = self._determine_subcategory(category, process_name, window_title, url)
                
                return {
                    'category': category,
                    'subcategory': subcategory,
                    'productivity_score': final_score,
                    'confidence': min(100, score)
                }
        
        # Default category if no match
        return {
            'category': 'uncategorized',
            'subcategory': 'unknown',
            'productivity_score': 50,
            'confidence': 0
        }
    
    def _determine_subcategory(self, category: str, process_name: str, window_title: str, url: str) -> str:
        """Determine subcategory based on specific patterns"""
        
        subcategory_patterns = {
            'productive': {
                'coding': ['code', 'pycharm', 'atom', 'sublime', 'vim', 'github'],
                'writing': ['word', 'notepad', 'typora', 'notion', 'obsidian'],
                'design': ['photoshop', 'illustrator', 'figma', 'sketch'],
                'data': ['excel', 'tableau', 'power bi', 'jupyter']
            },
            'communication': {
                'email': ['outlook', 'gmail', 'mail', 'thunderbird'],
                'chat': ['slack', 'teams', 'discord', 'whatsapp'],
                'video_call': ['zoom', 'meet', 'skype', 'facetime']
            },
            'research': {
                'learning': ['tutorial', 'course', 'learning', 'education'],
                'reference': ['documentation', 'docs', 'manual', 'api'],
                'news': ['news', 'article', 'blog', 'medium']
            },
            'entertainment': {
                'gaming': ['steam', 'epic', 'game', 'xbox', 'playstation'],
                'streaming': ['youtube', 'netflix', 'twitch', 'spotify'],
                'social_media': ['facebook', 'twitter', 'instagram', 'tiktok']
            }
        }
        
        if category in subcategory_patterns:
            text_to_check = f"{process_name} {window_title} {url}".lower()
            
            for subcat, keywords in subcategory_patterns[category].items():
                if any(keyword in text_to_check for keyword in keywords):
                    return subcat
        
        return 'general'

# ==========================================
# app/api/activity.py
from flask import Blueprint, request, jsonify
from app.services.activity_tracker import ActivityTracker
from app.models.activity import ActivitySession, Activity
from app import db
from datetime import datetime, timedelta
import logging

activity_bp = Blueprint('activity', __name__)
tracker = ActivityTracker()
logger = logging.getLogger(__name__)

@activity_bp.route('/start', methods=['POST'])
def start_tracking():
    """Start activity tracking"""
    try:
        result = tracker.start_tracking()
        return jsonify(result), 200
    except Exception as e:
        logger.error(f"Error starting tracking: {e}")
        return jsonify({"error": "Failed to start tracking"}), 500

@activity_bp.route('/stop', methods=['POST'])
def stop_tracking():
    """Stop activity tracking"""
    try:
        result = tracker.stop_tracking()
        return jsonify(result), 200
    except Exception as e:
        logger.error(f"Error stopping tracking: {e}")
        return jsonify({"error": "Failed to stop tracking"}), 500

@activity_bp.route('/status', methods=['GET'])
def get_status():
    """Get current tracking status"""
    try:
        status = tracker.get_status()
        return jsonify(status), 200
    except Exception as e:
        logger.error(f"Error getting status: {e}")
        return jsonify({"error": "Failed to get status"}), 500

@activity_bp.route('/current', methods=['GET'])
def get_current_activity():
    """Get current activity"""
    try:
        if not tracker.tracking:
            return jsonify({"message": "Tracking not active"}), 200
        
        # Get latest activity from current session
        if tracker.current_session:
            latest_activity = Activity.query.filter_by(
                session_id=tracker.current_session.session_id
            ).order_by(Activity.timestamp.desc()).first()
            
            if latest_activity:
                return jsonify(latest_activity.to_dict()), 200
        
        return jsonify({"message": "No current activity"}), 200
        
    except Exception as e:
        logger.error(f"Error getting current activity: {e}")
        return jsonify({"error": "Failed to get current activity"}), 500

@activity_bp.route('/history', methods=['GET'])
def get_activity_history():
    """Get activity history with pagination"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        days = request.args.get('days', 7, type=int)
        
        # Calculate date range
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Query activities
        activities = Activity.query.filter(
            Activity.timestamp >= start_date,
            Activity.timestamp <= end_date
        ).order_by(Activity.timestamp.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'activities': [activity.to_dict() for activity in activities.items],
            'pagination': {
                'page': page,
                'pages': activities.pages,
                'per_page': per_page,
                'total': activities.total,
                'has_next': activities.has_next,
                'has_prev': activities.has_prev
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting activity history: {e}")
        return jsonify({"error": "Failed to get activity history"}), 500

@activity_bp.route('/sessions', methods=['GET'])
def get_sessions():
    """Get activity sessions"""
    try:
        days = request.args.get('days', 7, type=int)
        
        # Calculate date range
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Query sessions
        sessions = ActivitySession.query.filter(
            ActivitySession.start_time >= start_date,
            ActivitySession.start_time <= end_date
        ).order_by(ActivitySession.start_time.desc()).all()
        
        session_data = []
        for session in sessions:
            session_info = {
                'session_id': session.session_id,
                'start_time': session.start_time.isoformat(),
                'end_time': session.end_time.isoformat() if session.end_time else None,
                'total_duration': session.total_duration,
                'productivity_score': session.productivity_score,
                'focus_score': session.focus_score,
                'is_active': session.is_active,
                'activity_count': len(session.activities)
            }
            session_data.append(session_info)
        
        return jsonify({'sessions': session_data}), 200
        
    except Exception as e:
        logger.error(f"Error getting sessions: {e}")
        return jsonify({"error": "Failed to get sessions"}), 500

@activity_bp.route('/session/<session_id>', methods=['GET'])
def get_session_details(session_id):
    """Get detailed information about a specific session"""
    try:
        session = ActivitySession.query.filter_by(session_id=session_id).first()
        
        if not session:
            return jsonify({"error": "Session not found"}), 404
        
        # Get activities for this session
        activities = Activity.query.filter_by(session_id=session_id).order_by(Activity.timestamp.asc()).all()
        
        session_details = {
            'session_info': {
                'session_id': session.session_id,
                'start_time': session.start_time.isoformat(),
                'end_time': session.end_time.isoformat() if session.end_time else None,
                'total_duration': session.total_duration,
                'productivity_score': session.productivity_score,
                'focus_score': session.focus_score,
                'is_active': session.is_active
            },
            'activities': [activity.to_dict() for activity in activities],
            'summary': {
                'total_activities': len(activities),
                'unique_apps': len(set(a.app_name for a in activities)),
                'categories': list(set(a.category for a in activities if a.category)),
                'avg_productivity': sum(a.productivity_score for a in activities) / len(activities) if activities else 0
            }
        }
        
        return jsonify(session_details), 200
        
    except Exception as e:
        logger.error(f"Error getting session details: {e}")
        return jsonify({"error": "Failed to get session details"}), 500

# ==========================================
# app/api/dashboard.py
from flask import Blueprint, jsonify, request
from app.models.activity import ActivitySession, Activity, WebActivity
from app import db
from datetime import datetime, timedelta
from sqlalchemy import func, desc
import logging

dashboard_bp = Blueprint('dashboard', __name__)
logger = logging.getLogger(__name__)

@dashboard_bp.route('/today', methods=['GET'])
def get_today_summary():
    """Get today's productivity summary"""
    try:
        today = datetime.utcnow().date()
        start_of_day = datetime.combine(today, datetime.min.time())
        end_of_day = datetime.combine(today, datetime.max.time())
        
        # Get today's activities
        activities = Activity.query.filter(
            Activity.timestamp >= start_of_day,
            Activity.timestamp <= end_of_day
        ).all()
        
        if not activities:
            return jsonify({
                'date': today.isoformat(),
                'total_time': 0,
                'productivity_score': 0,
                'focus_score': 0,
                'top_apps': [],
                'categories': {},
                'hourly_breakdown': []
            }), 200
        
        # Calculate metrics
        total_time = len(activities) * 5  # 5 seconds per activity
        avg_productivity = sum(a.productivity_score for a in activities) / len(activities)
        
        # App usage
        app_usage = {}
        for activity in activities:
            app_name = activity.app_name
            if app_name in app_usage:
                app_usage[app_name] += 5
            else:
                app_usage[app_name] = 5
        
        top_apps = sorted(app_usage.items(), key=lambda x: x[1], reverse=True)[:5]
        
        # Category breakdown
        category_usage = {}
        for activity in activities:
            if activity.category:
                if activity.category in category_usage:
                    category_usage[activity.category] += 5
                else:
                    category_usage[activity.category] = 5
        
        # Hourly breakdown
        hourly_data = [0] * 24
        for activity in activities:
            hour = activity.timestamp.hour
            hourly_data[hour] += 5
        
        hourly_breakdown = [
            {'hour': i, 'seconds': hourly_data[i], 'minutes': hourly_data[i] / 60}
            for i in range(24)
        ]
        
        # Focus score (simple calculation based on app switching)
        unique_apps = len(set(a.app_name for a in activities))
        focus_score = max(0, 100 - (unique_apps * 3))
        
        summary = {
            'date': today.isoformat(),
            'total_time': total_time,
            'total_minutes': total_time / 60,
            'productivity_score': round(avg_productivity, 2),
            'focus_score': round(focus_score, 2),
            'top_apps': [{'name': name, 'seconds': seconds, 'minutes': seconds/60} for name, seconds in top_apps],
            'categories': {cat: {'seconds': secs, 'minutes': secs/60} for cat, secs in category_usage.items()},
            'hourly_breakdown': hourly_breakdown,
            'total_activities': len(activities),
            'unique_apps': unique_apps
        }
        
        return jsonify(summary), 200
        
    except Exception as e:
        logger.error(f"Error getting today summary: {e}")
        return jsonify({"error": "Failed to get today's summary"}), 500

@dashboard_bp.route('/week', methods=['GET'])
def get_week_summary():
    """Get this week's productivity summary"""
    try:
        today = datetime.utcnow().date()
        week_start = today - timedelta(days=today.weekday())
        week_end = week_start + timedelta(days=6)
        
        start_datetime = datetime.combine(week_start, datetime.min.time())
        end_datetime = datetime.combine(week_end, datetime.max.time())
        
        # Get week's activities
        activities = Activity.query.filter(
            Activity.timestamp >= start_datetime,
            Activity.timestamp <= end_datetime
        ).all()
        
        if not activities:
            return jsonify({
                'week_start': week_start.isoformat(),
                'week_end': week_end.isoformat(),
                'daily_breakdown': [],
                'total_time': 0,
                'avg_productivity': 0
            }), 200
        
        # Daily breakdown
        daily_data = {}
        for activity in activities:
            day = activity.timestamp.date()
            if day not in daily_data:
                daily_data[day] = {
                    'activities': [],
                    'total_time': 0,
                    'productivity_scores': []
                }
            daily_data[day]['activities'].append(activity)
            daily_data[day]['total_time'] += 5
            daily_data[day]['productivity_scores'].append(activity.productivity_score)
        
        daily_breakdown = []
        for i in range(7):
            day = week_start + timedelta(days=i)
            day_data = daily_data.get(day, {'activities': [], 'total_time': 0, 'productivity_scores': []})
            
            avg_productivity = (
                sum(day_data['productivity_scores']) / len(day_data['productivity_scores'])
                if day_data['productivity_scores'] else 0
            )
            
            daily_breakdown.append({
                'date': day.isoformat(),
                'day_name': day.strftime('%A'),
                'total_time': day_data['total_time'],
                'minutes': day_data['total_time'] / 60,
                'productivity_score': round(avg_productivity, 2),
                'activity_count': len(day_data['activities'])
            })
        
        # Week totals
        total_time = sum(day['total_time'] for day in daily_breakdown)
        total_productivity_scores = [a.productivity_score for a in activities]
        avg_productivity = sum(total_productivity_scores) / len(total_productivity_scores) if total_productivity_scores else 0
        
        summary = {
            'week_start': week_start.isoformat(),
            'week_end': week_end.isoformat(),
            'daily_breakdown': daily_breakdown,
            'total_time': total_time,
            'total_minutes': total_time / 60,
            'total_hours': total_time / 3600,
            'avg_productivity': round(avg_productivity, 2),
            'total_activities': len(activities),
            'active_days': len([day for day in daily_breakdown if day['total_time'] > 0])
        }
        
        return jsonify(summary), 200
        
    except Exception as e:
        logger.error(f"Error getting week summary: {e}")
        return jsonify({"error": "Failed to get week summary"}), 500

@dashboard_bp.route('/productivity-trends', methods=['GET'])
def get_productivity_trends():
    """Get productivity trends over time"""
    try:
        days = request.args.get('days', 30, type=int)
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Get activities grouped by day
        daily_activities = db.session.query(
            func.date(Activity.timestamp).label('date'),
            func.count(Activity.id).label('activity_count'),
            func.avg(Activity.productivity_score).label('avg_productivity'),
            func.sum(Activity.duration).label('total_time')
        ).filter(
            Activity.timestamp >= start_date,
            Activity.timestamp <= end_date
        ).group_by(func.date(Activity.timestamp)).all()
        
        trends = []
        for day_data in daily_activities:
            trends.append({
                'date': day_data.date.isoformat(),
                'activity_count': day_data.activity_count,
                'avg_productivity': round(float(day_data.avg_productivity or 0), 2),
                'total_time': int(day_data.total_time or 0),
                'minutes': int(day_data.total_time or 0) / 60
            })
        
        # Fill in missing days with zero values
        current_date = start_date.date()
        end_date_only = end_date.date()
        complete_trends = []
        
        while current_date <= end_date_only:
            existing_day = next((t for t in trends if t['date'] == current_date.isoformat()), None)
            if existing_day:
                complete_trends.append(existing_day)
            else:
                complete_trends.append({
                    'date': current_date.isoformat(),
                    'activity_count': 0,
                    'avg_productivity': 0,
                    'total_time': 0,
                    'minutes': 0
                })
            current_date += timedelta(days=1)
        
        return jsonify({
            'trends': complete_trends,
            'period': {
                'start_date': start_date.date().isoformat(),
                'end_date': end_date.date().isoformat(),
                'days': days
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting productivity trends: {e}")
        return jsonify({"error": "Failed to get productivity trends"}), 500

@dashboard_bp.route('/app-usage', methods=['GET'])
def get_app_usage():
    """Get application usage statistics"""
    try:
        days = request.args.get('days', 7, type=int)
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Get app usage data
        app_usage = db.session.query(
            Activity.app_name,
            Activity.category,
            func.count(Activity.id).label('activity_count'),
            func.sum(Activity.duration).label('total_time'),
            func.avg(Activity.productivity_score).label('avg_productivity')
        ).filter(
            Activity.timestamp >= start_date,
            Activity.timestamp <= end_date
        ).group_by(Activity.app_name, Activity.category).all()
        
        apps = []
        for app_data in app_usage:
            apps.append({
                'name': app_data.app_name,
                'category': app_data.category,
                'activity_count': app_data.activity_count,
                'total_time': int(app_data.total_time or 0),
                'minutes': int(app_data.total_time or 0) / 60,
                'hours': int(app_data.total_time or 0) / 3600,
                'avg_productivity': round(float(app_data.avg_productivity or 0), 2)
            })
        
        # Sort by total time
        apps.sort(key=lambda x: x['total_time'], reverse=True)
        
        # Category summary
        category_summary = {}
        for app in apps:
            category = app['category'] or 'uncategorized'
            if category not in category_summary:
                category_summary[category] = {
                    'total_time': 0,
                    'app_count': 0,
                    'activity_count': 0
                }
            category_summary[category]['total_time'] += app['total_time']
            category_summary[category]['app_count'] += 1
            category_summary[category]['activity_count'] += app['activity_count']
        
        # Add percentages
        total_time = sum(app['total_time'] for app in apps)
        for app in apps:
            app['percentage'] = round((app['total_time'] / total_time * 100), 2) if total_time > 0 else 0
        
        for category in category_summary:
            category_data = category_summary[category]
            category_data['percentage'] = round((category_data['total_time'] / total_time * 100), 2) if total_time > 0 else 0
            category_data['minutes'] = category_data['total_time'] / 60
            category_data['hours'] = category_data['total_time'] / 3600
        
        return jsonify({
            'apps': apps,
            'category_summary': category_summary,
            'total_time': total_time,
            'total_minutes': total_time / 60,
            'total_hours': total_time / 3600,
            'period': {
                'start_date': start_date.date().isoformat(),
                'end_date': end_date.date().isoformat(),
                'days': days
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting app usage: {e}")
        return jsonify({"error": "Failed to get app usage"}), 500

# ==========================================
# app/api/web_tracking.py
from flask import Blueprint, request, jsonify
from flask_socketio import emit, disconnect
from app import socketio, db
from app.models.activity import WebActivity
from app.utils.categorizer import AppCategorizer
from datetime import datetime
import logging
import tldextract

web_bp = Blueprint('web_tracking', __name__)
categorizer = AppCategorizer()
logger = logging.getLogger(__name__)

# WebSocket events for browser extension
@socketio.on('connect', namespace='/extension')
def handle_extension_connect():
    """Handle browser extension connection"""
    logger.info('Browser extension connected')
    emit('connection_acknowledged', {'status': 'connected'})

@socketio.on('disconnect', namespace='/extension')
def handle_extension_disconnect():
    """Handle browser extension disconnection"""
    logger.info('Browser extension disconnected')

@socketio.on('page_visit', namespace='/extension')
def handle_page_visit(data):
    """Handle page visit data from extension"""
    try:
        # Extract domain from URL
        extracted = tldextract.extract(data.get('url', ''))
        domain = f"{extracted.domain}.{extracted.suffix}"
        
        # Categorize web activity
        category_data = categorizer.categorize_activity(
            process_name=data.get('browser', 'browser'),
            window_title=data.get('title', ''),
            url=data.get('url', '')
        )
        
        # Store web activity
        web_activity = WebActivity(
            session_id=data.get('session_id', 'unknown'),
            url=data.get('url', ''),
            domain=domain,
            page_title=data.get('title', ''),
            browser=data.get('browser', 'unknown'),
            category=category_data['category'],
            productivity_score=category_data['productivity_score'],
            is_productive=category_data['productivity_score'] >= 50
        )
        
        db.session.add(web_activity)
        db.session.commit()
        
        emit('page_visit_acknowledged', {'status': 'stored', 'category': category_data['category']})
        
    except Exception as e:
        logger.error(f"Error handling page visit: {e}")
        emit('error', {'message': 'Failed to store page visit'})

@socketio.on('time_update', namespace='/extension')
def handle_time_update(data):
    """Handle time spent updates from extension"""
    try:
        # Find and update existing web activity
        web_activity = WebActivity.query.filter_by(
            url=data.get('url'),
            session_id=data.get('session_id')
        ).order_by(WebActivity.timestamp.desc()).first()
        
        if web_activity:
            web_activity.time_spent = data.get('timeSpent', 0)
            web_activity.tab_switches = data.get('tabSwitches', 0)
            web_activity.scroll_depth = data.get('scrollDepth', 0.0)
            db.session.commit()
        
        emit('time_update_acknowledged', {'status': 'updated'})
        
    except Exception as e:
        logger.error(f"Error handling time update: {e}")
        emit('error', {'message': 'Failed to update time'})

# REST API endpoints
@web_bp.route('/activity', methods=['GET'])
def get_web_activity():
    """Get web browsing activity"""
    try:
        days = request.args.get('days', 7, type=int)
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        activities = WebActivity.query.filter(
            WebActivity.timestamp >= start_date,
            WebActivity.timestamp <= end_date
        ).order_by(WebActivity.timestamp.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'activities': [activity.to_dict() for activity in activities.items],
            'pagination': {
                'page': page,
                'pages': activities.pages,
                'per_page': per_page,
                'total': activities.total
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting web activity: {e}")
        return jsonify({"error": "Failed to get web activity"}), 500

@web_bp.route('/domains', methods=['GET'])
def get_top_domains():
    """Get top visited domains"""
    try:
        days = request.args.get('days', 7, type=int)
        limit = request.args.get('limit', 20, type=int)
        
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        domain_stats = db.session.query(
            WebActivity.domain,
            WebActivity.category,
            func.count(WebActivity.id).label('visit_count'),
            func.sum(WebActivity.time_spent).label('total_time'),
            func.avg(WebActivity.productivity_score).label('avg_productivity')
        ).filter(
            WebActivity.timestamp >= start_date,
            WebActivity.timestamp <= end_date
        ).group_by(WebActivity.domain, WebActivity.category).all()
        
        domains = []
        for domain_data in domain_stats:
            domains.append({
                'domain': domain_data.domain,
                'category': domain_data.category,
                'visit_count': domain_data.visit_count,
                'total_time': int(domain_data.total_time or 0),
                'minutes': int(domain_data.total_time or 0) / 60,
                'avg_productivity': round(float(domain_data.avg_productivity or 0), 2)
            })
        
        # Sort by total time and limit results
        domains.sort(key=lambda x: x['total_time'], reverse=True)
        domains = domains[:limit]
        
        return jsonify({
            'domains': domains,
            'period': {
                'start_date': start_date.date().isoformat(),
                'end_date': end_date.date().isoformat(),
                'days': days
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting top domains: {e}")
        return jsonify({"error": "Failed to get top domains"}), 500

# ==========================================
# app/api/analytics.py
from flask import Blueprint, jsonify, request
from app.models.activity import Activity, ActivitySession, WebActivity
from app import db
from datetime import datetime, timedelta
from sqlalchemy import func, text
import pandas as pd
import logging

analytics_bp = Blueprint('analytics', __name__)
logger = logging.getLogger(__name__)

@analytics_bp.route('/focus-score', methods=['GET'])
def get_focus_score():
    """Calculate and return focus score"""
    try:
        hours = request.args.get('hours', 8, type=int)  # Default to last 8 hours
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=hours)
        
        # Get activities in time range
        activities = Activity.query.filter(
            Activity.timestamp >= start_time,
            Activity.timestamp <= end_time
        ).all()
        
        if not activities:
            return jsonify({
                'focus_score': 0,
                'period_hours': hours,
                'factors': {
                    'app_switching': 0,
                    'productivity_consistency': 0,
                    'time_distribution': 0
                },
                'recommendations': ['Start tracking to get focus insights']
            }), 200
        
        # Calculate focus factors
        
        # 1. App switching penalty
        unique_apps = len(set(a.app_name for a in activities))
        total_activities = len(activities)
        app_switching_score = max(0, 100 - (unique_apps / total_activities * 100))
        
        # 2. Productivity consistency
        productivity_scores = [a.productivity_score for a in activities]
        avg_productivity = sum(productivity_scores) / len(productivity_scores)
        productivity_variance = sum((score - avg_productivity) ** 2 for score in productivity_scores) / len(productivity_scores)
        consistency_score = max(0, 100 - productivity_variance)
        
        # 3. Time distribution (prefer focused blocks)
        app_blocks = {}
        current_app = None
        block_length = 0
        
        for activity in sorted(activities, key=lambda x: x.timestamp):
            if activity.app_name != current_app:
                if current_app and current_app in app_blocks:
                    app_blocks[current_app].append(block_length)
                else:
                    app_blocks[current_app] = [block_length] if current_app else []
                current_app = activity.app_name
                block_length = 1
            else:
                block_length += 1
        
        # Add final block
        if current_app:
            if current_app in app_blocks:
                app_blocks[current_app].append(block_length)
            else:
                app_blocks[current_app] = [block_length]
        
        # Calculate average block length
        all_blocks = [block for blocks in app_blocks.values() for block in blocks if block > 0]
        avg_block_length = sum(all_blocks) / len(all_blocks) if all_blocks else 0
        time_distribution_score = min(100, avg_block_length * 10)  # Reward longer blocks
        
        # Combined focus score
        focus_score = (
            app_switching_score * 0.4 +
            consistency_score * 0.3 +
            time_distribution_score * 0.3
        )
        
        # Generate recommendations
        recommendations = []
        if app_switching_score < 70:
            recommendations.append("Try to stay focused on one application for longer periods")
        if consistency_score < 70:
            recommendations.append("Consider organizing your work to maintain consistent productivity")
        if time_distribution_score < 70:
            recommendations.append("Work in focused time blocks rather than switching frequently")
        if focus_score >= 80:
            recommendations.append("Great focus! Keep up the excellent work pattern")
        
        return jsonify({
            'focus_score': round(focus_score, 2),
            'period_hours': hours,
            'factors': {
                'app_switching': round(app_switching_score, 2),
                'productivity_consistency': round(consistency_score, 2),
                'time_distribution': round(time_distribution_score, 2)
            },
            'metrics': {
                'unique_apps': unique_apps,
                'total_activities': total_activities,
                'avg_productivity': round(avg_productivity, 2),
                'avg_block_length': round(avg_block_length, 2)
            },
            'recommendations': recommendations
        }), 200
        
    except Exception as e:
        logger.error(f"Error calculating focus score: {e}")
        return jsonify({"error": "Failed to calculate focus score"}), 500

@analytics_bp.route('/productivity-insights', methods=['GET'])
def get_productivity_insights():
    """Get AI-powered productivity insights"""
    try:
        days = request.args.get('days', 7, type=int)
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Get activities
        activities = Activity.query.filter(
            Activity.timestamp >= start_date,
            Activity.timestamp <= end_date
        ).all()
        
        if not activities:
            return jsonify({
                'insights': [],
                'patterns': {},
                'recommendations': ['Start tracking to get productivity insights']
            }), 200
        
        insights = []
        patterns = {}
        recommendations = []
        
        # Convert to DataFrame for analysis
        data = []
        for activity in activities:
            data.append({
                'timestamp': activity.timestamp,
                'hour': activity.timestamp.hour,
                'weekday': activity.timestamp.weekday(),
                'app_name': activity.app_name,
                'category': activity.category,
                'productivity_score': activity.productivity_score
            })
        
        df = pd.DataFrame(data)
        
        # 1. Peak productivity hours
        hourly_productivity = df.groupby('hour')['productivity_score'].mean()
        peak_hour = hourly_productivity.idxmax()
        peak_score = hourly_productivity.max()
        
        insights.append({
            'type': 'peak_hours',
            'title': 'Peak Productivity Time',
            'description': f"Your most productive hour is {peak_hour}:00 with an average productivity score of {peak_score:.1f}",
            'value': peak_hour,
            'score': peak_score
        })
        
        patterns['peak_hour'] = {
            'hour': int(peak_hour),
            'score': float(peak_score),
            'hourly_breakdown': {int(h): float(s) for h, s in hourly_productivity.items()}
        }
        
        # 2. Best/worst days
        daily_productivity = df.groupby('weekday')['productivity_score'].mean()
        best_day = daily_productivity.idxmax()
        worst_day = daily_productivity.idxmin()
        
        day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        
        insights.append({
            'type': 'daily_pattern',
            'title': 'Weekly Productivity Pattern',
            'description': f"You're most productive on {day_names[best_day]} and least productive on {day_names[worst_day]}",
            'best_day': day_names[best_day],
            'worst_day': day_names[worst_day]
        })
        
        patterns['weekly_pattern'] = {
            'best_day': day_names[best_day],
            'worst_day': day_names[worst_day],
            'daily_scores': {day_names[i]: float(daily_productivity.get(i, 0)) for i in range(7)}
        }
        
        # 3. App productivity analysis
        app_productivity = df.groupby('app_name').agg({
            'productivity_score': 'mean',
            'timestamp': 'count'
        }).rename(columns={'timestamp': 'usage_count'})
        
        # Find apps with high usage but low productivity
        high_usage_low_prod = app_productivity[
            (app_productivity['usage_count'] >= 10) & 
            (app_productivity['productivity_score'] < 50)
        ]
        
        if not high_usage_low_prod.empty:
            worst_app = high_usage_low_prod.index[0]
            insights.append({
                'type': 'distraction_alert',
                'title': 'Potential Distraction Detected',
                'description': f"You spend significant time on {worst_app} with low productivity. Consider limiting usage.",
                'app_name': worst_app,
                'productivity_score': float(high_usage_low_prod.loc[worst_app, 'productivity_score'])
            })
        
        # 4. Generate recommendations
        if peak_hour < 12:
            recommendations.append("You're a morning person! Schedule important tasks before noon.")
        elif peak_hour > 18:
            recommendations.append("You're most productive in the evening. Plan complex work for later in the day.")
        else:
            recommendations.append("Your peak productivity is in the afternoon. Block this time for focused work.")
        
        if daily_productivity.std() > 10:
            recommendations.append("Your productivity varies significantly by day. Try to maintain consistent routines.")
        
        # 5. Category analysis
        category_productivity = df.groupby('category')['productivity_score'].mean()
        if 'entertainment' in category_productivity and category_productivity['entertainment'] > 0:
            ent_time = len(df[df['category'] == 'entertainment']) * 5 / 60  # minutes
            recommendations.append(f"You spent {ent_time:.1f} minutes on entertainment. Consider time-boxing leisure activities.")
        
        return jsonify({
            'insights': insights,
            'patterns': patterns,
            'recommendations': recommendations,
            'period': {
                'start_date': start_date.date().isoformat(),
                'end_date': end_date.date().isoformat(),
                'days': days
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting productivity insights: {e}")
        return jsonify({"error": "Failed to get productivity insights"}), 500

# ==========================================
# app/api/settings.py
from flask import Blueprint, request, jsonify
from app import db
import json
import logging

settings_bp = Blueprint('settings', __name__)
logger = logging.getLogger(__name__)

# Simple settings storage (you might want to create a Settings model)
DEFAULT_SETTINGS = {
    'tracking': {
        'auto_start': False,
        'tracking_interval': 5,
        'idle_threshold': 300,
        'track_web_activity': True,
        'track_mouse_keyboard': True
    },
    'productivity':