"""Test script for HardwareMonitor."""
import time
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
    
    print(f"Collected {len(monitor.metrics)} data points")
    
    if monitor.metrics:
        print("First metric:", monitor.metrics[0])
        print("Last metric:", monitor.metrics[-1])
        
        summary = monitor.get_summary()
        print("\nSummary:")
        for k, v in summary.items():
            print(f"{k}: {v}")
    else:
        print("No metrics collected!")

if __name__ == "__main__":
    test_monitor()
