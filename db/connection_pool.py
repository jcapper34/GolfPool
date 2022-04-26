from psycopg2.pool import SimpleConnectionPool
from urllib.parse import parse_qs, urlparse
from config import DATABASE_URL
from db.conn import Conn


class ConnectionPool:
    def __init__(self, min_conn=1, max_conn=5) -> None:
        if " " not in DATABASE_URL:
            self.connection_pool = SimpleConnectionPool(min_conn, max_conn, DATABASE_URL)
        else:
            db_url = urlparse(DATABASE_URL)

            username = db_url.username
            password = db_url.password
            database = db_url.path[1:]
            hostname = db_url.hostname
            port = db_url.port
            sslmode = parse_qs(db_url.query).get("sslmode")
            sslmode = "prefer" if sslmode is None else sslmode[0]
            self.connection_pool = SimpleConnectionPool(self.MIN_CONN, self.MAX_CONN,
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