# app/services/enhanced_multi_window_tracker.py
import pygetwindow as gw
import psutil
import time
import re
from datetime import datetime
from collections import defaultdict
from typing import List, Dict, Optional, Tuple
import platform
import threading
import logging

try:
    import win32process
    import win32gui
    import win32con
except ImportError:
    if platform.system() == 'Windows':
        print("Note: pywin32 not installed. Advanced Windows features might not work properly.")

class EnhancedMultiWindowTracker:
    def __init__(self):
        self.window_states = {}
        self.active_windows = []
        self.focus_history = []
        self.window_usage_time = defaultdict(int)
        self.tracking = False
        self.start_time = None
        self.end_time = None
        self.interval = 5
        self.lock = threading.Lock()
        self.window_id_to_info = {}
        self.system_windows_detected = set()
        logging.basicConfig(level=logging.INFO)
        
        # Enhanced window classification patterns
        self.window_patterns = {
            'search': [
                r'search', r'find', r'cortana', r'spotlight', r'launcher',
                r'start menu', r'taskbar', r'windows search'
            ],
            'system_dialog': [
                r'dialog', r'properties', r'settings', r'control panel',
                r'preferences', r'options', r'configuration'
            ],
            'file_manager': [
                r'explorer', r'file manager', r'nautilus', r'dolphin',
                r'thunar', r'pcmanfm', r'finder'
            ],
            'terminal': [
                r'terminal', r'cmd', r'powershell', r'bash', r'zsh',
                r'command prompt', r'konsole', r'gnome-terminal'
            ],
            'notification': [
                r'notification', r'alert', r'popup', r'toast',
                r'banner', r'reminder'
            ],
            'system_tray': [
                r'system tray', r'notification area', r'taskbar',
                r'panel', r'dock'
            ]
        }

    def get_window_class_name(self, window) -> str:
        """Get the window class name (Windows specific)"""
        try:
            if platform.system() == 'Windows' and hasattr(window, '_hWnd'):
                import win32gui
                class_name = win32gui.GetClassName(window._hWnd)
                return class_name if class_name else ""
        except Exception as e:
            logging.warning(f"Error getting window class: {e}")
        return ""

    def get_window_extended_info(self, window) -> Dict:
        """Get extended window information including parent, style, etc."""
        info = {}
        try:
            if platform.system() == 'Windows' and hasattr(window, '_hWnd'):
                import win32gui
                import win32con
                
                hwnd = window._hWnd
                info['class_name'] = win32gui.GetClassName(hwnd)
                info['parent_hwnd'] = win32gui.GetParent(hwnd)
                info['window_style'] = win32gui.GetWindowLong(hwnd, win32con.GWL_STYLE)
                info['extended_style'] = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
                
                # Check if it's a system window
                info['is_system_window'] = (
                    info['extended_style'] & win32con.WS_EX_TOOLWINDOW or
                    info['window_style'] & win32con.WS_POPUP
                )
                
                # Check if it's always on top
                info['is_topmost'] = bool(info['extended_style'] & win32con.WS_EX_TOPMOST)
                
        except Exception as e:
            logging.warning(f"Error getting extended window info: {e}")
        
        return info

    def get_process_name(self, window) -> str:
        try:
            if hasattr(window, '_hWnd'):
                if platform.system() == 'Windows':
                    try:
                        import win32process
                        hwnd = window._hWnd
                        _, pid = win32process.GetWindowThreadProcessId(hwnd)
                        process = psutil.Process(pid)
                        
                        # Enhanced name mapping for system processes
                        name_map = {
                            "Code.exe": "Visual Studio Code",
                            "brave.exe": "Brave",
                            "vlc.exe": "VLC media player",
                            "explorer.exe": "File Explorer",
                            "chrome.exe": "Chrome",
                            "firefox.exe": "Firefox",
                            "msedge.exe": "Edge",
                            "notepad.exe": "Notepad",
                            "devenv.exe": "Visual Studio",
                            "pycharm64.exe": "PyCharm",
                            "SearchUI.exe": "Windows Search",
                            "StartMenuExperienceHost.exe": "Start Menu",
                            "ShellExperienceHost.exe": "Windows Shell",
                            "SystemSettings.exe": "Windows Settings",
                            "winlogon.exe": "Windows Logon",
                            "dwm.exe": "Desktop Window Manager",
                            "rundll32.exe": "Windows System Process",
                            "svchost.exe": "Windows Service Host",
                            "cortana.exe": "Cortana",
                            "SearchApp.exe": "Windows Search App"
                        }
                        process_name = process.name()
                        return name_map.get(process_name, process_name)
                    except Exception as e:
                        logging.warning(f"Error getting process name (win32process): {e}")
                
                # Fallback for non-Windows or when win32process fails
                try:
                    pid = window._hWnd
                    process = psutil.Process(pid)
                    return process.name()
                except (psutil.NoSuchProcess, AttributeError) as e:
                    logging.warning(f"Error getting process name (fallback): {e}")
                    return ""
            return ""
        except Exception as e:
            logging.error(f"Unexpected error in get_process_name: {e}")
            return ""

    def classify_window_type(self, title: str, class_name: str = "", process_name: str = "") -> str:
        """Enhanced window type classification"""
        title_lower = title.lower()
        class_lower = class_name.lower()
        process_lower = process_name.lower()
        
        # Check each pattern category
        for window_type, patterns in self.window_patterns.items():
            for pattern in patterns:
                if (re.search(pattern, title_lower) or 
                    re.search(pattern, class_lower) or 
                    re.search(pattern, process_lower)):
                    return window_type
        
        # # Additional specific checks
        if any(keyword in title_lower for keyword in ['search', 'find', 'cortana']):
            return 'search'
        
        if any(keyword in title_lower for keyword in ['properties', 'settings', 'control']):
            return 'system_dialog'
        
        if any(keyword in process_lower for keyword in ['explorer', 'file']):
            return 'file_manager'
        
        if any(keyword in title_lower for keyword in ['terminal', 'cmd', 'powershell']):
            return 'terminal'
        
        # Browser detection
        if any(browser in process_lower for browser in ['chrome', 'firefox', 'edge', 'brave', 'opera']):
            return 'browser'
        
        # Code editor detection
        if any(editor in process_lower for editor in ['code', 'pycharm', 'sublime', 'atom', 'vim']):
            return 'code_editor'
        
        return 'application'

    def enhanced_parse_title(self, title: str, window_info: Dict) -> Dict[str, str]:
        """Enhanced title parsing with better system window detection"""
        parts = [part.strip() for part in title.split(" - ") if part.strip()]
        
        result = {
            "raw_title": title,
            "app": "",
            "context": "",
            "sub_app": "",
            "is_file_explorer": False,
            "is_system_window": False,
            "is_search_window": False,
            "is_dialog": False,
            "simplified_path": title,
            "display_title": title,
            "window_type": "unknown",
            "class_name": window_info.get('class_name', ''),
            "process_name": window_info.get('process_name', ''),
            "parent_window": window_info.get('parent_hwnd', 0) != 0
        }

        # Determine window type using enhanced classification
        result['window_type'] = self.classify_window_type(
            title, 
            result['class_name'], 
            result['process_name']
        )

        # Set specific flags based on window type
        result['is_search_window'] = result['window_type'] == 'search'
        result['is_dialog'] = result['window_type'] == 'system_dialog'
        result['is_system_window'] = result['window_type'] in ['search', 'system_dialog', 'notification', 'system_tray']
        result['is_file_explorer'] = result['window_type'] == 'file_manager'

        # Enhanced File Explorer detection and parsing
        if result['is_file_explorer'] or any(keyword in title.lower() for keyword in ['file explorer', 'explorer']):
            result['is_file_explorer'] = True
            result['app'] = "File Explorer"
            result['window_type'] = "File Explorer"
            
            clean_path = title.replace("File Explorer", "").replace("Explorer", "").strip()
            if clean_path.startswith(("C:\\", "D:\\", "E:\\", "F:\\", "/")):
                path_parts = [p for p in clean_path.split("\\") if p.strip()]
                if len(path_parts) > 2:
                    result['context'] = "\\".join(path_parts[-2:])
                    result['simplified_path'] = f"File Explorer: {result['context']}"
                else:
                    result['context'] = clean_path
                    result['simplified_path'] = f"File Explorer: {clean_path}"
            else:
                result['simplified_path'] = f"File Explorer: {clean_path}"
            
            result['display_title'] = result['simplified_path']
            return result

        # Enhanced Search Window handling
        if result['is_search_window']:
            result['app'] = "Search"
            if "windows search" in title.lower() or "cortana" in title.lower():
                result['app'] = "Windows Search"
            elif "spotlight" in title.lower():
                result['app'] = "Spotlight Search"
            
            result['display_title'] = f"{result['app']}: {title}"
            return result

        # Enhanced System Dialog handling
        if result['is_dialog']:
            result['app'] = "System Dialog"
            if "properties" in title.lower():
                result['app'] = "Properties"
            elif "settings" in title.lower():
                result['app'] = "Settings"
            elif "control panel" in title.lower():
                result['app'] = "Control Panel"
            
            result['display_title'] = f"{result['app']}: {title}"
            return result

        # Original parsing logic for regular applications
        if not parts:
            result['context'] = title
            result['display_title'] = title
            return result

        if len(parts) == 1:
            result["context"] = parts[0]
        elif len(parts) == 2:
            result["context"] = parts[0]
            result["app"] = parts[1]
        else:
            result["context"] = " - ".join(parts[:-2])
            result["sub_app"] = parts[-2]
            result["app"] = parts[-1]

        # Browser handling
        known_browsers = {"Brave", "Chrome", "Google Chrome", "Firefox", "Microsoft Edge", "Opera", "Chromium"}
        if result["app"] in known_browsers:
            result["browser_app"] = result["sub_app"]
            result["sub_app"] = ""
            result["app"] = f"Browser ({result['app']})"

        result['display_title'] = f"{result.get('context', '')} - {result.get('app', '')}".strip(" - ")
        
        return result

    def capture_window_state(self) -> List[Dict]:
        """Enhanced window state capture with system window detection"""
        all_windows = gw.getAllWindows()
        current_time = datetime.now()
        window_data = []
        
        for window in all_windows:
            if window.title.strip():  # Include invisible windows that might be system windows
                try:
                    # Get extended window information
                    extended_info = self.get_window_extended_info(window)
                    
                    window_info = {
                        'id': id(window),
                        'title': window.title,
                        'position': (window.left, window.top),
                        'size': (window.width, window.height),
                        'is_minimized': window.isMinimized,
                        'is_maximized': window.isMaximized,
                        'is_active': window.isActive,
                        'is_visible': window.visible,
                        'process_name': self.get_process_name(window),
                        'timestamp': current_time.isoformat(),
                        'z_order': self.get_z_order(window),
                        **extended_info
                    }
                    
                    # Enhanced parsing
                    parsed_info = self.enhanced_parse_title(window.title, window_info)
                    window_info.update(parsed_info)
                    
                    # Track system windows separately
                    if window_info.get('is_system_window'):
                        self.system_windows_detected.add(window_info['id'])
                    
                    window_data.append(window_info)
                    
                except Exception as e:
                    logging.warning(f"Error processing window '{window.title}': {e}")
                    continue
        
        return window_data

    def get_z_order(self, window) -> int:
        try:
            all_windows = gw.getAllWindows()
            return all_windows.index(window)
        except ValueError:
            return -1
        except Exception as e:
            logging.error(f"Error in get_z_order: {e}")
            return -1

    def detect_active_window(self) -> Optional[Dict]:
        try:
            active_window = gw.getActiveWindow()
            if active_window:
                extended_info = self.get_window_extended_info(active_window)
                
                info = {
                    'id': id(active_window),
                    'title': active_window.title,
                    'process_name': self.get_process_name(active_window),
                    'timestamp': datetime.now().isoformat(),
                    **extended_info
                }
                
                parsed = self.enhanced_parse_title(active_window.title, info)
                info.update(parsed)
                return info
        except Exception as e:
            logging.warning(f"Error in detect_active_window: {e}")
        return None

    def track_window_usage(self, interval: int = 5):
        """Enhanced window usage tracking"""
        self.tracking = True
        self.interval = interval
        self.start_time = datetime.now()
        
        while self.tracking:
            current_window = self.detect_active_window()
            if current_window:
                with self.lock:
                    self.window_usage_time[current_window['id']] += interval
                    self.focus_history.append(current_window)
                    self.window_id_to_info[current_window['id']] = current_window
            time.sleep(interval)
        
        self.end_time = datetime.now()

    def stop_tracking(self):
        self.tracking = False

    def get_session_duration(self):
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        elif self.start_time:
            return (datetime.now() - self.start_time).total_seconds()
        return 0

    def get_window_stats_by_type(self):
        """Enhanced statistics with system window categories"""
        stats = defaultdict(int)
        with self.lock:
            for entry in self.focus_history:
                window_type = entry.get('window_type', 'unknown')
                stats[window_type] += self.interval
        return dict(stats)

    def get_system_window_stats(self):
        """Get statistics specifically for system windows"""
        system_stats = defaultdict(int)
        with self.lock:
            for entry in self.focus_history:
                if entry.get('is_system_window', False):
                    window_type = entry.get('window_type', 'unknown')
                    system_stats[window_type] += self.interval
        return dict(system_stats)

    def get_search_window_usage(self):
        """Get usage statistics for search windows specifically"""
        search_usage = []
        with self.lock:
            for entry in self.focus_history:
                if entry.get('is_search_window', False):
                    search_usage.append({
                        'title': entry.get('display_title', entry['title']),
                        'timestamp': entry['timestamp'],
                        'app': entry.get('app', 'Search'),
                        'process_name': entry.get('process_name', '')
                    })
        return search_usage

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

    def get_window_summary(self):
        """Get a comprehensive summary of window usage"""
        total_time = self.get_session_duration()
        window_stats = self.get_window_stats_by_type()
        system_stats = self.get_system_window_stats()
        top_windows = self.get_top_windows(10)
        
        return {
            'session_duration': total_time,
            'total_windows_tracked': len(self.window_id_to_info),
            'window_type_stats': window_stats,
            'system_window_stats': system_stats,
            'top_windows': top_windows,
            'system_windows_detected': len(self.system_windows_detected),
            'search_window_usage': self.get_search_window_usage()
        }


