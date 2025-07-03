import pygetwindow as gw

active = gw.getActiveWindow()
print("Active window:", active)
if active:
    print("Title:", active.title)
    print("hWnd:", getattr(active, '_hWnd', None))