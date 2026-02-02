import os
import redis
import psycopg2
from psycopg2 import OperationalError
from dotenv import load_dotenv

load_dotenv()

# Redis Configuration
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_DB = int(os.getenv("REDIS_DB", 0))

# Postgres Configuration
PG_DB = os.getenv("POSTGRES_DB", "monitor_db")
PG_USER = os.getenv("POSTGRES_USER", "postgres")
PG_PASSWORD = os.getenv("POSTGRES_PASSWORD", "password")
PG_HOST = os.getenv("POSTGRES_HOST", "localhost")
PG_PORT = os.getenv("POSTGRES_PORT", "5432")

class MockRedis:
    _shared_data = {}  # Class-level dictionary to share data across instances

    def __init__(self):
        print("BS: Using Mock Redis (In-Memory Shared)")

    def pipeline(self):
        return self

    def rpush(self, key, value):
        if key not in self._shared_data:
            self._shared_data[key] = []
        self._shared_data[key].append(value)
    
    def ltrim(self, key, start, end):
        if key in self._shared_data:
            # Python slice handling
            if start < 0: start += len(self._shared_data[key])
            if end < 0: end += len(self._shared_data[key])
            self._shared_data[key] = self._shared_data[key][max(0, start):end+1]

    def execute(self):
        pass

    def lrange(self, key, start, end):
        if key not in self._shared_data:
            return []
        if end == -1:
             return self._shared_data[key][start:]
        return self._shared_data[key][start:end+1]

class MockPostgres:
    def __init__(self):
        print("BS: Using Mock PostgreSQL (No-Op)")
    
    def cursor(self):
        return self
    
    def execute(self, query, params=None):
        print(f"BS-SQL: Executing > {query} | Params: {params}")
    
    def commit(self):
        pass
    
    def close(self):
        pass

def get_redis_conn():
    """Returns a Redis connection or Mock if failed."""
    try:
        conn = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, decode_responses=True)
        conn.ping() # Check connection
        return conn
    except Exception as e:
        print(f"Redis Connection Error: {e}")
        print("Falling back to MockRedis...")
        return MockRedis()

def get_postgres_conn():
    """Returns a PostgreSQL connection or Mock if failed."""
    try:
        conn = psycopg2.connect(
            dbname=PG_DB,
            user=PG_USER,
            password=PG_PASSWORD,
            host=PG_HOST,
            port=PG_PORT
        )
        return conn
    except OperationalError as e:
        print(f"PostgreSQL Connection Error: {e}")
        print("Falling back to MockPostgres...")
        return MockPostgres()

def init_db():
    """Initializes the PostgreSQL database schema."""
    conn = get_postgres_conn()
    if isinstance(conn, MockPostgres):
        return

    try:
        cur = conn.cursor()
        
        # Create incidents table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS incidents (
                id SERIAL PRIMARY KEY,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                type VARCHAR(50) NOT NULL,
                description TEXT,
                resolved BOOLEAN DEFAULT FALSE
            );
        """)
        
        conn.commit()
        cur.close()
        conn.close()
        print("Database initialized successfully.")
    except Exception as e:
        print(f"Error initializing database: {e}")

if __name__ == "__main__":
    init_db()