# # app/services/multi_window_tracker.py
# import pygetwindow as gw
# import psutil
# import time
# from datetime import datetime
# from collections import defaultdict
# from typing import List, Dict, Optional
# import platform
# import threading
# import logging
# try:
#     import win32process
# except ImportError:
#     if platform.system() == 'Windows':
#         print("Note: pywin32 not installed. Process names might not work properly.")

# class MultiWindowTracker:
#     def __init__(self):
#         self.window_states = {}
#         self.active_windows = []
#         self.focus_history = []
#         self.window_usage_time = defaultdict(int)
#         self.tracking = False
#         self.start_time = None
#         self.end_time = None
#         self.interval = 5  # Default interval
#         self.lock = threading.Lock()
#         self.window_id_to_info = {}  # For fast lookup in get_top_windows
#         logging.basicConfig(level=logging.INFO)

#     def get_process_name(self, window) -> str:
#         try:
#             if hasattr(window, '_hWnd'):
#                 if platform.system() == 'Windows':
#                     try:
#                         import win32process
#                         hwnd = window._hWnd
#                         _, pid = win32process.GetWindowThreadProcessId(hwnd)
#                         process = psutil.Process(pid)
#                         name_map = {
#                             "Code.exe": "Visual Studio Code",
#                             "brave.exe": "Brave",
#                             "vlc.exe": "VLC media player",
#                             "explorer.exe": "File Explorer",
#                             "chrome.exe": "Chrome",
#                             "firefox.exe": "Firefox",
#                             "msedge.exe": "Edge",
#                             "notepad.exe": "Notepad",
#                             "devenv.exe": "Visual Studio",
#                             "pycharm64.exe": "PyCharm"
#                         }
#                         process_name = process.name()
#                         return name_map.get(process_name, process_name)
#                     except Exception as e:
#                         logging.warning(f"Error getting process name (win32process): {e}")
#                 try:
#                     pid = window._hWnd
#                     process = psutil.Process(pid)
#                     return process.name()
#                 except (psutil.NoSuchProcess, AttributeError) as e:
#                     logging.warning(f"Error getting process name (fallback): {e}")
#                     return ""
#             return ""
#         except Exception as e:
#             logging.error(f"Unexpected error in get_process_name: {e}")
#             return ""

