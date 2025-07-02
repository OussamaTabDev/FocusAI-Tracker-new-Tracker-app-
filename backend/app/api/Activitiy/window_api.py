from flask import jsonify
from datetime import datetime
from . import activity_bp
from app.services.multi_window_tracker import MultiWindowTracker

tracker = MultiWindowTracker()

@activity_bp.route('/current', methods=['GET'])
def get_current_window():
    current_window = tracker.detect_active_window()
    if current_window:
        return jsonify({
            'status': 'success',
            'data': current_window,
            'timestamp': datetime.now().isoformat()
        }), 200
    return jsonify({
        'status': 'error',
        'message': 'Unable to detect active window'
    }), 400

@activity_bp.route('/all-windows', methods=['GET'])
def get_all_windows():
    return jsonify({
        'status': 'success',
        'data': tracker.capture_window_state(),
        'timestamp': datetime.now().isoformat()
    }), 200 