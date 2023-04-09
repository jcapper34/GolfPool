from typing import Any, ByteString
import psycopg2
import psycopg2.extras
from psycopg2.extensions import connection
from psycopg2.pool import SimpleConnectionPool
from urllib.parse import parse_qs, urlparse

class Conn:
    def __init__(self, pgconn: connection, conn_pool: SimpleConnectionPool = None) -> None:
        self.pgconn = pgconn
        self.conn_pool = conn_pool

    def new_cursor(self, use_dict=True) -> None:
        if use_dict:
            self.cur = self.pgconn.cursor(
                cursor_factory=psycopg2.extras.DictCursor)
        else:
            self.cur = self.pgconn.cursor()

    def exec(self, query, args=None) -> None:
        self.cur.execute(query, args)

    def exec_fetch(self, query, args=None, fetchall=True) -> Any:
        self.cur.execute(query, args)
        if fetchall:
            return self.cur.fetchall()
        else:
            return self.cur.fetchone()

    def exec_commit(self, query, args=None) -> None:
        self.cur.execute(query, args)
        self.pgconn.commit()

    def commit(self) -> None:
        self.pgconn.commit()
    
    def mogrify(self, query, args=None) -> ByteString:
        return self.cur.mogrify(query, args)

    def wherify(self, where=()) -> str:
        if where and not isinstance(where[0], (list, tuple)):
            where = (where, )
        where_str = ' WHERE ' if where else ''
        return where_str + ' AND '.join(self.cur.mogrify(x[0] + " = %s", (x[1],)).decode('utf-8') for x in where)

    def close(self) -> None:
        if getattr(self, "conn", None) is not None:
            self.pgconn.close()
        if getattr(self, "cur", None) is not None:
            self.cur.close()
        
    def __enter__(self) -> Any:
        self.new_cursor()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.cur.close()
        if self.conn_pool is not None:
            self.conn_pool.putconn(self.pgconn)
