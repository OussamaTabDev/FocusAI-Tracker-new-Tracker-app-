
# app/services/multi_window_tracker.py
import pygetwindow as gw
import psutil
import time
from datetime import datetime
from collections import defaultdict
from typing import List, Dict, Optional
import platform
try:
    import win32process
except ImportError:
    if platform.system() == 'Windows':
        print("Note: pywin32 not installed. Process names might not work properly.")

class MultiWindowTracker:
    def __init__(self):
        self.window_states = {}
        self.active_windows = []
        self.focus_history = []
        self.window_usage_time = defaultdict(int)
        self.tracking = False
        self.start_time = None
        self.end_time = None

    def get_process_name(self, window) -> str:
        try:
            if hasattr(window, '_hWnd'):
                if platform.system() == 'Windows':
                    try:
                        import win32process
                        hwnd = window._hWnd
                        _, pid = win32process.GetWindowThreadProcessId(hwnd)
                        process = psutil.Process(pid)
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
                            "pycharm64.exe": "PyCharm"
                        }
                        process_name = process.name()
                        return name_map.get(process_name, process_name)
                    except Exception:
                        pass
                
                # Fallback for non-Windows or if win32process fails
                try:
                    pid = window._hWnd
                    process = psutil.Process(pid)
                    return process.name()
                except (psutil.NoSuchProcess, AttributeError):
                    return ""
            return ""
        except Exception:
            return ""

    def get_z_order(self, window) -> int:
        try:
            all_windows = gw.getAllWindows()
            return all_windows.index(window)
        except ValueError:
            return -1

    def generic_parse_title(self, title: str) -> Dict[str, str]:
        parts = [part.strip() for part in title.split(" - ") if part.strip()]
        result = {
            "raw_title": title,
            "app": "",
            "context": "",
            "sub_app": "",
            "is_file_explorer": False,
            "simplified_path": title,
            "display_title": title,
            "window_type": "unknown"
        }

        if not parts:
            return result

        # Detect File Explorer windows
        is_file_explorer = (
            ("File Explorer" in title or 
             "Explorer" in title or 
             title.startswith(("C:\\", "D:\\", "E:\\", "F:\\", "/")) or
             ("\\" in title and not any(x in title.lower() for x in ["visual studio", "code", "chrome", "brave", "edge"]))
        ))

        if is_file_explorer:
            result['is_file_explorer'] = True
            result['app'] = "File Explorer"
            result['window_type'] = "file_manager"
            
            # Clean up the path display
            clean_path = title.replace("File Explorer", "").replace("Explorer", "").strip()
            path_parts = [p for p in clean_path.split("\\") if p.strip()]
            
            if len(path_parts) > 2:
                result['context'] = "\\".join(path_parts[-2:])
                result['simplified_path'] = f"File Explorer: {result['context']}"
            else:
                result['context'] = clean_path
                result['simplified_path'] = f"File Explorer: {clean_path}"
            
            result['display_title'] = result['simplified_path']
            return result

        # Original parsing logic for non-file-explorer windows
        if len(parts) == 1:
            result["context"] = parts[0]
        elif len(parts) == 2:
            result["context"] = parts[0]
            result["app"] = parts[1]
        else:
            result["context"] = " - ".join(parts[:-2])
            result["sub_app"] = parts[-2]
            result["app"] = parts[-1]

        # Special case: browser handling
        known_browsers = {"Brave", "Chrome", "Google Chrome", "Firefox", "Microsoft Edge", "Opera", "Chromium"}
        if result["app"] in known_browsers:
            result["browser_app"] = result["sub_app"]
            result["sub_app"] = ""
            result["app"] = "Browser"
            result["window_type"] = "browser"

        # Detect other common window types
        if "Visual Studio Code" in result.get("app", ""):
            result["window_type"] = "code_editor"
        elif "Terminal" in result.get("app", ""):
            result["window_type"] = "terminal"
        elif "PyCharm" in result.get("app", ""):
            result["window_type"] = "ide"

        result['display_title'] = f"{result.get('context', '')} - {result.get('app', '')}".strip(" - ")
        return result

    def capture_window_state(self) -> List[Dict]:
        all_windows = gw.getAllWindows()
        current_time = datetime.now()

        window_data = []
        for window in all_windows:
            if window.visible and window.title.strip():
                window_info = {
                    'id': id(window),
                    'title': window.title,
                    'position': (window.left, window.top),
                    'size': (window.width, window.height),
                    'is_minimized': window.isMinimized,
                    'is_maximized': window.isMaximized,
                    'is_active': window.isActive,
                    'process_name': self.get_process_name(window),
                    'timestamp': current_time.isoformat(),
                    'z_order': self.get_z_order(window)
                }
                parsed_info = self.generic_parse_title(window.title)
                window_info.update(parsed_info)
                window_data.append(window_info)
        return window_data

    def detect_active_window(self) -> Optional[Dict]:
        try:
            active_window = gw.getActiveWindow()
            if active_window:
                info = {
                    'id': id(active_window),
                    'title': active_window.title,
                    'process_name': self.get_process_name(active_window),
                    'timestamp': datetime.now().isoformat()
                }
                parsed = self.generic_parse_title(active_window.title)
                info.update(parsed)
                return info
        except Exception:
            pass
        return None

    def track_window_usage(self, interval: int = 5):
        """Continuously track the active window every `interval` seconds"""
        self.tracking = True
        self.start_time = datetime.now()
        while self.tracking:
            current_window = self.detect_active_window()
            if current_window:
                self.window_usage_time[current_window['id']] += interval
                self.focus_history.append(current_window)
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
        stats = defaultdict(int)
        for entry in self.focus_history:
            stats[entry.get('window_type', 'unknown')] += 5  # assuming 5s interval
        return dict(stats)

    def get_top_windows(self, n=5):
        sorted_windows = sorted(self.window_usage_time.items(), key=lambda x: -x[1])
        top_windows = []
        for window_id, usage_time in sorted_windows[:n]:
            window_info = next((w for w in self.focus_history if w['id'] == window_id), None)
            if window_info:
                top_windows.append({
                    'title': window_info.get('display_title', window_info['title']),
                    'usage_seconds': usage_time,
                    'app': window_info.get('app', 'Unknown'),
                    'window_type': window_info.get('window_type', 'unknown')
                })
        return top_windows










