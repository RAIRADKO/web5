import MySQLdb
from flask import g

def get_db():
    if 'db' not in g:
        g.db = MySQLdb.connect(
            host="localhost",
            user="root",
            password="",
            database="db_kominfo",  # ganti sesuai nama database kamu
            charset="utf8mb4"
        )
    return g.db
