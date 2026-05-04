import os
import sqlite3
import pathlib


db_check = pathlib.Path("wager.db")

if db_check.exists():
    print("already exists")
else:
    # create db
    cur = sqlite3.connect("wager.db")

    with open("wager-db.sql") as fp:
        cur.executescript(fp.read())
        print("db created and initialized\n")