# ----------------------------------------------------------------------------------------------
# import pygetwindow as gw
# import psutil
# import time
# from datetime import datetime
# from collections import defaultdict
# from typing import List, Dict, Optional


# class MultiWindowTracker:
#     def __init__(self):
#         self.window_states = {}
#         self.active_windows = []
#         self.focus_history = []
#         self.window_usage_time = defaultdict(int)
#         self.tracking = True

#     def get_process_name(self, window) -> str:
#         try:
#             pid = window._hWnd if hasattr(window, '_hWnd') else None
#             if pid:
#                 process = psutil.Process(pid)
#                 name_map = {
#                     "Code.exe": "Visual Studio Code",
#                     "brave.exe": "Brave",
#                     "vlc.exe": "VLC media player"
#                 }
#                 process_name = process.name()
#                 return name_map.get(process_name, process_name)
#             return ""
#         except (psutil.NoSuchProcess, AttributeError):
#             return ""

#     def get_z_order(self, window) -> int:
#         try:
#             all_windows = gw.getAllWindows()
#             return all_windows.index(window)
#         except ValueError:
#             return -1

#     def generic_parse_title(self, title: str) -> Dict[str, str]:
#         parts = [part.strip() for part in title.split(" - ") if part.strip()]
#         result = {
#             "raw_title": title,
#             "app": "",
#             "context": "",
#             "sub_app": ""
#         }

#         if not parts:
#             return result

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
#         except Exception:
#             pass
#         return None

#     def track_window_usage(self, interval: int = 5):
#         """Continuously track the active window every `interval` seconds"""
#         self.tracking = True
#         while self.tracking:
#             current_window = self.detect_active_window()
#             if current_window:
#                 self.window_usage_time[current_window['id']] += interval
#                 self.focus_history.append(current_window)
#             time.sleep(interval)

#     def stop_tracking(self):
#         self.tracking = False
