# This file has been split into tracking_api.py, window_api.py, and stats_api.py for better organization.
# All endpoints have been moved. This file is deprecated.

# app/api/activity.py
from flask import jsonify, request
from flask import current_app as app
from app.services.multi_window_tracker import MultiWindowTracker
from threading import Thread
# from . import activity_bp
from datetime import datetime

tracker = MultiWindowTracker()
tracker_thread = None

# @activity_bp.route('/start', methods=['POST'])
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

@activity_bp.route('/history', methods=['GET'])
def get_focus_history():
    limit = min(int(request.args.get('limit', 50)), 1000)  # Max 1000 entries
    return jsonify({
        'status': 'success',
        'data': tracker.focus_history[-limit:],
        'total_entries': len(tracker.focus_history)
    }), 200

@activity_bp.route('/usage', methods=['GET'])
def get_usage_summary():
    summary = {}
    for entry in tracker.focus_history:
        app = entry.get("browser_app") or entry.get("app", "Unknown")
        summary[app] = summary.get(app, 0) + tracker.track_window_usage.__defaults__[0]  # Get interval from function defaults
    return jsonify({
        'status': 'success',
        'summary': summary,
        'window_types': tracker.get_window_stats_by_type()
    }), 200

@activity_bp.route('/top-windows', methods=['GET'])
def get_top_windows():
    limit = min(int(request.args.get('limit', 5)), 20)  # Max 20 windows
    return jsonify({
        'status': 'success',
        'data': tracker.get_top_windows(limit),
        'total_unique_windows': len(tracker.window_usage_time)
    }), 200

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

@activity_bp.route('/all-windows', methods=['GET'])
def get_all_windows():
    return jsonify({
        'status': 'success',
        'data': tracker.capture_window_state(),
        'timestamp': datetime.now().isoformat()
    }), 200























# ---------------------------------------------------------
# # app/api/activity.py
# from flask import jsonify, request
# from flask import current_app as app
# from app.services.multi_window_tracker import MultiWindowTracker
# from threading import Thread
# from . import activity_bp

# tracker = MultiWindowTracker()
# tracker_thread = None

# @activity_bp.route('/start', methods=['POST'])
# def start_tracking():
#     global tracker_thread

#     if not tracker_thread or not tracker_thread.is_alive():
#         tracker_thread = Thread(target=tracker.track_window_usage)
#         tracker_thread.daemon = True
#         tracker_thread.start()
#         return jsonify({
#             'status': 'success',
#             'message': 'Tracking started'
#         }), 200

#     return jsonify({
#         'status': 'error',
#         'message': 'Tracking already running'
#     }), 400

# @activity_bp.route('/stop', methods=['POST'])
# def stop_tracking():
#     global tracker_thread
#     if tracker_thread and tracker_thread.is_alive():
#         tracker.stop_tracking()
#         tracker_thread.join(timeout=2)
#         return jsonify({
#             'status': 'success',
#             'message': 'Tracking stopped'
#         }), 200
#     return jsonify({
#         'status': 'error',
#         'message': 'No active tracking session'
#     }), 400

# @activity_bp.route('/current', methods=['GET'])
# def get_current_window():
#     current_window = tracker.detect_active_window()
#     if current_window:
#         return jsonify({
#             'status': 'success',
#             'data': current_window
#         }), 200
#     return jsonify({
#         'status': 'error',
#         'message': 'Unable to detect active window'
#     }), 400

# @activity_bp.route('/history', methods=['GET'])
# def get_focus_history():
#     return jsonify({
#         'status': 'success',
#         'data': tracker.focus_history[-50:]  # last 50 entries
#     }), 200

# @activity_bp.route('/usage', methods=['GET'])
# def get_usage_summary():
#     summary = {}
#     for entry in tracker.focus_history:
#         app = entry.get("browser_app") or entry.get("app", "Unknown")
#         summary[app] = summary.get(app, 0) + 5  # assuming 5s interval
#     return jsonify({
#         'status': 'success',
#         'summary': summary
#     }), 200
