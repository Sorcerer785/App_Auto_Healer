import time
import json
import subprocess
import os
import redis
import platform
import psutil
from monitor.db import get_redis_conn, get_postgres_conn

METRICS_KEY = "system_metrics"
CHECK_INTERVAL = 10
THRESHOLDS = {
    "cpu": 90.0,
    "memory": 50.0,
    "disk": 96.0
}
SCRIPTS_DIR = os.path.join(os.getcwd(), "scripts")

def kill_process_by_pattern(pattern):
    """Finds and kills processes matching a pattern (cross-platform)."""
    killed_count = 0
    try:
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            # Check if command line exists and contains the pattern
            if proc.info['cmdline'] and pattern in " ".join(proc.info['cmdline']):
                print(f"Killing process {proc.info['pid']} ({proc.info['name']}) matched '{pattern}'")
                proc.kill()
                killed_count += 1
    except Exception as e:
        print(f"Error killing process: {e}")
    return killed_count

def log_incident(incident_type, description):
    """Logs an incident to the database."""
    print(f"Logging Incident: {incident_type} - {description}")
    conn = get_postgres_conn()
    if not conn:
        print("db connection failed, skipping db log")
        return
    try:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO incidents (type, description) VALUES (%s, %s)",
            (incident_type, description)
        )
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Failed to log incident: {e}")

def trigger_remediation(script_name):
    """Executes a remediation script."""
    
    # SPECIAL CASE: For the unstable_app demo, we want to actually kill the python process
    # regardless of platform (since it's not a real systemd service).
    if "restart_service" in script_name:
        print(f"Triggering remediation: Stopping unstable_app.py")
        count = kill_process_by_pattern("unstable_app.py")
        if count > 0:
            log_incident("REMEDIATION_SUCCESS", f"Killed {count} instance(s) of unstable_app.py")
            
            # NOW RESTART IT
            print("Triggering remediation: Restarting unstable_app.py (Memory Mode)")
            try:
                # Launch independent process
                subprocess.Popen(["python3", "unstable_app.py", "2"], cwd=os.getcwd())
                log_incident("REMEDIATION_SUCCESS", "Restarted unstable_app.py")
            except Exception as e:
                log_incident("REMEDIATION_ERROR", f"Failed to restart app: {e}")

        else:
            log_incident("REMEDIATION_NO_OP", "Attempted to kill unstable_app.py but found no running process")
        return

    # Standard Script Execution (for other scripts like cleanup_disk)
    script_path = os.path.join(SCRIPTS_DIR, script_name)
    if not os.path.exists(script_path):
        print(f"Script not found: {script_path}")
        return

    print(f"Triggering remediation: {script_name}")
    
    if platform.system() == "Windows":
        print(f"Windows detected: Simulating execution of {script_path}")
        log_incident("REMEDIATION_SUCCESS", f"Simulated run of {script_name} (Windows)")
        return

    # Linux Execution
    cmd = ["bash", script_path]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        log_incident("REMEDIATION_SUCCESS", f"Ran {script_name}: {result.stdout.strip()}")
    except FileNotFoundError:
        msg = "Bash not found."
        print(msg)
        log_incident("REMEDIATION_ERROR", msg)
    except subprocess.CalledProcessError as e:
        log_incident("REMEDIATION_FAILED", f"Failed to run {script_name}: {e.stderr}")
    except Exception as e:
        log_incident("REMEDIATION_ERROR", str(e))

def check_health():
    """Checks latest metrics against thresholds."""
    conn = get_redis_conn()
    if not conn:
        return

    # Get last metric
    # LRANGE match_key -1 -1 gets the last element
    data = conn.lrange(METRICS_KEY, -1, -1)
    if not data:
        return

    try:
        metrics = json.loads(data[0])
    except (json.JSONDecodeError, IndexError):
        return
    
    print(f"Analyzing metrics: {metrics}")

    # CPU Check
    if metrics["cpu"] > THRESHOLDS["cpu"]:
        log_incident("HIGH_CPU", f"CPU usage at {metrics['cpu']}%")
        # trigger_remediation("restart_service.sh") 

    # Memory Check
    if metrics["memory"] > THRESHOLDS["memory"]:
        log_incident("HIGH_MEMORY", f"Memory usage at {metrics['memory']}%")
        trigger_remediation("restart_service.sh")

    # Disk Check
    if metrics["disk"] > THRESHOLDS["disk"]:
        log_incident("HIGH_DISK", f"Disk usage at {metrics['disk']}%")
        trigger_remediation("cleanup_disk.sh")

def start_healer():
    print("Starting auto-healer...")
    # Wait for collector to populate some data
    time.sleep(2) 
    
    while True:
        try:
            check_health()
            time.sleep(CHECK_INTERVAL)
        except KeyboardInterrupt:
            print("Stopping healer.")
            break
        except Exception as e:
            print(f"Error in healer: {e}")
            time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    start_healer()
