import sqlite3
import numpy as np


class dbAPI:
    db_path = r'assets/data.db'

    create_locals = """
                    CREATE TABLE IF NOT EXISTS locals(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    paths STRING)"""

    create_networks = """
                    CREATE TABLE IF NOT EXISTS nets(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name STRING,
                    link STRING,
                    author STRING,
                    create_date STRING,
                    duration INTEGER,
                    tags STRING
                    )"""

    create_local_files  = """
                    CREATE TABLE IF NOT EXISTS lfiles(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    file_name STRING,
                    path STRING,
                    author STRING,
                    create_data STRING,
                    duration INTEGER,
                    tags STRING
                    )"""

    create_network_places="""
                    CREATE TABLE IF NOT EXISTS net_links(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    link STRING)"""

    create_playlist = """
                    CREATE TABLE IF NOT EXISTS playlist(
                    type STRING,
                    id STRING,
                    title STRING)"""

    def __init__(self):
        self.conn = sqlite3.connect(self.db_path)
        sqlite3.register_adapter(np.int64, lambda val: int(val))
        sqlite3.register_adapter(np.int32, lambda val: int(val))
        self.conn.execute("pragma foreign_keys")
        cur = self.conn.cursor()
        cur.execute(self.create_locals)
        cur.execute(self.create_local_files)
        cur.execute(self.create_networks)
        cur.execute(self.create_network_places)
        cur.execute(self.create_playlist)
        self.conn.commit()

    def get_links_to_read(self):
        qry = """SELECT link FROM net_links"""
        cur = self.conn.cursor()
        cur.execute(qry)
        return cur.fetchall()

    def insert_net(self, lst):
        cur = self.conn.cursor()
        cur.executemany("""INSERT OR REPLACE INTO nets VALUES(?, ?, ?, ?, ?, ?, ?)""", lst)
        self.conn.commit()


