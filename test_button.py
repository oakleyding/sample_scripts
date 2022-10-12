#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import sys
import datetime
import time
import argparse
import subprocess

import requests
import re
import codecs
from requests import session, get
from bs4 import BeautifulSoup
import undetected_chromedriver as uc


if __name__ == "__main__":

    bmcip = '172.17.10.242'
    options = uc.ChromeOptions()
    options.add_argument("start-maximized")
    options.add_argument("disable-infobars")
    options.add_argument('--ignore-ssl-errors=yes')
    options.add_argument('--ignore-certificate-errors')
    browser = uc.Chrome(options=options)
    print("Browser initialized")

    browser.get(f'https://{bmcip}/nodeexp/')
    time.sleep(2)
    browser.find_element_by_xpath("//input[@placeholder='Username']").send_keys("administrator")
    browser.find_element_by_xpath("//input[@placeholder='Password']").send_keys("advantech")
    browser.find_element_by_xpath("//button[@type='submit']").click()
    
#    time.sleep(2)
#    browser.get(f'https://{bmcip}/nodeexp/ne/config-maintenance')
#    
#    time.sleep(2)
#    browser.find_element_by_xpath("//div[@aria-posinset='3']").click()
#    
#    time.sleep(2)
#    browser.find_element_by_xpath("//input[@type='file']").send_keys('/Users/oakley/Downloads/test_button.py')
#    #browser.find_element_by_xpath("//button[@mat-raised-button]").click()
    
    time.sleep(2)
    browser.get(f'https://{bmcip}/nodeexp/ne/config-network')
    
    time.sleep(2)
    section = browser.find_element_by_xpath("//app-config-network-ipv6")
    panels = section.find_elements_by_xpath(".//mat-panel-title")
    panel = None
    for p in panels:
        if "Static IPv6" == p.text.strip():
            p = p.find_element_by_xpath("..")
            p = p.find_element_by_xpath("..")
            panel = p.find_element_by_xpath("..")
            break
    if panel:
        p = panel.find_element_by_xpath("./mat-expansion-panel-header")
        p.click()
        time.sleep(2)
        p = panel.find_element_by_xpath(".//input[@placeholder='IPv6 Address']")
        p.clear()
        p.send_keys("7fff::7")
        value = p.get_attribute("value");
        print(f"value = '{value}'")
    else:
        print('Not found')
        
    time.sleep(30)
    browser.quit()
    