#     def get_z_order(self, window) -> int:
#         try:
#             all_windows = gw.getAllWindows()
#             return all_windows.index(window)
#         except ValueError:
#             return -1
#         except Exception as e:
#             logging.error(f"Error in get_z_order: {e}")
#             return -1

#     def generic_parse_title(self, title: str) -> Dict[str, str]:
#         parts = [part.strip() for part in title.split(" - ") if part.strip()]
#         result = {
#             "raw_title": title,
#             "app": "",
#             "context": "",
#             "sub_app": "",
#             "is_file_explorer": False,
#             "simplified_path": title,
#             "display_title": title,
#             "window_type": "unknown"
#         }

#         if not parts:
#             return result

#         # Detect File Explorer windows
#         is_file_explorer = (
#             ("File Explorer" in title or 
#              "Explorer" in title or 
#              title.startswith(("C:\\", "D:\\", "E:\\", "F:\\", "/")) or
#              ("\\" in title and not any(x in title.lower() for x in ["visual studio", "code", "chrome", "brave", "edge"]))
#         ))

#         if is_file_explorer:
#             result['is_file_explorer'] = True
#             result['app'] = "File Explorer"
#             result['window_type'] = "file_manager"
            
#             # Clean up the path display
#             clean_path = title.replace("File Explorer", "").replace("Explorer", "").strip()
#             path_parts = [p for p in clean_path.split("\\") if p.strip()]
            
