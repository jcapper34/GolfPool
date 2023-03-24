import os
from psycopg2.pool import SimpleConnectionPool
from urllib.parse import parse_qs, urlparse
from db.connection import Conn


class ConnectionPool:
    def __init__(self, min_conn=1, max_conn=5) -> None:
        username = os.getenv("DB_USER")
        password = os.getenv("DB_PASSWORD")
        database = os.getenv("DB_NAME")
        hostname = os.getenv("DB_HOSTNAME")
        port = os.getenv("DB_PORT")
        sslmode = os.getenv("DB_SSLMODE")
        print("Connecting to db username=%s password=%s database=%s host=%s port=%s sslmode=%s" % 
            (username, password, database, hostname, port, sslmode))
        self.connection_pool = SimpleConnectionPool(min_conn, max_conn,
            database=database,
            user=username,
            password=password,
            host=hostname,
            port=port,
            sslmode=sslmode
        )
    
    def get_conn(self) -> Conn:
        pgconn = self.connection_pool.getconn()
        return Conn(pgconn, self.connection_pool)

db_pool = ConnectionPool()