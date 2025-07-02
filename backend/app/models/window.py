from dataclasses import dataclass
from typing import Tuple, Dict, Any

@dataclass
class WindowInfo:
    id: int
    title: str
    process_name: str
    class_name: str = ""
    parent_hwnd: int = 0
    window_style: int = 0
    extended_style: int = 0
    is_system_window: bool = False
    is_topmost: bool = False
    window_type: str = "unknown"
    is_search_window: bool = False
    is_dialog: bool = False
    is_file_explorer: bool = False
    display_title: str = ""
    
    def __post_init__(self):
        if not self.display_title:
            self.display_title = self.title