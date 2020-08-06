import os
import sqlite3
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# theater url
theater_urls = [
    "https://www.ambassador.com.tw/home/Showtime?ID=357633f4-36a4-428d-8ac8-dee3428a5919",
    "https://www.ambassador.com.tw/home/Showtime?ID=3301d822-b385-4aa8-a9eb-aa59d58e95c9",
    "https://www.ambassador.com.tw/home/Showtime?ID=9383c5fa-b4f3-4ba8-ba7a-c25c7df95fd0",
    "https://www.ambassador.com.tw/home/Showtime?ID=1e42d235-c3cf-4f75-a382-af60f67a4aad",
    "https://www.ambassador.com.tw/home/Showtime?ID=453b2966-f7c2-44a9-b2eb-687493855d0e",
    "https://www.ambassador.com.tw/home/Showtime?ID=84b87b82-b936-4a39-b91f-e88328d33b4e",
    "https://www.ambassador.com.tw/home/Showtime?ID=5c2d4697-7f54-4955-800c-7b3ad782582c"
]

webdriver_path = "./chromedriver/chromedriver.exe"
chrome_options = Options()
chrome_options.add_argument("--headless")
driver = webdriver.Chrome(executable_path=webdriver_path, options=chrome_options)
wait = WebDriverWait(driver, 10)


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


def get_dates(dates):
    dates_html = [x.get_attribute('innerHTML') for x in dates]
    date_strs = []
    for html in dates_html:
        sub_url = html.split("\"")[1]
        date_str = sub_url[len(sub_url) - 10 : len(sub_url)].replace("/", "-")
        date_strs.append(date_str)

    return date_strs


def get_schedule_url(theater_url, date):
    date = date.replace("-", "/")
    url = f"{theater_url}&date={date}"

    return url


def get_title(info):
    title = strQ2B(info[0].text.split(")")[1].replace(" ", ""))
    other = [strQ2B(x.text.split(")")[0].split("(")[1].replace(" ", "")) for x in info]

    return title, other


def scrap(c):
    num = 0
    for theater_url in theater_urls:
        driver.get(theater_url)
        theater = wait.until(EC.presence_of_element_located((By.XPATH, "/html/body/div[2]/div[1]/div/h1"))).text
        sleep(2)

        dates = driver.find_elements_by_xpath("/html/body/div[2]/section/div/div[1]/section/div/div/div[1]/ul/li/ul/li")
        
        dates = get_dates(dates)

        for date in dates:
            movies = driver.find_elements_by_css_selector("div.theater-box")
            # print(movies[0].text)
            for movie in movies:
                info = movie.find_elements_by_css_selector("p.tag-seat")
                # print(info[0].text)
                time_lists = movie.find_elements_by_css_selector("ul.no-bullet.seat-list.theater")
                # print(time_list[0].text)

                title, others = get_title(info)

                for i in range(len(time_lists)):
                    other = others[i]
                    times = time_lists[i].find_elements_by_tag_name("h6")
                    times = [x.text for x in times]
                    # print(times)

                    for time in times:
                        insert_db(c, title, theater, date, time, other)
                        num += 1
                        print(f"scraped {num} movie sessions", end="\r")

    driver.close()


# create new database
def create_db():
    if os.path.exists("db/ambassador.db"):
        os.remove("db/ambassador.db")
    db = sqlite3.connect("db/ambassador.db")

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
        print(" " * 95 + row[4], end="\r")
        print(" " * 85 + row[3], end="\r")
        print(" " * 70 + row[2], end="\r")
        print(" " * 40 + row[1], end="\r")
        print(row[0], end="\r")
        print()


print("=== Scraping Ambassador Cinema ===")
print("Creating database")
db, c = create_db()
print("Scraping")
scrap(c)
# list_db(c)
db.commit()
db.close()
print("\nDone")