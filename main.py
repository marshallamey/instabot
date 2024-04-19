#!/usr/bin/env python3
# Author: Marshall Amey
# Date: 02/28/2020

'''Module for scraping photos from saved instagram profile collections'''
import time
import datetime
import getpass
from pathlib import Path
from instabot import Instabot

TIMESTAMP = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")
print( f"{TIMESTAMP}:: Instabot started..." )

### MAIN PROGRAM ###
username = input('Username: ')
password = getpass.getpass()
IG = Instabot()
IG.sign_in(username, password)
time.sleep(5)

# Get file save location
while True:
    try:
        path = input('Enter the path where you want to save the files: ')
        if Path(path).exists():
            IG.filepath = path
            break
        Path(path).mkdir(parents=True, exist_ok=True)
        IG.filepath = path
        break
    except Exception as e:
        print(f'Invalid directory. Try again. You need a place to save the Instagram photos\n{e}')

# Display menu options until the user exits
while True:
    try:
        IG.show_menu()
        choice = int(input())
        # 0: EXIT PROGRAM
        if choice == 0:
            break
        # 1: DOWNLOAD SAVED PHOTOS
        elif choice == 1:
            IG.go_to_saved_photos(IG.username)
            break
        # 2: DOWNLOAD PROFILE PHOTOS
        # elif choice == 2:
        #     IG.go_to_profile_photos(IG.username)
        #     break
    except FileNotFoundError as e:
        print(f'Not a file\n{e}')
        break
    except Exception as e:
        print(f'Not a number\n{e}')
        break
    finally: IG.close_browser()

TIMESTAMP = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
print( f"{TIMESTAMP}:: Instabot stopped..." )
