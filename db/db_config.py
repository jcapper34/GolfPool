from os import environ

from helper import RUNNING_LOCALLY

USE_LOCAL = RUNNING_LOCALLY    # Will be true if running locally
USE_LOCAL = False   # Uncomment if you want to use the remote DB locally

LOCAL_DB_CREDENTIALS = {
            "dbname": 'postgres',
            "user": 'jcapp',
            "host": 'localhost',
            "password": 'cmcapper',
            "options": '-c search_path=golfpool'
}

HEROKU_DB_CREDENTIALS = {
            "dbname": 'd5le5ff7esjtrb',
            "user": 'xcidhpvweehrud',
            "host": 'ec2-23-21-171-25.compute-1.amazonaws.com',
            "password": 'fdc587747cf954a402fc66ca4c5710e908b006200ccff68db953b32ed352a2a9',
            "options": '-c search_path=golfpool'
}

