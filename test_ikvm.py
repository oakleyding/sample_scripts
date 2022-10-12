#!/usr/local/bin/python3
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

import pytesseract
import cv2

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
    browser.close()
    browser.quit()
    exit(code)

if __name__ == "__main__":

    bmcip = '172.17.10.242'
    options = selenium.webdriver.ChromeOptions()
    options.add_argument("--lang=en-US");
    options.add_argument("start-maximized")
    options.add_argument("disable-infobars")
    options.add_argument('--ignore-ssl-errors=yes')
    options.add_argument('--ignore-certificate-errors')
    browser = selenium.webdriver.Chrome(options=options)
    print("Browser initialized")

    browser.get(f'https://{bmcip}/nodeexp/')
    time.sleep(2)
    browser.find_element(By.XPATH, "//input[@placeholder='Username']").send_keys("administrator")
    browser.find_element(By.XPATH, "//input[@placeholder='Password']").send_keys("advantech")
    time.sleep(2)
    browser.find_element(By.XPATH, "//button[@type='submit']").click()
    
    time.sleep(5)
    browser.get(f'https://172.17.10.242/nodeexp/rc/kvm')
    
    time.sleep(5)
    print('Refresh iKVM')
    button = findButton(browser.find_element(By.XPATH, ".//app-toolbar"), 'refresh')
    if button:
        button.click()
    else:
        print('Can not found refresh button')
        cleanQuit(-1)

    time.sleep(5)
    print('Check power status')
    button = findButton(browser.find_element(By.XPATH, ".//app-toolbar"), 'screen_share')
    if button:
        actions = ActionChains(browser) # initialize ActionChain object
        actions.move_to_element(button)
        actions.perform()
        time.sleep(10)

        msgId = button.get_attribute('aria-describedby')
        print(msgId)
        msg = browser.find_element(By.ID, msgId).get_attribute('innerHTML')
        print(msg)
        psr = re.compile(r'(On|Off)')
        mo = psr.search(msg)
        if mo is None:
            ps = ''
        else:
            ps = str(mo.group(1))
        print('Power status is %s' % ps)
        if ('Off' == ps):
            print('Power on')
            button.click()
            time.sleep(2)
            buttons = browser.find_elements(By.CLASS_NAME, 'mat-menu-item')
            buttons[0].click()
            print("Waiting 100 seconds got Linux booting up ...")
            time.sleep(100)
    else:
        print('Can not found refresh button')
        cleanQuit(-1)
    
    time.sleep(5)
    button = findButton(browser.find_element(By.CLASS_NAME, "status-bar"), 'keyboard')
    if button:
        print(button.get_attribute('innerHTML'))
        button.click()
#        actions = ActionChains(browser) # initialize ActionChain object
#        actions.move_to_element(panel)
#        actions.click(panel)
#        actions.perform()
        time.sleep(2)
    else:
        print('Not found')
    
    print("send keys")
    keys = browser.find_elements(By.TAG_NAME, "app-kvm-keyboard-key")
    sendKeys(keys, 'TestUpperLowerCases')
    keys[km['enter']].click()
    keys[km['enter']].click()
    time.sleep(5)
    sendKeys(keys, 'root')
    keys[km['enter']].click()
    time.sleep(5)
    sendKeys(keys, 'advantech')
    keys[km['enter']].click()
    
    time.sleep(10)
    
    canvas = browser.find_element(By.TAG_NAME, "canvas")
    # get the canvas as a PNG base64 string
    canvas_base64 = browser.execute_script("return arguments[0].toDataURL('image/png').substring(21);", canvas)
    # decode
    canvas_png = base64.b64decode(canvas_base64)
    # save to a file
    with open(r"canvas.png", 'wb') as f:
        f.write(canvas_png)
    
    print("Resize picture")
    img = cv2.imread(r"canvas.png")
    img = cv2.resize(img, None, fx=2, fy=2)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    cv2.imwrite(r'canvas_x2.png', img)
    
    print("Picture to text")
    print("--------------------------------")
    print(pytesseract.image_to_string(r'canvas_x2.png'))
    print("--------------------------------")
    
    time.sleep(15)
    
    browser.execute_script("window.open('about:blank', 'secondtab');")
    # It is switching to second tab now
    browser.switch_to.window("secondtab")
    # In the second tab
    time.sleep(2)
    browser.get('https://172.17.10.242/nodeexp/rc/serial')
    
    time.sleep(600)
    cleanQuit(0)
    