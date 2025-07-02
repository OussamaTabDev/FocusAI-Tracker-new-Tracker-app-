import time
from datetime import datetime
from threading import Thread, Lock
from typing import Dict, List, Optional , Any 
from collections import defaultdict
import logging
from ...models.window import WindowInfo
from .Classifaction import WindowClassifier
from ...services.Storage.category_storage import CategoryStorage
import pygetwindow as gw

class WindowTracker:
    def __init__(self):
        self.window_usage_time = defaultdict(int)
        self.focus_history = []
        self.window_id_to_info = {}
        self.system_windows_detected = set()
        self.tracking = False
        self.interval = 5
        self.lock = Lock()
        
        # Dependencies
        self.classifier = WindowClassifier()
        self.storage = CategoryStorage()
        
        logging.basicConfig(level=logging.INFO)
    
    def track_window_usage(self, interval: int = 5):
        """Main tracking loop"""
        self.tracking = True
        self.interval = interval
        self.start_time = datetime.now()
        
        while self.tracking:
            current_window = self._detect_active_window()
            if current_window:
                with self.lock:
                    self._update_window_stats(current_window)
            time.sleep(interval)
        
        self.end_time = datetime.now()
    
    def _update_window_stats(self, window_info: WindowInfo):
        """Update tracking statistics for a window"""
        window_id = window_info.id
        self.window_usage_time[window_id] += self.interval
        self.focus_history.append(window_info)
        self.window_id_to_info[window_id] = window_info
        
        if window_info.is_system_window:
            self.system_windows_detected.add(window_id)
    
    def _detect_active_window(self) -> Optional[WindowInfo]:
        """Detect and classify the active window"""
        try:
            active_window = gw.getActiveWindow()
            if active_window:
                return self.classifier.classify_window(active_window)
        except Exception as e:
            logging.warning(f"Error in detect_active_window: {e}")
        return None
    
    # ... rest of the tracking methods (get_top_windows, get_session_duration, etc.) ...
    def get_top_windows(self, n=5, include_system=True):
        """Enhanced top windows with option to include/exclude system windows"""
        with self.lock:
            if include_system:
                items = list(self.window_usage_time.items())
            else:
                items = [(wid, time) for wid, time in self.window_usage_time.items() 
                        if wid not in self.system_windows_detected]
            
            sorted_windows = sorted(items, key=lambda x: -x[1])
            top_windows = []
            
            for window_id, usage_time in sorted_windows[:n]:
                window_info = self.window_id_to_info.get(window_id)
                if window_info:
                    top_windows.append({
                        'title': window_info.get('display_title', window_info['title']),
                        'usage_seconds': usage_time,
                        'app': window_info.get('app', 'Unknown'),
                        'window_type': window_info.get('window_type', 'unknown'),
                        'is_system_window': window_info.get('is_system_window', False),
                        'process_name': window_info.get('process_name', '')
                    })
        return top_windows

    

    def stop_tracking(self):
        """Stops the main tracking loop."""
        
        self.tracking = False
        logging.info("Tracking stop requested.")

    def get_session_duration(self) -> float:
        """Calculate the duration of the current/last tracking session in seconds."""
        if hasattr(self, 'start_time') and hasattr(self, 'end_time') and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        elif hasattr(self, 'start_time') and self.tracking:
            return (datetime.now() - self.start_time).total_seconds()
        return 0.0

    

    def get_categorized_usage(self) -> Dict[str, int]:
        """Calculates total usage time per category."""
        categorized_usage = defaultdict(int)
        with self.lock: # Ensure thread-safe access to window_usage_time and window_id_to_info
            for window_id, usage_time in self.window_usage_time.items():
                window_info = self.window_id_to_info.get(window_id)
                if window_info and window_info.window_type:
                    categorized_usage[window_info.window_type] += usage_time
                else:
                    categorized_usage['unclassified'] += usage_time # Fallback for unclassified
        return dict(categorized_usage)

    def get_window_stats_by_type(self) -> Dict[str, Dict[str, Any]]:
        """Returns statistics about windows by their type (count, total usage)."""
        stats = defaultdict(lambda: {'count': 0, 'total_usage_seconds': 0})
        with self.lock:
            for window_id, usage_time in self.window_usage_time.items():
                window_info = self.window_id_to_info.get(window_id)
                if window_info and window_info.window_type:
                    window_type = window_info.window_type
                    stats[window_type]['count'] += 1
                    stats[window_type]['total_usage_seconds'] += usage_time
                else:
                    stats['unclassified']['count'] += 1
                    stats['unclassified']['total_usage_seconds'] += usage_time
        return dict(stats)