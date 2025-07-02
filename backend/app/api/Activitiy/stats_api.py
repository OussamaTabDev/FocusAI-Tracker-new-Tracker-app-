from flask import jsonify, request
from . import activity_bp
from app.services.multi_window_tracker import MultiWindowTracker

tracker = MultiWindowTracker()

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
    interval = getattr(tracker, 'interval', 5)  # Use tracker.interval if available, else default to 5
    for entry in tracker.focus_history:
        app = entry.get("browser_app") or entry.get("app", "Unknown")
        summary[app] = summary.get(app, 0) + interval
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