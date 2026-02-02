#!/bin/bash

LOG_FILE=${1:-/var/log/monitor.log}

echo "[$(date)] Rotating log file: $LOG_FILE"

if [ -f "$LOG_FILE" ]; then
    TIMESTAMP=$(date +%Y%m%d%H%M%S)
    BACKUP_FILE="${LOG_FILE}.${TIMESTAMP}"
    
    # mv "$LOG_FILE" "$BACKUP_FILE"
    # touch "$LOG_FILE"
    # gzip "$BACKUP_FILE"
    
    echo "Simulated: mv $LOG_FILE $BACKUP_FILE && gzip $BACKUP_FILE"
else
    echo "Log file $LOG_FILE not found."
fi

echo "Log rotation completed."
