import psycopg2
import psycopg2.extras
from urllib.parse import parse_qs, urlparse
from config import DATABASE_URL


class Conn:
    def __init__(self):
        if " " not in DATABASE_URL:
            db_url = urlparse(DATABASE_URL)

            username = db_url.username
            password = db_url.password
            database = db_url.path[1:]
            hostname = db_url.hostname
            port = db_url.port
            sslmode = parse_qs(db_url.query).get("sslmode")
            sslmode = "prefer" if sslmode is None else sslmode[0]
            self.conn = psycopg2.connect(
                database=database,
                user=username,
                password=password,
                host=hostname,
                port=port,
                sslmode=sslmode
            )
        else:
            self.conn = psycopg2.connect(DATABASE_URL)
        
        self.new_cursor()

    def new_cursor(self, use_dict=True):
        if use_dict:
            self.cur = self.conn.cursor(
                cursor_factory=psycopg2.extras.DictCursor)
        else:
            self.cur = self.conn.cursor()

    def exec(self, query, args=None):
        self.cur.execute(query, args)

    def exec_fetch(self, query, args=None, fetchall=True):
        self.cur.execute(query, args)
        if fetchall:
            return self.cur.fetchall()
        else:
            return self.cur.fetchone()

    def exec_commit(self, query, args=None):
        self.cur.execute(query, args)
        self.conn.commit()

    def commit(self):
        self.conn.commit()
    
    
    def mogrify(self, query, args=None):
        return self.cur.mogrify(query, args)

    def wherify(self, where=()):
        if where and not isinstance(where[0], (list, tuple)):
            where = (where, )
        where_str = ' WHERE ' if where else ''
        return where_str + ' AND '.join(self.cur.mogrify(x[0] + " = %s", (x[1],)).decode('utf-8') for x in where)

    def __del__(self):
        if getattr(self, "conn", None) is not None:
            self.conn.close()
