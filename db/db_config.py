from os import environ

from helper import RUNNING_LOCALLY

USE_LOCAL = RUNNING_LOCALLY    # Will be true if running locally
# USE_LOCAL = False   # Uncomment if you want to use the remote DB locally

LOCAL_DB_CREDENTIALS = {
            "dbname": 'postgres',
            "user": 'jcapp',
            "host": 'localhost',
            "password": 'cmcapper',
            "options": '-c search_path=golfpool'
}

HEROKU_DB_CREDENTIALS = {
            "dbname": 'd494jt3e43ugjm',
            "user": 'dnydvecerfhlus',
            "host": 'ec2-3-215-52-251.compute-1.amazonaws.com',
            "password": '5bb791bfdcb7afa07b23f9703f9e3091c3d52459f4bfd0390afcc6938e9a0af5',
            "options": '-c search_path=golfpool'
}

