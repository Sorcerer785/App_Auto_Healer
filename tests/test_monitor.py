import sys
from unittest.mock import MagicMock

# Mock external dependencies to allow testing without installation
sys.modules["redis"] = MagicMock()
sys.modules["psycopg2"] = MagicMock()
sys.modules["psycopg2.OperationalError"] = Exception
sys.modules["dotenv"] = MagicMock()
sys.modules["psutil"] = MagicMock()
sys.modules["ping3"] = MagicMock()

import unittest
import json
from unittest.mock import patch
from monitor.healer import check_health, THRESHOLDS

class TestMonitor(unittest.TestCase):
    
    @patch('monitor.healer.get_postgres_conn')
    @patch('monitor.healer.trigger_remediation')
    @patch('monitor.healer.get_redis_conn')
    def test_high_cpu_trigger(self, mock_redis_conn, mock_trigger, mock_pg_conn):
        # Mock Redis connection and return data
        mock_r = MagicMock()
        mock_redis_conn.return_value = mock_r
        
        # CPU > Threshold
        metrics = {
            "timestamp": 123456,
            "cpu": THRESHOLDS["cpu"] + 5,
            "memory": 50,
            "disk": 50,
            "latency": 10
        }
        mock_r.lrange.return_value = [json.dumps(metrics)]
        
        check_health()
        
        # Verify DB connection was attempted (for logging)
        mock_pg_conn.assert_called()
        
    @patch('monitor.healer.get_postgres_conn')
    @patch('monitor.healer.trigger_remediation')
    @patch('monitor.healer.get_redis_conn')
    def test_high_memory_trigger(self, mock_redis_conn, mock_trigger, mock_pg_conn):
        mock_r = MagicMock()
        mock_redis_conn.return_value = mock_r
        
        metrics = {
            "timestamp": 123456,
            "cpu": 50,
            "memory": THRESHOLDS["memory"] + 5,
            "disk": 50,
            "latency": 10
        }
        mock_r.lrange.return_value = [json.dumps(metrics)]
        
        check_health()
        
        # Verify remediation called
        mock_trigger.assert_called_with("restart_service.sh")

if __name__ == '__main__':
    unittest.main()
