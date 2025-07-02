import platform
import psutil
import logging
from typing import Dict, List, Optional , Any  

try:
    import win32process
    import win32gui
    import win32con
except ImportError:
    if platform.system() == 'Windows':
        print("Note: pywin32 not installed. Some features may not work.")

class SystemUtils:
    def get_window_extended_info(self, window) -> Dict[str, Any]:
        """Windows-specific window information"""
        info = {}
        if platform.system() == 'Windows' and hasattr(window, '_hWnd'):
            try:
                hwnd = window._hWnd
                info['class_name'] = win32gui.GetClassName(hwnd)
                info['parent_hwnd'] = win32gui.GetParent(hwnd)
                info['window_style'] = win32gui.GetWindowLong(hwnd, win32con.GWL_STYLE)
                info['extended_style'] = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
                info['is_system_window'] = (
                    info['extended_style'] & win32con.WS_EX_TOOLWINDOW or
                    info['window_style'] & win32con.WS_POPUP
                )
                info['is_topmost'] = bool(info['extended_style'] & win32con.WS_EX_TOPMOST)
            except Exception as e:
                logging.warning(f"Error getting extended window info: {e}")
        return info
    
    def get_process_name(self, window) -> str:
        """Get process name with enhanced mapping"""
        try:
            if hasattr(window, '_hWnd'):
                if platform.system() == 'Windows':
                    try:
                        _, pid = win32process.GetWindowThreadProcessId(window._hWnd)
                        process = psutil.Process(pid)
                        return self._map_process_name(process.name())
                    except Exception:
                        pass
                
                # Fallback for non-Windows
                try:
                    pid = window._hWnd
                    process = psutil.Process(pid)
                    return process.name()
                except (psutil.NoSuchProcess, AttributeError):
                    pass
        except Exception as e:
            logging.error(f"Unexpected error in get_process_name: {e}")
        return ""
    
    def _map_process_name(self, name: str) -> str:
        """Map process names to more friendly names"""
        name_map = {
            "Code.exe": "Visual Studio Code",
            "explorer.exe": "File Explorer",
            "brave.exe": "Brave",
            "vlc.exe": "VLC media player",
            "explorer.exe": "File Explorer",
            "chrome.exe": "Chrome",
            "firefox.exe": "Firefox",
            "msedge.exe": "Edge",
            "notepad.exe": "Notepad",
            "devenv.exe": "Visual Studio",
            "pycharm64.exe": "PyCharm",
            # ... other mappings ...
        }
        return name_map.get(name, name)