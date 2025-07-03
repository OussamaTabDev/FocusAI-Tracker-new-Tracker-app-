"""
Core activity tracking request handlers.
"""

from flask import jsonify, request
from threading import Thread, Lock
from datetime import datetime
import logging
from dataclasses import asdict
from typing import Optional, Dict, Any

from app.services.Activity.WindowTracker import WindowTracker
from ..config import *

logger = logging.getLogger(__name__)


class ActivityHandlers:
    """Handles core activity tracking operations."""
    
    def __init__(self):
        self.tracker: WindowTracker = WindowTracker()
        self.tracker_thread: Optional[Thread] = None
        self.tracker_lock: Lock = Lock()
    
    def start_tracking(self) -> tuple[Dict[str, Any], int]:
        """Start window tracking with specified interval."""
        with self.tracker_lock:
            if self.tracker.tracking:
                return {
                    'status': 'error',
                    'message': 'Tracking already running',
                    'start_time': self._get_start_time_iso()
                }, HTTP_BAD_REQUEST

            try:
                data = request.get_json(silent=True) or {}
                interval = data.get('interval', DEFAULT_INTERVAL)
                if isinstance(interval, tuple):  # Error response
                    return interval
                
                self.tracker_thread = Thread(
                    target=self.tracker.track_window_usage, 
                    kwargs={'interval': interval}
                )
                self.tracker_thread.daemon = True
                self.tracker_thread.start()
                
                logger.info(f"Tracking started with interval: {interval} seconds.")
                
                return {
                    'status': 'success',
                    'message': 'Tracking started',
                    'interval': interval,
                    'start_time': self._get_start_time_iso()
                }, HTTP_OK
                
            except Exception as e:
                logger.error(f"Error starting tracking: {e}")
                return {
                    'status': 'error',
                    'message': f"Failed to start tracking: {e}"
                }, HTTP_INTERNAL_SERVER_ERROR
    
    def stop_tracking(self) -> tuple[Dict[str, Any], int]:
        """Stop active window tracking."""
        with self.tracker_lock:
            if not self.tracker.tracking:
                return {
                    'status': 'error',
                    'message': 'No active tracking session to stop.'
                }, HTTP_BAD_REQUEST
            
            try:
                self.tracker.stop_tracking()
                if self.tracker_thread and self.tracker_thread.is_alive():
                    self.tracker_thread.join(timeout=THREAD_JOIN_TIMEOUT)
                
                logger.info("Tracking stopped.")
                return {
                    'status': 'success',
                    'message': 'Tracking stopped',
                    'session_duration_seconds': self.tracker.get_session_duration(),
                    'start_time': self._get_start_time_iso(),
                    'end_time': self._get_end_time_iso()
                }, HTTP_OK
                
            except Exception as e:
                logger.error(f"Error stopping tracking: {e}")
                return {
                    'status': 'error',
                    'message': f"Failed to stop tracking: {e}"
                }, HTTP_INTERNAL_SERVER_ERROR
    
    def get_session_info(self) -> tuple[Dict[str, Any], int]:
        """Get current tracking session information."""
        with self.tracker_lock:
            return {
                'status': 'success',
                'data': {
                    'is_tracking': self.tracker.tracking,
                    'current_interval_seconds': getattr(self.tracker, 'interval', DEFAULT_INTERVAL),
                    'start_time': self._get_start_time_iso(),
                    'end_time': self._get_end_time_iso(),
                    'session_duration_seconds': self.tracker.get_session_duration(),
                    'total_focus_events': len(self.tracker.focus_history),
                    'unique_windows_tracked': len(self.tracker.window_id_to_info)
                }
            }, HTTP_OK
    
    def get_current_window(self) -> tuple[Dict[str, Any], int]:
        """Get currently active window information."""
        current_window = self.tracker._detect_active_window()
        print(current_window)
        if current_window:
            return {
                'status': 'success',
                'data': asdict(current_window),
                'timestamp': datetime.now().isoformat()
            }, HTTP_OK
        
        return {
            'status': 'error',
            'message': 'Unable to detect active window'
        }, HTTP_NOT_FOUND
    
    def get_all_captured_windows(self) -> tuple[Dict[str, Any], int]:
        """Get all captured window information."""
        with self.tracker_lock:
            captured_windows = [
                asdict(info) for info in self.tracker.window_id_to_info.values()
            ]
        
        return {
            'status': 'success',
            'data': captured_windows,
            'count': len(captured_windows),
            'timestamp': datetime.now().isoformat()
        }, HTTP_OK
    
    def get_focus_history(self) -> tuple[Dict[str, Any], int]:
        """Get window focus history with optional limit."""
        limit = min(
            int(request.args.get('limit', DEFAULT_HISTORY_LIMIT)), 
            MAX_HISTORY_LIMIT
        )
        
        with self.tracker_lock:
            history_data = [
                asdict(entry) for entry in self.tracker.focus_history[-limit:]
            ]
        
        return {
            'status': 'success',
            'data': history_data,
            'total_entries': len(self.tracker.focus_history)
        }, HTTP_OK
    
    def get_usage_summary(self) -> tuple[Dict[str, Any], int]:
        """Get categorized usage summary."""
        with self.tracker_lock:
            categorized_usage = self.tracker.get_categorized_usage()
            window_type_stats = self.tracker.get_window_stats_by_type()
        
        return {
            'status': 'success',
            'summary': categorized_usage,
            'window_types_summary': window_type_stats
        }, HTTP_OK
    
    def get_top_windows(self) -> tuple[Dict[str, Any], int]:
        """Get top windows by usage time."""
        limit = min(
            int(request.args.get('limit', DEFAULT_TOP_WINDOWS_LIMIT)), 
            MAX_TOP_WINDOWS_LIMIT
        )
        
        with self.tracker_lock:
            top_windows_data = self.tracker.get_top_windows(limit)
            formatted_top_windows = [
                {
                    'window_info': asdict(info), 
                    'usage_time_seconds': usage
                }
                for info, usage in top_windows_data
            ]
        
        return {
            'status': 'success',
            'data': formatted_top_windows,
            'total_unique_windows': len(self.tracker.window_id_to_info)
        }, HTTP_OK
    
    def _get_interval_from_request(self) -> int | tuple[Dict[str, Any], int]:
        """Extract and validate interval from request."""
        interval = request.json.get('interval', DEFAULT_INTERVAL) if request.json else DEFAULT_INTERVAL
        
        if not isinstance(interval, (int, float)) or interval <= 0:
            return {
                'status': 'error',
                'message': 'Invalid interval. Must be a positive number.'
            }, HTTP_BAD_REQUEST
        
        return int(interval)
    
    def _get_start_time_iso(self) -> Optional[str]:
        """Get start time in ISO format."""
        return (
            self.tracker.start_time.isoformat() 
            if hasattr(self.tracker, 'start_time') and self.tracker.start_time 
            else None
        )
    
    def _get_end_time_iso(self) -> Optional[str]:
        """Get end time in ISO format."""
        return (
            self.tracker.end_time.isoformat() 
            if hasattr(self.tracker, 'end_time') and self.tracker.end_time 
            else None
        )