#!/usr/bin/env python
# coding: utf-8
#author: thienan
#email: thienan99dt@gmail.com
#date: Jun 17 2019

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import getpass
import pandas as pd
from time import sleep
from parsel import Selector

class LinkedinCrawler:
    def __init__(self):
        print("\nSign in Linkedin\n")
        self.usr = input("Email/User: ")
        self.pwd = getpass.getpass("Password: ")
        #change path web.driver.Chrome if you use Windows/MacOS
        self.driver = webdriver.Chrome('chromedriver_linux64/chromedriver') 
    
        self.driver.get('https://www.linkedin.com')
        sleep(2)
        
        usr_form = self.driver.find_element_by_class_name('login-email')
        pwd_form = self.driver.find_element_by_class_name('login-password')
        usr_form.clear()
        
        usr_form.send_keys(self.usr)
        sleep(0.5)
        pwd_form.send_keys(self.pwd)
        sleep(0.5)
        
        btn_sign_in = self.driver.find_element_by_xpath('//*[@type="submit"]')
        btn_sign_in.click()
        sleep(1)
        assert "Not found." not in self.driver.page_source
    
    def search_google(self, query):
        self.driver.get('https:www.google.com')
        sleep(2)

        search_query = self.driver.find_element_by_name('q')
        keyword = "site:linkedin.com/in/ AND " + str(query)
        search_query.send_keys(keyword)
        search_query.send_keys(Keys.RETURN)
        sleep(1)
        
    def get_URL(self, pageNumber = 1 , pageLimit = 1):
        linkedin_urls = []        
        while(pageNumber <= pageLimit):
            lsURL = self.driver.find_elements_by_class_name('iUh30')
            for url in lsURL:
                linkedin_urls.append(url.text)
                print(url.text)

            pageNumber +=1

            direct = "//a[@aria-label='Page " + str(pageNumber) +"']"
            page = self.driver.find_element_by_xpath(direct)
            try:
                page.click()
                sleep(75)
            except NameError:
                print("\nPage " + str(pageNumber) + "may exceed limit page of Google Search.")
                break
                
        
        print( "A total of {total} links".format( total = len(linkedin_urls) ))
        return linkedin_urls


    def get_profile(self, linkedin_urls):
        count = 1
        header_keys = ['Name', 'Job', 'Company', 'College', 'Location', 'URL']
        df = pd.DataFrame(columns = header_keys)
        
        for linkedin_url in linkedin_urls:
            self.driver.get(linkedin_url)
            sel = Selector(text=self.driver.page_source)

            fullName = sel.xpath('//*[starts-with(@class, "pv-top-card-section__name")]/text()').extract_first()
            job = sel.xpath('//*[starts-with(@class, "pv-top-card-section__headline")]/text()').extract_first()
            company = sel.xpath('//*[starts-with(@class,"pv-top-card-v2-section__entity-name pv-top-card-v2-section__company-name")]/text()').extract_first()
            college = sel.xpath('//*[starts-with(@class,"pv-top-card-v2-section__entity-name pv-top-card-v2-section__school-name")]/text()').extract_first()
            location = sel.xpath('//*[starts-with(@class, "pv-top-card-section__location")]/text()').extract_first()
            curURL = self.driver.current_url
            print("Get:" + str(count) + " " + str(curURL))
            count +=1
            
            if fullName:
                fullName = fullName.strip()
            if job:
                job = job.strip()
            if company:
                company = company.strip()
            if college:
                college=college.strip()
            if location:
                location = location.strip()


            df = df.append(pd.Series([fullName,job, company, college, location, curURL], index=df.columns ), ignore_index=True)
            print("Appending " + str(curURL) + " into dataframe done")
            sleep(125)

        
        return df
    
    def close(self):
        self.driver.quit()