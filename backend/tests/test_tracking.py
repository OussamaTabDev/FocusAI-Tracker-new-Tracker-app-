import time
from app.services.multi_window_tracker import MultiWindowTracker

def main():
    tracker = MultiWindowTracker()
    
    print("🔴 Tracking started for 20 seconds...\n")
    tracker.track_window_usage(interval=5)  # or use a thread if you want to stop it externally
    
    # Let it run for 20 seconds
    time.sleep(20)
    
    tracker.stop_tracking()
    
    print("\n🟢 Tracking stopped.")
    print(f"⏱️ Total session duration: {tracker.get_session_duration()} seconds\n")
    
    print("📊 Top 5 Windows:")
    for win in tracker.get_top_windows():
        print(f"  - {win['title']} ({win['app']}, {win['window_type']}): {win['usage_seconds']}s")

    print("\n📈 Window Usage by Type:")
    stats = tracker.get_window_stats_by_type()
    for wtype, duration in stats.items():
        print(f"  - {wtype}: {duration}s")

if __name__ == "__main__":
    main()
