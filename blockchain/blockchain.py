import os.path
import sqlite3

from blockchain.network import STORAGE_DATA


class Blockchain(object):
    create_tables_sqls = [
        """CREATE TABLE IF NOT EXISTS peers(
           ip TEXT PRIMARY KEY
        )""",
        """CREATE TABLE IF NOT EXISTS blocks(
           hash TEXT PRIMARY KEY,
           ts TEXT,
           proof INTEGER
        )""",
        """CREATE TABLE IF NOT EXISTS transactions(
          hash TEXT PRIMARY KEY,
          ts TEXT,
          from_addr TEXT,
          to_addr TEXT,
          amount REAL,
          signature BLOB,
          pub_key BLOB
        )""",
        """CREATE TABLE IF NOT EXISTS blocks_transactions(
          block TEXT,
          tx TEXT,
           FOREIGN KEY (block) REFERENCES blocks(hash),
           FOREIGN KEY (tx) REFERENCES transactions(hash)
        )"""
    ]

    def __init__(self):
        if not os.path.exists(STORAGE_DATA):
            os.makedirs(STORAGE_DATA)
        self.data = sqlite3.connect(os.path.join(STORAGE_DATA, 'blockchain'))
        self.ensure_tables()

    def ensure_tables(self):
        cursor = self.data.cursor()
        for sql in self.create_tables_sqls:
            cursor.execute(sql)
        cursor.close()

    def add_peer(self, peer):
        sql = 'INSERT OR REPLACE INTO peers (?)'
        cursor = self.data.cursor()
        cursor.execute(sql, (peer,))
        cursor.close()

    def get_peer_count(self):
        cursor = self.data.cursor()
        cursor.execute('SELECT COUNT(ip) FROM peers')
        res = cursor.fetchone()
        cursor.close()
        return res[0]

    def iter_peers(self):
        cursor = self.data.cursor()
        cursor.execute('SELECT ip FROM peers')
        for peer in cursor.fetchall():
            yield peer
        cursor.close()
