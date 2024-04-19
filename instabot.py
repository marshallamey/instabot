#!/usr/bin/env python3
# Author: Marshall Amey
# Date: 02/28/2020

'''
Instabot class
'''
import os
import re
import time
import urllib.request
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup


class Instabot:

    """
    Constructs an Instabot object.  It's variables are composed of the username
    of the profile that is logging in to Instagram and an array of the profiles
    that are going to be downloaded.
    Information about the Webdriver and ChromeOptions can be found at the site below:
    https://sites.google.com/a/chromium.org/chromedriver/capabilities
    """

    def __init__(self):
        self.browser_profile = webdriver.ChromeOptions()
        self.browser_profile.add_experimental_option('prefs', {
            'profile.default_content_setting_values.notifications': 2,
            'profile.managed_default_content_settings.popups': 2,
            'profile.managed_default_content_settings.geolocation': 2,
        })
        self.browser = webdriver.Chrome(options=self.browser_profile)
        self.ig_profiles = []
        self.username = ''
        self.filepath = ''


    # Sign in to Instagram using credentials provided by user
    def sign_in(self, username, password):
        '''Function for signing in to Instagram'''
        self.username = username
        self.browser.get('https://www.instagram.com/accounts/login/')
        time.sleep(2)

        username_input = self.browser.find_element('name', 'username')
        password_input = self.browser.find_element('name', 'password')

        username_input.send_keys(username)
        password_input.send_keys(password)
        password_input.send_keys(Keys.ENTER)
        time.sleep(5)

    def show_menu(self):
        '''Presents user with media dowload options'''
        print('\nEnter 1 to download saved pictures')
        # print('Enter 2 to download profile pictures')
        print('Enter 0 to exit')

    def go_to_profile_photos(self, profile):
        '''    
        # Navigates to profile(s) to get media from page
        '''
        self.browser.get(f'https://www.instagram.com/{profile}/')
        self.get_media()

    def go_to_saved_photos(self, profile):
        '''    
        # Navigates to profile(s) to get saved media
        '''
        self.browser.get(f'https://www.instagram.com/{profile}/saved/all-posts/')
        self.get_media()

    def get_media(self):
        '''Collects URLs for all images and videos on an Instagram page into separate lists'''
        time.sleep(10)
        # Create destination path for media
        asset_folder = self.filepath
        print(asset_folder)
        body = self.browser.find_element(By.TAG_NAME, "body")
        print (body)

        ## Create lists for media URLs
        # last_urls = [0,0]
        temp_img_urls = ['']
        temp_vid_urls = ['']
        img_urls = []
        vid_urls = []
        prev_img_len = -1
        prev_vid_len = -1

        # Loop until no new URLs are added
        #while len(last_urls) != len(temp_img_urls) or last_urls[0] != temp_img_urls[0]:
        while (prev_img_len != len(img_urls) or prev_vid_len != len(vid_urls)):
            # last_urls = temp_img_urls
            temp_img_urls = []
            temp_vid_urls = []
            prev_img_len = len(img_urls)
            prev_vid_len = len(vid_urls)

            # Find new media
            soup = BeautifulSoup(self.browser.page_source, 'html.parser')
            imgs = soup.article.find_all('img')
            print(imgs)
            vids = soup.article.find_all('span', attrs={"aria-label": "Video"})
            print(vids)

            # Create temporary lists
            for img in imgs:
                temp_img_urls.append(img['src'])
            for vid in vids:
                temp_vid_urls.append(vid.parent.parent['href'])

            # Search for last_img_url of img_urls in temp_img_urlsXXI@iKR6WN$7
            last_img_url = ''
            last_vid_url = ''
            found_img_url = -1
            found_vid_url = -1
            if len(img_urls) > 0:
                last_img_url = img_urls[len(img_urls) - 1]
            if len(vid_urls) > 0:
                last_vid_url = vid_urls[len(vid_urls) - 1]
            if last_img_url in temp_img_urls:
                found_img_url = temp_img_urls.index(last_img_url)
            if last_vid_url in temp_vid_urls:
                found_vid_url = temp_vid_urls.index(last_vid_url)
            print(
                f'Found {len(temp_img_urls) - found_img_url - 1} '
                f'new images and {len(temp_vid_urls) - found_vid_url - 1} new videos...'
            )

            # Add new URLS to the master lists
            for url in temp_img_urls[found_img_url+1:]:
                if not os.path.isfile(Path(f'{asset_folder}/{self.url2jpg(url)}')):
                    img_urls.append(url)
            for url in temp_vid_urls[found_vid_url+1:]:
                vid_urls.append(url)
            print(f'Current Total: {len(img_urls)} pics : {len(vid_urls)} vids')

            # print(
            #f'lURL:{len(last_urls)} != tURL{len(temp_img_urls)} \n'
            #f'{last_urls[0]} != {temp_img_urls[0]}'
            #)

            # Scroll down the page
            for _ in range(4):
                body.send_keys(Keys.PAGE_DOWN)
                time.sleep(1)
            time.sleep(1.5)

        self.download_media(img_urls, vid_urls, asset_folder)


    def download_media(self, imgs, vids, destination):
        '''Loops through image and video lists and retrieves media'''
        ## Download images
        for num, url in enumerate(imgs, start=1):
            filename = self.url2jpg(url)
            print(f'Saving ({num}/{len(imgs)}): {filename}...')
            if not os.path.isfile(Path(f'{destination}/{filename}')):
                urllib.request.urlretrieve(url, Path(f'{destination}/{filename}'))
        ## Download videos
        for num, url in enumerate(vids, start=1):
            self.browser.get(f'https://www.instagram.com/{url}')
            soup = BeautifulSoup(self.browser.page_source, 'html.parser')
            vid = soup.article.video['src']
            filename = self.url2mp4(vid)
            print(f'Saving ({num}/{len(vids)}): {filename}...')
            if not os.path.isfile(Path(f'{destination}/{filename}')):
                urllib.request.urlretrieve(vid, Path(f'{destination}/{filename}'))


    def url2jpg(self, url):
        '''Finds the jpeg filename embedded in the URL'''
        # Retrieve JPEG name from URL
        base = os.path.basename(url)
        filename = re.match(r'^.*\.jpg', base)
        if filename:
            print('FILENAME: ', filename.group())
            return filename.group()
        return None


    def url2mp4(self, url):
        '''Finds the mp4 filename embedded in the URL'''
        # Retrieve mp4 name from URL
        base = os.path.basename(url)
        filename = re.match(r'^.*\.mp4', base)
        return filename.group()

    def close_browser(self):
        '''Closes browser window'''
        print('Exiting program...\n')
        self.browser.close()
