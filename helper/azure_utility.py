from collections import namedtuple
from datetime import datetime, timedelta
import functools
import logger
import struct
from azure.identity import ChainedTokenCredential, DefaultAzureCredential
from config import *

AZURE_DB_SCOPE = "https://database.windows.net/.default"

@functools.cache # This is auto cached for the existence of program
def get_credential() -> ChainedTokenCredential:
    logger.info("Acquiring azure credential")
    return DefaultAzureCredential(
        exclude_interactive_browser_credential=IS_PRODUCTION)

# get_token_struct tuple(params) -> (value, timestamp) map
TokenCacheTuple = namedtuple("TokenCacheTuple", ['value', 'timestamp'])
token_cache = {}

def get_token_struct(credential: ChainedTokenCredential = None, tenant_id: str = None) -> bytes:
    if credential is None:
        credential = get_credential()
    if tenant_id is None:
        tenant_id = AZURE_TENANT_ID
    
    # Grab from cache if possible
    time_now = datetime.now()
    cache_key = (credential, tenant_id)
    cache_val = token_cache.get(cache_key)
    if cache_val is not None and time_now < cache_val.timestamp + AZURE_TOKEN_EXPIRY:
        logger.info("Returning azure token from cache for %s", AZURE_DB_SCOPE)
        return cache_val.value

    # Request token in scope
    logger.info("Requesting azure token for %s", AZURE_DB_SCOPE)
    token_bytes = credential.get_token(
        AZURE_DB_SCOPE,
        tenant_id = tenant_id).token.encode("UTF-16-LE")
    token = struct.pack(f'<I{len(token_bytes)}s', len(token_bytes), token_bytes)

    # Add to cache
    token_cache[cache_key] = TokenCacheTuple(token, time_now)
    
    return token
