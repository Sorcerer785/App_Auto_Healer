import time
import threading

def consume_cpu():
    print("Consuming CPU...")
    try:
        while True:
            pass
    except KeyboardInterrupt:
        pass

def consume_memory():
    print("Consuming Memory...")
    data = []
    try:
        while True:
            # Append 10MB
            data.append(' ' * 200 * 1024 * 1024) 
            time.sleep(1)
    except MemoryError:
        print("Memory full!")
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    import sys
    
    mode = None
    if len(sys.argv) > 1:
        mode = sys.argv[2]
    
    if not mode:
        print("Select mode:")
        print("1. High CPU")
        print("2. High Memory")
        mode = input("Enter choice (1/2): ")
    
    if mode == "1":
        # Launch multiple threads to max out cores
        for _ in range(4):
            threading.Thread(target=consume_cpu, daemon=True).start()
    elif mode == "2":
        consume_memory()
    else:
        print(f"Invalid choice: {mode}")
    
    print("Running... Press Ctrl+C to stop.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopping...")
