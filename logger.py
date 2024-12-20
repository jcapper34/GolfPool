import logging

logging.basicConfig(format='[%(asctime)s] - %(message)s', level=logging.INFO)

def info(msg, *args, **kwargs):
    logging.info(msg, *args, **kwargs)

def error(msg, *args, **kwargs):
    logging.error(msg, *args, **kwargs)

def warn(msg, *args, **kwargs):
    logging.warn(msg, *args, **kwargs)

def fatal(msg, *args, **kwargs):
    logging.fatal(msg, *args, **kwargs)

def debug(msg, *args, **kwargs):
    logging.debug(msg, *args, **kwargs)