#             if len(path_parts) > 2:
#                 result['context'] = "\\".join(path_parts[-2:])
#                 result['simplified_path'] = f"File Explorer: {result['context']}"
#             else:
#                 result['context'] = clean_path
#                 result['simplified_path'] = f"File Explorer: {clean_path}"
            
#             result['display_title'] = result['simplified_path']
#             return result

#         # Original parsing logic for non-file-explorer windows
#         if len(parts) == 1:
#             result["context"] = parts[0]
#         elif len(parts) == 2:
#             result["context"] = parts[0]
#             result["app"] = parts[1]
#         else:
#             result["context"] = " - ".join(parts[:-2])
#             result["sub_app"] = parts[-2]
#             result["app"] = parts[-1]

#         # Special case: browser handling
#         known_browsers = {"Brave", "Chrome", "Google Chrome", "Firefox", "Microsoft Edge", "Opera", "Chromium"}
#         if result["app"] in known_browsers:
#             result["browser_app"] = result["sub_app"]
#             result["sub_app"] = ""
#             result["app"] = "Browser"
#             result["window_type"] = "browser"

#         # Detect other common window types
#         if "Visual Studio Code" in result.get("app", ""):
#             result["window_type"] = "code_editor"
#         elif "Terminal" in result.get("app", ""):
#             result["window_type"] = "terminal"
#         elif "PyCharm" in result.get("app", ""):
#             result["window_type"] = "ide"

