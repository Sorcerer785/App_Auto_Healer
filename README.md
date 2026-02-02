# Application Reliability Monitoring & Auto-Healing System

A system that monitors running applications, stores metrics in Redis/PostgreSQL, and triggers auto-healing Bash scripts when thresholds are breached.

## Tech Stack
- **Python**: Metrics collector (`psutil`), Healer logic.
- **Redis**: Real-time metrics storage.
- **PostgreSQL**: Incident logging.
- **Bash**: Remediation scripts (restart service, cleanup disk).
- **Systemd**: Service management (Linux only).

## Setup (Windows/Linux)

1.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

2.  **Environment Variables**:
    Copy `.env.example` to `.env` and update credentials.
    ```bash
    cp .env.example .env
    ```

3.  **Databases**:
    Ensure Redis and PostgreSQL are running.
    - **Step Id 21 comment**: User requested sticking to Redis/Postgres.
    - If on Windows, use Docker or native installers.

4.  **Run the System**:
    ```bash
    python -m monitor.main
    ```

## Testing Auto-Healing

1.  Run the monitor: `python -m monitor.main`
2.  Run the unstable app to trigger alerts:
    ```bash
    python unstable_app.py
    ```
    - Select Option 1 (CPU) or 2 (Memory).
3.  Watch the console for "Logging Incident" and "Triggering remediation".
4.  Check `scripts/` execution (simulated on Windows).

## Project Structure
- `monitor/`: Python package for collector and healer.
- `scripts/`: Bash scripts for remediation.
- `config/`: Systemd unit files.
- `tests/`: Unit tests.
