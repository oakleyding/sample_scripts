#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import sys
import datetime
import time
import argparse
import subprocess

import re
import base64
import selenium.webdriver
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains

#import pytesseract

bmcip = ''
password = ''

# build key mapping
km = {'enter': 69, 'shift': 70}
for ci, c in enumerate('`1234567890-='):
    km[c] = 21 + ci
for ci, c in enumerate('qwertyuiop[]\\'):
    km[c] = 40 + ci
for ci, c in enumerate('asdfghjkl;\''):
    km[c] = 58 + ci
for ci, c in enumerate('zxcvbnm,./'):
    km[c] = 71 + ci

def findButton(bar, key):
    buttons = bar.find_elements(By.XPATH, ".//button")
    for b in buttons:
        icon = b.find_element(By.XPATH, ".//mat-icon")
        text = icon.get_attribute('innerHTML')
        text = text.strip()
        if key == text:
            return b
    return None

def sendKeys(keys, key):
    for k in key:
        if k.isupper():
            keys[km['shift']].click()
            k = k.lower()
        ki = km[k]
        keys[ki].click()

def cleanQuit(code):
    browser1.close()
    browser1.quit()
    browser2.close()
    browser2.quit()
    exit(code)

def launchSerial(browser):
    browser.get(f'https://{bmcip}/nodeexp/')
    time.sleep(2)
    try:
        browser.switch_to.alert.accept();
    except selenium.common.exceptions.NoAlertPresentException:
        print("Unable to locate alert")

    try:
        browser.find_element(By.XPATH, "//input[@placeholder='Username']").send_keys("admin")
        browser.find_element(By.XPATH, "//input[@placeholder='Password']").send_keys(password)
        time.sleep(2)
        browser.find_element(By.XPATH, "//button[@type='submit']").click()
        print("login initialized")
    except selenium.common.exceptions.NoSuchElementException:
        print("login bypassed")

    time.sleep(2)
    try:
        browser.get(f'https://{bmcip}/nodeexp/rc/serial')
        browser.switch_to.alert.accept();
    except selenium.common.exceptions.NoAlertPresentException:
        print("Unable to locate alert")

    try:
        time.sleep(2)
        buttons = browser.find_elements(By.XPATH, "//button[contains(@class, 'mat-raised-button')]")
        for b in buttons:
            span = b.find_element(By.XPATH, ".//span")
            text = span.get_attribute('innerHTML').strip()
            if 'OK' == text:
                b.click()
    except selenium.common.exceptions.NoSuchElementException:
        print("Unable to locate OK element, ignore")

    try:
        time.sleep(2)
        buttons = browser.find_elements(By.XPATH, "//button[contains(@class, 'mat-raised-button')]")
        for b in buttons:
            span = b.find_element(By.XPATH, ".//span")
            text = span.get_attribute('innerHTML').strip()
            if 'Yes' == text:
                b.click()
    except selenium.common.exceptions.NoSuchElementException:
        print("Unable to locate element, ignore")
    
    print('Reditected to serial')

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='auto launch BMC remote serial')
    parser.add_argument("-p", "--password", help="password of admin", required=True)
    parser.add_argument("--ip", help="ip of bmc", required=True)
    # parse input arguments
    args = parser.parse_args()
    password = args.password
    bmcip = args.ip
    
    options = selenium.webdriver.ChromeOptions()
    options.add_argument("--lang=en-US");
    options.add_argument("start-maximized")
    options.add_argument("--window-size=960,1080")
    options.add_argument("disable-infobars")
    options.add_argument('--ignore-ssl-errors=yes')
    options.add_argument('--ignore-certificate-errors')
    
    browser1 = selenium.webdriver.Chrome(options=options)
    browser1.set_window_position(0, 0, windowHandle='current')
    browser1.set_page_load_timeout(10)
    browser1.implicitly_wait(5);
    browser2 = selenium.webdriver.Chrome(options=options)
    browser2.set_window_position(960, 0, windowHandle='current')
    browser2.set_page_load_timeout(10)
    browser2.implicitly_wait(5);
    round = 0
    while True:
        try:
            round = round + 1
            print("Starting round " + str(round))
            launchSerial(browser1)
            time.sleep(5)
            launchSerial(browser2)
            time.sleep(10)
        except Exception as e:
            print(str(e))
            break

    cleanQuit(0)
