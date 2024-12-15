import atexit
from typing import Any, Dict, Generator, Iterator, List, Sequence, Union
from typing_extensions import Self
import logger
import pyodbc
from config import *
from helper import azure_utility
from helpers import retry_util

class DatabaseTableRow:
    _row : pyodbc.Row = None
    _column_mappings: Dict[str, int] = None

    def __init__(self, row: pyodbc.Row, column_mappings: Dict[str, int]):
        self._row = row
        self._column_mappings = column_mappings

    def __getitem__(self, key: Any):
        if isinstance(key, int):
            return self._row[key]
        
        return self._row[self._column_mappings[key]]
    
    def __str__(self) -> str:
        return str(self._row)
    
    def __repr__(self) -> str:
        return repr(self._row)

    def __dict__(self) -> dict:
        return {k: self[k] for k in self._column_mappings}

class DatabaseCursor:
    def __init__(self, cursor: pyodbc.Cursor):
        self._cursor = cursor

    def execute(self, sql: str, *params: Any) -> Self:
        self._cursor.execute(sql, *params)
        return self
    
    def executemany(self, sql: str, params: Union[Sequence, Iterator, Generator]) -> Self:
        self._cursor.executemany(sql, params)
        return self

    def fetchone(self) -> DatabaseTableRow:
        row = self._cursor.fetchone()
        if row is None:
            return None
        
        return DatabaseTableRow(row, self._get_column_mappings())

    def fetchall(self) -> Iterator[DatabaseTableRow]:
        mappings = self._get_column_mappings()
        return (DatabaseTableRow(x, mappings) for x in self._cursor.fetchall())

    def commit(self) -> None:
        return self._cursor.commit()
    
    def rowcount(self) -> int:
        return self._cursor.rowcount
    
    def enable_fastexecutemany(self):
        self._cursor.fast_executemany = True
    
    def _get_column_mappings(self):
        return {x[0]:i for i, x in enumerate(self._cursor.description)}
    
    def close(self) -> None:
        return self._cursor.close()

class DatabaseConnection:
    CONNECTION_IS_CLOSED_ERROR = "Attempt to use a closed connection."
    
    def __init__(self, token_credential: bytes = None):
        if token_credential is None:
            token_credential = azure_utility.get_token_struct()

        SQL_COPT_SS_ACCESS_TOKEN = 1256  # Connection option definition

        try:
            self._connection = retry_util(
                lambda: pyodbc.connect(
                    DB_CONNECTION_STRING,
                    attrs_before={SQL_COPT_SS_ACCESS_TOKEN: token_credential}))
            logger.info("Connected to database - %s", DB_CONNECTION_STRING)

            atexit.register(self.close) # Make sure connection always closes when app exits
        except Exception as e:
            logger.error("Failed to connect to database with error %s", e)
            raise e

    def cursor(self) -> DatabaseCursor:
        return DatabaseCursor(self._connection.cursor())
    
    def close(self) -> None:
        try:
            self._connection.close()
        except pyodbc.ProgrammingError as e:
            if e.args[0] != self.__class__.CONNECTION_IS_CLOSED_ERROR:
                raise e
        
    def __enter__(self) -> Any:
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()
