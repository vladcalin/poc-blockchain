import sqlite3


class CreateTableSql:
    CREATE_TRANSACTION_TABLE = (
        "CREATE TABLE IF NOT EXISTS transactions ("
        "   index PRIMARY KEY "
        ")")


class Sqlite3Persistence(object):
    def __init__(self, db_path):
        self._db = sqlite3.connect(db_path)
        self.ensure_tables()

    def ensure_tables(self):
        pass
