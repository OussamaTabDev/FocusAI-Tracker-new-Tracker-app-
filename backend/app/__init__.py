from flask import Flask
from app.core.config import Config
from app.core.extensions import db , migrate , cors





# Sub Routes (apps)
from app.api.Widgets import widgets_bp
from app.api.Activitiy import activity_bp



def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    
    # Enable CORS for Electron frontend
    cors(app, origins=["http://localhost:3000", "file://"])
    
    # Register blueprints
    # from app.api.activity import bp as activity_bp
    # from app.api.dashboard import bp as dashboard_bp
    # from app.api.settings import bp as settings_bp
    # from app.api.kids_mode import bp as kids_bp
    
    # app.register_blueprint(activity_bp, url_prefix='/api/activity')
    # app.register_blueprint(dashboard_bp, url_prefix='/api/dashboard')
    # app.register_blueprint(settings_bp, url_prefix='/api/settings')
    # app.register_blueprint(kids_bp, url_prefix='/api/kids')
    app.register_blueprint(widgets_bp)
    app.register_blueprint(activity_bp)
    # app.disableHardwareAcceleration();



    # Basic routes
    @app.route('/')
    def index():
        return {"message": "FocusAI Tracker API is running!"}
    
    @app.route('/health')
    def health():
        return {"status": "healthy", "version": "1.0.0"}
    
    return app




