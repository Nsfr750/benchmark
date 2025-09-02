"""Manual test for HardwareMonitor."""
import sys
import os
import time

# Add the parent directory to the path so we can import script
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from script.test_script.hardware_monitor import HardwareMonitor

def test_monitor():
    print("Starting hardware monitor test...")
    monitor = HardwareMonitor(interval=0.1)
    
    print("Starting monitoring...")
    monitor.start()
    
    print("Running for 2 seconds...")
    time.sleep(2)
    
    print("Stopping monitoring...")
    monitor.stop()
    
    print(f"\nCollected {len(monitor.metrics)} data points")
    
    if monitor.metrics:
        print("\nFirst metric:")
        for k, v in vars(monitor.metrics[0]).items():
            print(f"  {k}: {v}")
            
        print("\nLast metric:")
        for k, v in vars(monitor.metrics[-1]).items():
            print(f"  {k}: {v}")
        
        summary = monitor.get_summary()
        print("\nSummary:")
        for k, v in summary.items():
            print(f"  {k}: {v}")
    else:
        print("No metrics collected!")

if __name__ == "__main__":
    test_monitor()
