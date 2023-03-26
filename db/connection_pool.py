from config import *
from psycopg2.pool import SimpleConnectionPool
from urllib.parse import parse_qs, urlparse
from db.connection import Conn


class ConnectionPool:
    """
    Class that manages a pool of connections to the postgres database
    Should be treated as a singleton
    """
    
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

        print("Connected to db username=%s password=%s database=%s host=%s port=%s sslmode=%s" % 
            (self.username, self.password, self.database, self.hostname, self.port, self.sslmode))
    
    def get_conn(self) -> Conn:
        """
        Grab db connection from pool. Will connect if no connection has been created yet
        """
        if getattr(self, "connection_pool", None) is None:
            self.connect()

        pgconn = self.connection_pool.getconn()
        return Conn(pgconn, self.connection_pool)

db_pool = ConnectionPool()