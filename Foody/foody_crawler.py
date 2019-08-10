#!/usr/bin/venv python
# coding: utf-8
#author: thienan
#email: thienan99dt@gmail.com
#date: Jul 22 2019

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains  import ActionChains

import pandas as pd
from time import sleep
from parsel import Selector
import json
import glob
import os
import csv

"""
    This is the source code to crawl foody.vn site.
    
    In this source code, I just crawl coffeeshop in foody website. Of course, you can change it.
    
    I would crawl the user's comments and rating, after then saving to csv.

    urls.txt file is to store all link crawled at self.driver.get('path').

    Requirements:
        !pip3 install selenium
        !pip3 install pandas

        You also need a foody account to sign in foody.vn site.
            - usr: your user
            - pwd: your password
        
        Installing the webkit (firefox or chrome), my source is using Chromedriver in Linux64,
        you can download the webkits in selenium website to be compatible with your OS.
        After downloading, you change the path to your webkits
            - self.driver = webdriver.Chrome('[your path to webkit]')
"""

class FoodyCrawler:
    def __init__(self):

        self.driver = webdriver.Chrome('chromedriver_linux64/chromedriver')

        self.driver.get('https://www.foody.vn/ho-chi-minh/cafe/')
        sleep(2)
        assert "Not found." not in self.driver.page_source

        print("\t\t----Login Successfully")
        usr = 'your_email@mail.com'
        pwd = 'your_password'

        log_in = self.driver.find_element_by_css_selector('#accountmanager > a')
        log_in.click()
        sleep(2)

        usr_form = self.driver.find_element_by_xpath('//*[@id="Email"]')
        pwd_form = self.driver.find_element_by_xpath('//*[@id="Password"]')
        usr_form.send_keys(usr)
        sleep(0.5)
        pwd_form.send_keys(pwd)
        sleep(0.5)

        btn_sign_in = self.driver.find_element_by_xpath('//*[@id="bt_submit"]')
        btn_sign_in.click()
        sleep(1)

    def load_more_pages_main(self, pages = 1):
        #load more pages
        error_load_page = 0
        print("\t\t-----Loading more pages")
        for t in range(pages):
            try:
                sel = self.driver.find_elements_by_xpath("//*[@id='scrollLoadingPage']")[0]
                ActionChains(self.driver).move_to_element(sel).click(sel).perform()
                sleep(2)
            except Exception as e:
                #print(e)
                error_load_page +=1
                if(error_load_page == 2):
                    break


    def get_attribute(self,path):
        div = self.driver.find_element_by_css_selector(path)
        return div.find_element_by_css_selector('a').get_attribute('href')


    def parse_urls(self):
        urls = []
        cn_urls = []
        i = 1
        error = 0

        while(1):
            try:
                path = '#result-box > div.row-view > div > div > div:nth-child(' + str(i) + ') > div.row-view-right > div.result-name > div.resname > h2'
                t = self.get_attribute(path)
                i+=1

                if(re.search(r'thuong-hieu',t)):
                    print('\t----add to cn_urls: ', t)
                    cn_urls.append(t)
                    continue

                urls.append(t)
                print('\t----add to urls: ', t)
            except Exception as e:
                print(e)
                error += 1
                if(error == 2):
                    break

        length = len(cn_urls)
        for idx in range(length):
            j = 1
            path = cn_urls[idx]
            self.driver.get(path)
            while(1):
                try:
                    print('\t----getting thuong-hieu link')
                    path = '#FoodyApp > div.pn-brand > div.ng-scope > div.fw-padding > div > div.ng-scope > ul > li:nth-child(' + str(j) + ') > div.ldc-item-header > div.ldc-item-h-name > h2'
                    t = self.get_attribute(path)
                    j+=1
                    urls.append(t)
                    print('\t----add to urls: ', t)
                except Exception as e:
                    #print(e)
                    break

        print( "A total of {total} links".format( total = len(urls) ))

        #writting file
        file = open('urls.txt','a+')
        for url in urls:
            file.write(url)
            file.write('\n')
        file.close()

        return urls

    def parse_items(self, fileName):
        with open(fileName) as f:
            urls = f.read()
            #print(urls)

        list_url = urls.split('\n')
        #flag variable is to write header of csv file
        flag = True
        comments = []
        scores = []

        print("length of list: ",len(list_url))
        print()

        length = len(list_url)

        for idx in range(length-1):
            path = list_url[idx] + '/binh-luan'
            self.driver.get(path)
            sleep(1.5)
            actions = ActionChains(self.driver)
            count = 0
            print('\t----' + str(idx) + '\t' + list_url[idx])
            while(count < 30):
                try:
                    load_more_pages = self.driver.find_element_by_xpath("//div/*[@ng-click=\'LoadMore()\']")
                    actions.move_to_element(load_more_pages).click(load_more_pages).perform()
                    self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    count +=1
                    sleep(4)
                except Exception as e:
                    count+=1

            text =  self.driver.find_elements_by_xpath("//div/span[@ng-bind-html=\'Model.Description\']")
            rating = self.driver.find_elements_by_xpath("//li/div/div/div/span[@class=\'ng-binding\']")
            print('\t\t--- text extraction')

            for txt, rat in zip(text,rating):
                try:
                    comment = txt.text
                    score = rat.text
                    #sleep(3)
                    with open('data.csv', mode='a') as f:
                        header = ['comment','rating']
                        writer = csv.DictWriter(f,fieldnames=header)

                        if flag:
                            writer.writeheader()
                            flag = False

                        writer.writerow({'comment': comment, 'rating': score})

                    comments.append(comment)
                    scores.append(score)
                except Exception as e:
                    print(e)
            print('\t\t---- writting file: DONE')

        return (comments, scores)

    def close(self):
        self.driver.close()

if __name__ == '__main__':
    api = FoodyCrawler()
    api.parse_urls()
    api.parse_items('urls.txt')
    api.close()
