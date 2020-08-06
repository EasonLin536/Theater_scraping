#!/bin/bash

python3 src/ambassador_scrap.py
python3 src/showtime_scrap.py
python3 src/vieshow_scrap.py
python3 src/combine_db.py