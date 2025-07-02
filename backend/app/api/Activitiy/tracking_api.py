from flask import jsonify, request
from threading import Thread
from datetime import datetime
from . import activity_bp
from app.services.multi_window_tracker import MultiWindowTracker

tracker = MultiWindowTracker()
tracker_thread = None

@activity_bp.route('/start', methods=['POST'])
def start_tracking():
    global tracker_thread
    if not tracker_thread or not tracker_thread.is_alive():
        interval = request.json.get('interval', 5) if request.json else 5
        tracker_thread = Thread(target=tracker.track_window_usage, kwargs={'interval': interval})
        tracker_thread.daemon = True
        tracker_thread.start()
        return jsonify({
            'status': 'success',
            'message': 'Tracking started',
            'interval': interval,
            'start_time': tracker.start_time.isoformat() if tracker.start_time else None
        }), 200
    return jsonify({
        'status': 'error',
        'message': 'Tracking already running',
        'start_time': tracker.start_time.isoformat() if tracker.start_time else None
    }), 400

@activity_bp.route('/stop', methods=['POST'])
def stop_tracking():
    global tracker_thread
    if tracker_thread and tracker_thread.is_alive():
        tracker.stop_tracking()
        tracker_thread.join(timeout=2)
        return jsonify({
            'status': 'success',
            'message': 'Tracking stopped',
            'session_duration': tracker.get_session_duration(),
            'start_time': tracker.start_time.isoformat() if tracker.start_time else None,
            'end_time': tracker.end_time.isoformat() if tracker.end_time else None
        }), 200
    return jsonify({
        'status': 'error',
        'message': 'No active tracking session'
    }), 400

@activity_bp.route('/session', methods=['GET'])
def get_session_info():
    return jsonify({
        'status': 'success',
        'data': {
            'is_tracking': tracker.tracking,
            'start_time': tracker.start_time.isoformat() if tracker.start_time else None,
            'end_time': tracker.end_time.isoformat() if tracker.end_time else None,
            'duration_seconds': tracker.get_session_duration(),
            'windows_tracked': len(tracker.focus_history),
            'unique_windows': len(tracker.window_usage_time)
        }
    }), 200 