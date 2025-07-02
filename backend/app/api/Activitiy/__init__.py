from flask import Blueprint

activity_bp = Blueprint('activity', __name__ , url_prefix="/api/activity")

from . import tracking_api, window_api, stats_api

# routes register 
# from . import activity_api
# from . import weather_apiactivity_bp  = Blueprint("activity" , __name__ , url_prefix="/api/activity")