#         result['display_title'] = f"{result.get('context', '')} - {result.get('app', '')}".strip(" - ")
#         return result

#     def capture_window_state(self) -> List[Dict]:
#         all_windows = gw.getAllWindows()
#         current_time = datetime.now()
#         window_data = []
#         for window in all_windows:
#             if window.visible and window.title.strip():
#                 window_info = {
#                     'id': id(window),
#                     'title': window.title,
#                     'position': (window.left, window.top),
#                     'size': (window.width, window.height),
#                     'is_minimized': window.isMinimized,
#                     'is_maximized': window.isMaximized,
#                     'is_active': window.isActive,
#                     'process_name': self.get_process_name(window),
#                     'timestamp': current_time.isoformat(),
#                     'z_order': self.get_z_order(window)
#                 }
#                 parsed_info = self.generic_parse_title(window.title)
#                 window_info.update(parsed_info)
#                 window_data.append(window_info)
#         return window_data

#     def detect_active_window(self) -> Optional[Dict]:
#         try:
#             active_window = gw.getActiveWindow()
#             if active_window:
#                 info = {
#                     'id': id(active_window),
#                     'title': active_window.title,
#                     'process_name': self.get_process_name(active_window),
#                     'timestamp': datetime.now().isoformat()
#                 }
#                 parsed = self.generic_parse_title(active_window.title)
#                 info.update(parsed)
#                 return info
#         except Exception as e:
#             logging.warning(f"Error in detect_active_window: {e}")
#         return None

#     def track_window_usage(self, interval: int = 5):
#         """Continuously track the active window every `interval` seconds"""
#         self.tracking = True
#         self.interval = interval
#         self.start_time = datetime.now()
#         while self.tracking:
#             current_window = self.detect_active_window()
#             if current_window:
#                 with self.lock:
#                     self.window_usage_time[current_window['id']] += interval
#                     self.focus_history.append(current_window)
#                     self.window_id_to_info[current_window['id']] = current_window
#             time.sleep(interval)
#         self.end_time = datetime.now()

#     def stop_tracking(self):
#         self.tracking = False

#     def get_session_duration(self):
#         if self.start_time and self.end_time:
#             return (self.end_time - self.start_time).total_seconds()
#         elif self.start_time:
#             return (datetime.now() - self.start_time).total_seconds()
#         return 0

#     def get_window_stats_by_type(self):
#         stats = defaultdict(int)
#         with self.lock:
#             for entry in self.focus_history:
#                 stats[entry.get('window_type', 'unknown')] += self.interval
#         return dict(stats)

