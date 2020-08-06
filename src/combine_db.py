import os
import sqlite3

showtime_db = sqlite3.connect("db/showtime.db")
vieshow_db = sqlite3.connect("db/vieshow.db")
ambassador_db = sqlite3.connect("db/ambassador.db")


# create db
def create_db():
    if os.path.exists("db/all.db"):
        os.remove("db/all.db")
    db = sqlite3.connect("db/all.db")

    c = db.cursor()
    c.execute(
        """CREATE TABLE MOVIE
        (
            TITLE TEXT,
            PLACE TEXT,
            DATE  TEXT,
            TIME  TEXT,
            OTHER TEXT
        )
        ;"""
    )

    return db, c


# insert a movie data
def insert_db(c, title, place, date, time, other):
    c.execute("INSERT INTO MOVIE (TITLE, PLACE, DATE, TIME, OTHER) \
        VALUES (?, ?, ?, ?, ?)", (title, place, date, time, other))


# combine dbs
def combine(showtime_c, vieshow_c, ambassador_c):
    db, c = create_db()
    
    showtime_cursor = showtime_c.execute("SELECT TITLE, PLACE, DATE, TIME, OTHER from MOVIE")
    for row in showtime_cursor:
        insert_db(c, row[0], row[1], row[2], row[3], row[4])
    vieshow_cursor = vieshow_c.execute("SELECT TITLE, PLACE, DATE, TIME, OTHER from MOVIE")
    for row in vieshow_cursor:
        insert_db(c, row[0], row[1], row[2], row[3], row[4])
    ambassador_cursor = ambassador_c.execute("SELECT TITLE, PLACE, DATE, TIME, OTHER from MOVIE")
    for row in ambassador_cursor:
        insert_db(c, row[0], row[1], row[2], row[3], row[4])

    db.commit()
    db.close()


showtime_c = showtime_db.cursor()
vieshow_c = vieshow_db.cursor()
ambassador_c = ambassador_db.cursor()
combine(showtime_c, vieshow_c, ambassador_c)