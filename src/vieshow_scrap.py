import os
import sqlite3
import datetime
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


url = "https://www.vscinemas.com.tw/ShowTimes/"
webdriver_path = "./chromedriver/chromedriver.exe"
chrome_options = Options()
chrome_options.add_argument("--headless")
driver = webdriver.Chrome(executable_path=webdriver_path, options=chrome_options)
wait = WebDriverWait(driver, 10)


def get_theaters():
    driver.get(url)

    select_theater = wait.until(EC.presence_of_element_located((By.NAME, "CinemaNameTWInfoF")))
    sleep(2)

    sl = Select(select_theater)
    theaters = [x.text for x in sl.options][1:7]

    return theaters


def strQ2B(ustring):
    ss = []
    for s in ustring:
        rstring = ""
        for uchar in s:
            inside_code = ord(uchar)
            if inside_code == 12288:
                inside_code = 32
            elif (inside_code >= 65281 and inside_code <= 65374):
                inside_code -= 65248
            rstring += chr(inside_code)
        ss.append(rstring)
    return ''.join(ss)


def get_title(title):
    title = title.replace("(", "|")
    title = title.replace(")", "|")
    title = title.split("|")

    return strQ2B(title[2].replace(" ", "")), title[1]


def get_dates(dates):
    now = datetime.datetime.now()
    year = now.year

    new_dates = []
    for date in dates:
        month = date.split("月")[0]
        day = date.split("月")[1].split("日")[0]
        new_dates.append(f"{year}-{month}-{day}")

    return new_dates


def get_times(time_rows):
    new_time_rows = []
    for time_row in time_rows:
        times = time_row.split("\n")
        new_time_rows.append(times)

    return new_time_rows


# scrap showtime.com
def scrap(c):
    num = 0
    theaters = get_theaters()

    for idx in range(len(theaters)):
        place = theaters[idx]
        # print(place)
        driver.get(url)

        select_theater = wait.until(EC.presence_of_element_located((By.NAME, "CinemaNameTWInfoF")))
        sleep(2)

        sl = Select(select_theater)
        sl.select_by_index(idx+1)
        movie_container = wait.until(EC.presence_of_element_located((By.ID, "ShowTimeSecondInfo")))
        sleep(2)

        # movies = movie_container.find_elements_by_xpath(f"/html/body/div/div[2]/div[2]/div/div[47]")
        # print(len(movies))


        i = 1
        while 1:
            # print(i)
            movie = 0
            try:
                movie = movie_container.find_element_by_xpath(f"/html/body/div/div[2]/div[2]/div/div[{i}]")
            except:
                break

            i += 1
            
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "strong.col-xs-12.LangTW.MovieName")))
            title = movie.find_element_by_css_selector("strong.col-xs-12.LangTW.MovieName").text
            title, other = get_title(title)
            if other == "PRE" or other == "LIVE":
                continue
            # print(title)
            

            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "strong.col-xs-12.LangTW.RealShowDate")))
            dates = movie.find_elements_by_css_selector("strong.col-xs-12.LangTW.RealShowDate")
            dates = [x.text for x in dates]
            dates = get_dates(dates)
            # print(dates)

            time_rows = movie.find_elements_by_css_selector("div.col-xs-12.SessionTimeInfo")
            time_rows = [x.text for x in time_rows]
            time_rows = get_times(time_rows)
            # print(time_rows)

            for j in range(len(dates)):
                date = dates[j]
                # print(date)
                times = time_rows[j]

                for time in times:
                    # print(time)
                    insert_db(c, title, place, date, time, other)
                    num += 1
                    print(f"scraped {num} movie sessions", end="\r")

        # break

    driver.close()



# create new database
def create_db():
    if os.path.exists("db/vieshow.db"):
        os.remove("db/vieshow.db")
    db = sqlite3.connect("db/vieshow.db")

    c = db.cursor()
    c.execute(
        """CREATE TABLE MOVIE
        (
            TITLE TEXT NOT NULL,
            PLACE TEXT NOT NULL,
            DATE  TEXT NOT NULL,
            TIME  TEXT NOT NULL,
            OTHER TEXT
        )
        ;"""
    )

    return db, c


# insert a movie data
def insert_db(c, title, place, date, time, other):
    c.execute("INSERT INTO MOVIE (TITLE, PLACE, DATE, TIME, OTHER) \
        VALUES (?, ?, ?, ?, ?)", (title, place, date, time, other))


# list all data in table MOVIE
def list_db(c):
    cursor = c.execute("SELECT TITLE, PLACE, DATE, TIME, OTHER from MOVIE")
    for row in cursor:
        print("TITLE = ", row[0])
        print("PLACE = ", row[1])
        print("DATE  = ", row[2])
        print("TIME  = ", row[3])
        print("OTHER = ", row[4])
        print()


print("=== Scraping Vieshow Cinema ===")
print("Creating database")
db, c = create_db()
print("Scraping")
scrap(c)
# list_db(c)
db.commit()
db.close()
print("\nDone")