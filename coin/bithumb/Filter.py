#!/usr/bin/env python
# coding: utf-8

# In[5]:


# -*- coding: utf-8 -*-
import os, sys
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service


def transaction_end_filter():
    # 크롬드라이버 실행
    service = Service()
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver1 = webdriver.Chrome(service=service, options=options)
    #driver1 = webdriver.Chrome()
    url0 = 'https://cafe.bithumb.com/view/boards/43?keyword=&noticeCategory=6'
    driver1.get(url0)
    time.sleep(3)
    tbody1 = driver1.find_element(By.XPATH, '/html/body/div[1]/div/div[1]/div/div/table/tbody')

    result = ""
    for tr in tbody1.find_elements(By.TAG_NAME, "tr"):
        txt = []
        for td in tr.find_elements(By.TAG_NAME, "td"):
            txt_buf = td.get_attribute("innerText")
            txt.append(txt_buf)
        if "[거래지원종료]" in txt[1]:
            print(txt[1].strip())
            result+= txt[1].strip().split("(")[1].split(")")[0] +"\n"
    driver1.quit()

    f = open("must_not_buy.txt", "w")
    f.write(result)
    f.close()