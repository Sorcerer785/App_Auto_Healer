import time
import json
import psutil
from ping3 import ping
from monitor.db import get_redis_conn

# Configuration
METRICS_KEY = "system_metrics"
MAX_HISTORY = 100  # Keep last 100 data points
POLL_INTERVAL = 5  # Seconds

def get_system_metrics():
    """Collects system metrics."""
    # psutil.cpu_percent(interval=None) is non-blocking if called repeatedly,
    # but the first call can be 0. We'll stick to non-blocking or short interval.
    # If interval is > 0, it blocks.
    cpu = psutil.cpu_percent(interval=1)
    
    memory = psutil.virtual_memory().percent
    
    # Disk usage for root "/"
    # On Windows "/" maps to current drive usually, or valid.
    disk = psutil.disk_usage('/').percent
    
    # Latency to google.com
    try:
        latency = ping("google.com", timeout=2)
        if latency is None:
            latency = -1 # Timeout
    except Exception:
        latency = -1 # Error

    metrics = {
        "timestamp": time.time(),
        "cpu": cpu,
        "memory": memory,
        "disk": disk,
        "latency": latency
    }
    return metrics

def start_collector():
    """Main loop to collect and store metrics."""
    redis_conn = get_redis_conn()
    
    if not redis_conn:
        print("Failed to connect to Redis. Exiting collector.")
        return

    print("Starting metrics collector...")
    while True:
        try:
            metrics = get_system_metrics()
            
            # Serialize to JSON
            data = json.dumps(metrics)
            
            # Atomic push and trim
            pipe = redis_conn.pipeline()
            pipe.rpush(METRICS_KEY, data)
            pipe.ltrim(METRICS_KEY, -MAX_HISTORY, -1) 
            pipe.execute()
            
            print(f"Collected: cpu={metrics['cpu']}%, mem={metrics['memory']}%, disk_space={metrics['disk']}%, lat={metrics['latency']}s")
            
            # Wait for next poll (handled largely by cpu_percent interval=1 consuming 1s, plus sleep)
            time.sleep(POLL_INTERVAL - 1 if POLL_INTERVAL > 1 else 0)
            
        except KeyboardInterrupt:
            print("Stopping collector.")
            break
        except Exception as e:
            print(f"Error in collector: {e}")
            time.sleep(POLL_INTERVAL)

if __name__ == "__main__":
    start_collector()
