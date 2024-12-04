import atexit
import threading
from config import *
from psycopg2.pool import SimpleConnectionPool, ThreadedConnectionPool
from urllib.parse import parse_qs, urlparse
from db.connection import Conn
from helpers import retry_util


class ConnectionPool:
    """
    Class that manages a pool of connections to the postgres database
    Should be treated as a singleton
    """
    
    lock = threading.Lock()

    def __init__(self, min_conn=1, max_conn=5) -> None:
        self.min_conn = min_conn
        self.max_conn = max_conn
        
        self.username = DB_USER
        self.password = DB_PASSWORD
        self.database = DB_NAME
        self.hostname = DB_HOSTNAME
        self.port = DB_PORT
        self.sslmode = DB_SSLMODE

    def connect(self):
        print("Connecting to db username=%s password=%s database=%s host=%s port=%s sslmode=%s" % 
            (self.username, self.password, self.database, self.hostname, self.port, self.sslmode))
        
        def try_connect():
            if ENABLE_THREADED_DB_CONN:
                self.connection_pool = ThreadedConnectionPool(
                    self.min_conn,
                    self.max_conn,
                    database = self.database,
                    user = self.username,
                    password = self.password,
                    host = self.hostname,
                    port = self.port,
                    sslmode = self.sslmode
                )
            else:
                self.connection_pool = SimpleConnectionPool(
                    self.min_conn,
                    self.max_conn,
                    database = self.database,
                    user = self.username,
                    password = self.password,
                    host = self.hostname,
                    port = self.port,
                    sslmode = self.sslmode
                )

        retry_util(try_connect) # Connect with retries

        if self.connection_pool is not None:
            print("Database connection was successful")
        else:
            print("Failed to connect to database")
    
    def get_conn(self) -> Conn:
        """
        Grab db connection from pool. Will create connection if no connection has been created yet
        """
        # Use a lock in case multiple connections need to be re-created at once
        with self.lock:
            if getattr(self, "connection_pool", None) is None:
                self.connect()
            pgconn = self.connection_pool.getconn()

        return Conn(pgconn, self.connection_pool)
    
    def close(self) -> None:
        if getattr(self, "connection_pool", None) is not None:
            print("Closing connection pool")
            self.connection_pool.closeall()

# Global connection pool
db_pool = ConnectionPool()
atexit.register(db_pool.close) # Make sure pool always closes when program exits
