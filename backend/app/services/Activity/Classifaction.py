import re
import pygetwindow as gw
from ..models.window import WindowInfo
from ..utils.system_utils import SystemUtils

class WindowClassifier:
    def __init__(self):
        self.system_utils = SystemUtils()
        self.categories = Categories()
    
    def classify_window(self, window) -> WindowInfo:
        """Classify a window and return WindowInfo object"""
        # Get basic window info
        extended_info = self.system_utils.get_window_extended_info(window)
        process_name = self.system_utils.get_process_name(window)
        
        # Create WindowInfo object
        window_info = WindowInfo(
            id=id(window),
            title=window.title,
            process_name=process_name,
            **extended_info
        )
        
        # Determine window type
        window_type = self._determine_window_type(
            window.title,
            window_info.class_name,
            process_name
        )
        window_info.window_type = window_type
        
        # Parse title and set additional flags
        self._parse_window_title(window_info)
        return window_info
    
    def _determine_window_type(self, title: str, class_name: str, process_name: str) -> str:
        """Determine the window type using categories"""
        # First check app mappings
        mapped_category = self.categories.get_mapped_category(process_name, title, class_name)
        if mapped_category:
            return mapped_category
        
        # Then check pattern matching
        return self.categories.match_patterns(title, class_name, process_name)
    
    def _parse_window_title(self, window_info: WindowInfo):
        """Parse window title and set additional flags"""
        # ... title parsing logic ...
        pass