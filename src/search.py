import sys
import sqlite3


# print db
def print_db(cursor):
    for row in cursor:
        print(" " * 95 + row[4], end="\r")
        print(" " * 85 + row[3], end="\r")
        print(" " * 70 + row[2], end="\r")
        print(" " * 40 + row[1], end="\r")
        print(row[0], end="\r")
        print()


def print_usage():
    print("example: [-name 玩命關頭] [-theater 板橋秀泰] [-date 2020-08-05]")
    # print("example: [-name 玩命關頭] [-theater 板橋秀泰] [-date 2020-08-05] [-time 13:00-17:00]")
    print("type \"quit\" to exit program")
    print("type \"list\" to see all movies")


# Process command
def command():
    cmd = input("search>> ")
    name = ""
    theater = ""
    date = ""
    time = ""
    
    if cmd == "quit": sys.exit()
    
    elif cmd == "list":
        name = " "
        theater = " "
        date = " "
        time = " "

    elif cmd == "": 
        print_usage()

    else:    
        tokens = cmd.split()

        for i in range(0,len(tokens),2):
            if tokens[i] == "-name":
                name = tokens[i+1]
            elif tokens[i] == "-theater":
                theater = tokens[i+1]
            elif tokens[i] == "-time":
                time = tokens[i+1]
            elif tokens[i] == "-date":
                date = tokens[i+1]
            else: 
                print("Illegal command.")
                return
    
    return name, theater, date, time


# Handle every kind of search
def search(c, name, theater, date, time):
    if name == " " and theater == " " and date == " " and time == " ":
        cursor = c.execute("SELECT DISTINCT TITLE from MOVIE")
        for row in cursor: print(row[0])
        return
        
    sql_cmd = "SELECT * from MOVIE"
    sql_value = []

    cnt = 0
    if name:
        sql_cmd += " WHERE TITLE LIKE ?"
        sql_value.append("%"+name+"%")
        cnt += 1

    if theater:
        if cnt == 0:
            sql_cmd += " WHERE PLACE LIKE ?"
        else:
            sql_cmd += " and PLACE LIKE ?"
        sql_value.append("%"+theater+"%")
        cnt += 1

    if date:
        if cnt == 0:
            sql_cmd += " WHERE DATE = ?"
        else:
            sql_cmd += " and DATE = ?"
        sql_value.append(date)

    sql_value = tuple(sql_value)

    cursor = c.execute(sql_cmd, sql_value)
    print_db(cursor)


# main
db = sqlite3.connect("db/all.db")
c = db.cursor()

while True:
    name, theater, date, time = command()
    search(c, name, theater, date, time)