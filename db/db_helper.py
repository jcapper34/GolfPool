import psycopg2
from db.conn import Conn

def filter_conn(conn):
    '''
    Starts a database connection if conn is not None
    '''
    return conn if conn is not None else Conn()