#     def get_top_windows(self, n=5):
#         with self.lock:
#             sorted_windows = sorted(self.window_usage_time.items(), key=lambda x: -x[1])
#             top_windows = []
#             for window_id, usage_time in sorted_windows[:n]:
#                 window_info = self.window_id_to_info.get(window_id)
#                 if window_info:
#                     top_windows.append({
#                         'title': window_info.get('display_title', window_info['title']),
#                         'usage_seconds': usage_time,
#                         'app': window_info.get('app', 'Unknown'),
#                         'window_type': window_info.get('window_type', 'unknown')
#                     })
#         return top_windows










# # ----------------------------------------------------------------------------------------------
# # import pygetwindow as gw
# # import psutil
# # import time
# # from datetime import datetime
# # from collections import defaultdict
# # from typing import List, Dict, Optional


# # class MultiWindowTracker:
# #     def __init__(self):
# #         self.window_states = {}
# #         self.active_windows = []
# #         self.focus_history = []
# #         self.window_usage_time = defaultdict(int)
# #         self.tracking = True

# #     def get_process_name(self, window) -> str:
# #         try:
# #             pid = window._hWnd if hasattr(window, '_hWnd') else None
# #             if pid:
# #                 process = psutil.Process(pid)
# #                 name_map = {
# #                     "Code.exe": "Visual Studio Code",
# #                     "brave.exe": "Brave",
# #                     "vlc.exe": "VLC media player"
# #                 }
# #                 process_name = process.name()
# #                 return name_map.get(process_name, process_name)
# #             return ""
# #         except (psutil.NoSuchProcess, AttributeError):
# #             return ""

# #     def get_z_order(self, window) -> int:
# #         try:
# #             all_windows = gw.getAllWindows()
# #             return all_windows.index(window)
# #         except ValueError:
# #             return -1

# #     def generic_parse_title(self, title: str) -> Dict[str, str]:
# #         parts = [part.strip() for part in title.split(" - ") if part.strip()]
# #         result = {
# #             "raw_title": title,
# #             "app": "",
# #             "context": "",
# #             "sub_app": ""
# #         }

# #         if not parts:
# #             return result

# #         if len(parts) == 1:
# #             result["context"] = parts[0]
# #         elif len(parts) == 2:
# #             result["context"] = parts[0]
# #             result["app"] = parts[1]
# #         else:
# #             result["context"] = " - ".join(parts[:-2])
# #             result["sub_app"] = parts[-2]
# #             result["app"] = parts[-1]

# #         # Special case: browser handling
# #         known_browsers = {"Brave", "Chrome", "Google Chrome", "Firefox", "Microsoft Edge", "Opera", "Chromium"}
# #         if result["app"] in known_browsers:
# #             result["browser_app"] = result["sub_app"]
# #             result["sub_app"] = ""
# #             result["app"] = "Browser"

# #         return result

# #     def capture_window_state(self) -> List[Dict]:
# #         all_windows = gw.getAllWindows()
# #         current_time = datetime.now()

# #         window_data = []
# #         for window in all_windows:
# #             if window.visible and window.title.strip():
# #                 window_info = {
# #                     'id': id(window),
# #                     'title': window.title,
# #                     'position': (window.left, window.top),
# #                     'size': (window.width, window.height),
# #                     'is_minimized': window.isMinimized,
# #                     'is_maximized': window.isMaximized,
# #                     'is_active': window.isActive,
# #                     'process_name': self.get_process_name(window),
# #                     'timestamp': current_time.isoformat(),
# #                     'z_order': self.get_z_order(window)
# #                 }
# #                 parsed_info = self.generic_parse_title(window.title)
# #                 window_info.update(parsed_info)
# #                 window_data.append(window_info)
# #         return window_data

# #     def detect_active_window(self) -> Optional[Dict]:
# #         try:
# #             active_window = gw.getActiveWindow()
# #             if active_window:
# #                 info = {
# #                     'id': id(active_window),
# #                     'title': active_window.title,
# #                     'process_name': self.get_process_name(active_window),
# #                     'timestamp': datetime.now().isoformat()
# #                 }
# #                 parsed = self.generic_parse_title(active_window.title)
# #                 info.update(parsed)
# #                 return info
# #         except Exception:
# #             pass
# #         return None

# #     def track_window_usage(self, interval: int = 5):
# #         """Continuously track the active window every `interval` seconds"""
# #         self.tracking = True
# #         while self.tracking:
# #             current_window = self.detect_active_window()
# #             if current_window:
# #                 self.window_usage_time[current_window['id']] += interval
# #                 self.focus_history.append(current_window)
# #             time.sleep(interval)

# #     def stop_tracking(self):
# #         self.tracking = False
