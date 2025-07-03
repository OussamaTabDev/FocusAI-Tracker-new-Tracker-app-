"""
Core activity tracking route definitions.
"""

from flask import jsonify
from .. import activity_bp
from ..Handlers.handlers import ActivityHandlers

# Initialize handlers
activity_handlers = ActivityHandlers()

@activity_bp.route('/start', methods=['POST'])
def start_tracking():
    """Start window activity tracking."""
    response_data, status_code = activity_handlers.start_tracking()
    return jsonify(response_data), status_code

@activity_bp.route('/stop', methods=['POST'])
def stop_tracking():
    """Stop window activity tracking."""
    response_data, status_code = activity_handlers.stop_tracking()
    return jsonify(response_data), status_code

@activity_bp.route('/session', methods=['GET'])
def get_session_info():
    """Get current tracking session information."""
    response_data, status_code = activity_handlers.get_session_info()
    return jsonify(response_data), status_code

@activity_bp.route('/current-window', methods=['GET'])
def get_current_window():
    """Get currently active window information."""
    response_data, status_code = activity_handlers.get_current_window()
    return jsonify(response_data), status_code

@activity_bp.route('/all-captured-windows', methods=['GET'])
def get_all_captured_windows():
    """Get all captured window information."""
    response_data, status_code = activity_handlers.get_all_captured_windows()
    return jsonify(response_data), status_code

@activity_bp.route('/history', methods=['GET'])
def get_focus_history():
    """Get window focus history."""
    response_data, status_code = activity_handlers.get_focus_history()
    return jsonify(response_data), status_code

@activity_bp.route('/usage', methods=['GET'])
def get_usage_summary():
    """Get usage summary and statistics."""
    response_data, status_code = activity_handlers.get_usage_summary()
    return jsonify(response_data), status_code

@activity_bp.route('/top-windows', methods=['GET'])
def get_top_windows():
    """Get top windows by usage time."""
    response_data, status_code = activity_handlers.get_top_windows()
    return jsonify(response_data), status_code