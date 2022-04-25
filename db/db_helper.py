from db.conn import Conn

def filter_conn(conn) -> Conn:
    '''
    Starts a database connection if conn is not None
    '''
    return conn if conn is not None else Conn()
