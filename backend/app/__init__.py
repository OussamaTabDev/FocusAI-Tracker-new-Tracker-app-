from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from app.core.config import Config





# Sub Routes (apps)
from app.api.Widgets import widgets_bp
# import app.api.Widgets  




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
    # from app.api.activity import bp as activity_bp
    # from app.api.dashboard import bp as dashboard_bp
    # from app.api.settings import bp as settings_bp
    # from app.api.kids_mode import bp as kids_bp
    
    # app.register_blueprint(activity_bp, url_prefix='/api/activity')
    # app.register_blueprint(dashboard_bp, url_prefix='/api/dashboard')
    # app.register_blueprint(settings_bp, url_prefix='/api/settings')
    # app.register_blueprint(kids_bp, url_prefix='/api/kids')
    app.register_blueprint(widgets_bp)
    # app.disableHardwareAcceleration();
    # Basic routes
    @app.route('/')
    def index():
        return {"message": "FocusAI Tracker API is running!"}
    
    @app.route('/health')
    def health():
        return {"status": "healthy", "version": "1.0.0"}
    
    return app




# from flask import Flask


# def create_app():
#     app = Flask(__name__)
    
#     # views
#     return app
