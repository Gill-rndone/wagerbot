import sqlite3
import pathlib


def init_db():
    db_check = pathlib.Path("wager.db")

    if db_check.exists():
        print("already exists")
    else:
        # create db
        cur = sqlite3.connect("wager.db")

        with open("wager-db.sql") as schema:
            cur.executescript(schema.read())
            print("db created and initialized\n")
