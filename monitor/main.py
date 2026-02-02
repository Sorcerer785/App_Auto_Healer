import threading
import time
from monitor.collector import start_collector
from monitor.healer import start_healer

def main():
    print("Starting Application Reliability Monitoring System...")
    
    # Run Collector in a separate thread
    t_collector = threading.Thread(target=start_collector, daemon=True)
    t_collector.start()
    
    # Run Healer in a separate thread
    t_healer = threading.Thread(target=start_healer, daemon=True)
    t_healer.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Shutting down...")

if __name__ == "__main__":
    main()
