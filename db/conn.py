import psycopg2
import psycopg2.extras
from urllib.parse import urlparse
from config import LOCAL_DB_CREDENTIALS, HEROKU_DB_CREDENTIALS, USE_LOCAL

class Conn:
    def __init__(self, use_local=False):
        # Uncomment when local db is installed
        db_url = urlparse(LOCAL_DB_CREDENTIALS if USE_LOCAL else HEROKU_DB_CREDENTIALS)
        
        username = db_url.username
        password = db_url.password
        database = db_url.path[1:]
        hostname = db_url.hostname
        port = db_url.port
        self.conn = psycopg2.connect(
            database = database,
            user = username,
            password = password,
            host = hostname,
            port = port
        )
        
        # credentials = LOCAL_DB_CREDENTIALS if use_local else HEROKU_DB_CREDENTIALS
        # self.conn = psycopg2.connect(**credentials)
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

    def wherify(self, where=()):
        if where and not isinstance(where[0], (list, tuple)):
            where = (where, )
        where_str = ' WHERE ' if where else ''
        return where_str + ' AND '.join(self.cur.mogrify(x[0] + " = %s", (x[1],)).decode('utf-8') for x in where)

    def __del__(self):
        if getattr(self, "conn", None) is not None:
            self.conn.close()
