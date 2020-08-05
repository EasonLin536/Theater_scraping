# Theater Scraping
Combine movie schedules of vieshow and showtime for a more convenient movie ticket searching platform.

## Uasge
### Install packages needed
```bash
pip3 install -r requirements.txt
```
### Chromedriver
[Download](https://chromedriver.chromium.org/downloads) chromedriver and place it in the folder `chromedriver`.
### Scrap https://www.vscinemas.com.tw/
```bash
python3 src/vieshow_scrap.py
```
Scraps all movies available and store in `db/vieshow.db`.
### Scrap https://www.showtimes.com.tw/
```bash
python3 src/showtime_scrap.py
```
Scraps all movies available and store in `db/showtime.db`.
### Combine 2 databases
```bash
python3 src/combine.py
```
Combines databases and store in `db/all.db`.
### Search
```bash
python3 src/search,py
```
Press `enter` for command usage.

Currently, only supports searching by name, theater, and date.