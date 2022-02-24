import psycopg2
from db.conn import Conn

def safe_exec(cur, query, params=None, fetch=False, return_error=False):
    try:
        cur.execute(query, params)
    except (psycopg2.DataError, psycopg2.DatabaseError, psycopg2.IntegrityError) as e:
        if return_error:
            return e
        else:
            return False
    if fetch:
        return cur.fetchall()

    return True


def filter_conn(conn):
    return conn if conn is not None else Conn()
