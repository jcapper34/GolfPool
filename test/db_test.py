import os
import sys

APP_ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, APP_ROOT)

### Start Test Script Here ###
from db.conn import Conn

def test_local_connection():
    conn = None
    try:
        conn = Conn(use_local=True)
    except Exception:
        return False

    return conn is not None


def test_remote_connection():
    conn = None
    try:
        conn = Conn(use_local=False)
    except Exception:
        return False

    return conn is not None


if __name__ == "__main__":
    print("Local connection ", "SUCCESS" if test_local_connection() else "FAILED")
    print("Remote connection ", "SUCCESS" if test_remote_connection() else "FAILED")
