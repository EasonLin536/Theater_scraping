import os
import sqlite3
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# theater index
theater = {
    "欣欣秀泰"   : 2,
    "今日秀泰"   : 4,
    "板橋秀泰"   : 6,
    "樹林秀泰"   : 54,
    "東南亞秀泰" : 8,
    "土城秀泰"   : 55,
}

webdriver_path = "./chromedriver/chromedriver.exe"
chrome_options = Options()
chrome_options.add_argument("--headless")
driver = webdriver.Chrome(executable_path=webdriver_path, options=chrome_options)
wait = WebDriverWait(driver, 10)


# get url of different theater
def get_theater_url(theater_id):
    url = f"https://www.showtimes.com.tw/events?corpId={theater_id}"
    return url


# get url of different date
def get_schedule_url(theater_url, date):
    date = date.replace("-", "/")
    url = f"{theater_url}&date={date}"

    return url


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

# scrap showtime.com
def scrap(theater_dict, c):
    num = 0

    # get theaters
    for item in theater.items():
        place = item[0]
        # print(place)
        
        theater_url = get_theater_url(item[1])
        driver.get(theater_url)
        element = wait.until(EC.presence_of_element_located((By.XPATH, "//div/div[1]/div[2]/div[2]/div/div/div[2]/div/select[1]")))
        sleep(2)

        dates = element.text
        dates = dates.split("\n")

        # get dates
        for date in dates:
            # print(" " * 2, date)
            schedule_url = get_schedule_url(theater_url, date)

            driver.get(schedule_url)
            movie_container = wait.until(EC.presence_of_element_located((By.XPATH, "/html/body/div[2]/div/div[1]/div[2]/div[2]/div/div/div[3]")))
            sleep(2)

            movies = movie_container.find_elements_by_class_name("col-xs-12")

            # get movies
            for movie in movies:
                title = strQ2B(movie.find_elements_by_tag_name("a")[1].text.replace(" ", ""))
                # print(" " * 4, title)

                schedule = movie.find_element_by_class_name("col-md-8")
                time_rows = schedule.find_elements_by_class_name("hidden-xs")
                
                # get times
                for time_row in time_rows:
                    hall = time_row.find_elements_by_tag_name("span")[0].text
                    other = time_row.find_elements_by_tag_name("span")[1].text
                    times = time_row.find_elements_by_tag_name("div")
                    times = [x.text[0:5] for x in times]
                    # print(" " * 8 + f"{hall} : {times}")

                    for time in times:
                        insert_db(c, title, place, date, time, f"{hall}, {other}")
                        num += 1
                        print(f"scraped {num} movie sessions", end="\r")

    driver.close()

    return c


# create new database
def create_db():
    if os.path.exists("db/showtime.db"):
        os.remove("db/showtime.db")
    db = sqlite3.connect("db/showtime.db")

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


print("=== Scraping Showtine Cinema ===")
print("Creating database")
db, c = create_db()
print("Scraping")
c = scrap(theater, c)
# list_db(c)
db.commit()
db.close()
print("\nDone")