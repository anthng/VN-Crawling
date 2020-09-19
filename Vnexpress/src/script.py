#!/usr/bin/env python
# coding: utf-8
#author: thienan
#email: thienan99dt[at]gmail[dot]com
#date: 03 May 2019

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import pandas as pd
from time import sleep
from parsel import Selector
import json
import glob
import os
import requests
import urllib.request

driver = webdriver.Chrome('chromedriver_linux64/chromedriver')

def get_URL():
    i = 1
    urls = []        
    lsURL = driver.find_elements_by_class_name('icon_commend')
    for url in lsURL:
        if url.get_attribute("href"):
            str_url = str(url.get_attribute("href"))
            urls.append(str_url[:-12])
            print(str(i) + "\t" + str_url[:-12])
            i +=1
    
    print( "A total of {total} links".format( total = len(urls) ))

    return urls

def get_info(lsUrls):
    count = 0
    comment_url = 'https://usi-saas.vnexpress.net/index/get?callback=okmen&offset=0&limit=1000&frommobile=0&sort=like&objectid='
    header_keys = ['No','Title', 'URL', 'ObjectID', 'SiteID', 'ObjectType', "JSON_URL"]
    df = pd.DataFrame(columns = header_keys)
    error = 0
    flag = False
    for url in lsUrls:
        try:
            driver.get(str(url))
            sleep(0.5)
        except NameError:
            print("\n==========> Error: " + str(url))
            error +=1
            continue
        
        print("Loading page: " + str(url) )
        
        sel = Selector(text=driver.page_source)
        title = sel.xpath('//*[starts-with(@class, "title_news_detail")]/text()').extract_first()
        
        if driver.find_elements_by_xpath('//*[@id="social_like"]/div[1]'):
            parent_tag = driver.find_elements_by_xpath('//*[@id="social_like"]/div[1]')
            print("===== XPath selector")
        else:
            try:
                parent_tag = driver.find_element_by_css_selector('div.item_social.font_icon')
                flag = True
                print("===== CSS selector")
            except:
                print("\n==========> Error: " + str(url))
                print("Can not select elements\n\n")
                error +=1
                continue
            
        #The way to get attribute for Xpath
        if(flag == True):
            objid = parent_tag.get_attribute('data-component-objectid')
            siteid = parent_tag.get_attribute('data-component-siteid')
            objtype = parent_tag.get_attribute('data-objecttype')
            flag = False
        else:
            for obj in parent_tag:
                objid = obj.get_attribute('data-component-objectid')
                siteid = obj.get_attribute('data-component-siteid')
                objtype = obj.get_attribute('data-objecttype')
                break
            
        direct_comment_url = comment_url + str(objid) + "&siteid=" + str(siteid) + "&objecttype=" + str(objtype)
        curURL = driver.current_url

        print(str(count) + " -- Get information:" + " " + str(curURL))
        
        if title: title = title.strip()
            
        try:
            df = df.append(pd.Series([count ,title, curURL, objid, siteid, objtype, direct_comment_url], index= df.columns ), ignore_index=True)
            print("Appending " + str(curURL) + " into dataframe ==============> DONE")
        except NameError:
            print("\n==========> Error: " + str(curURL))
            error +=1
            continue
        
        print()
        count +=1

    print("\n Collected " + str(count)+"/"+str(count+error)+ " links \n Error links: " + str(error)+"/"+str(error + count))
    print(" Error rate: {}".format( count/(count+error) ))
    if not os.path.isfile('urls.csv'):
        print("\n=========== Create 'data.csv' ===========\n")
        df.to_csv('urls.csv', index = False)
        print("Writeout CSV file ==============> DONE\n")
    else:
        df.to_csv('urls.csv', mode='a', header = None, index = False)
        print("Writeout CSV file ==============> DONE\n")  
        
    return df

def write_to_json(data):
    i = 1
    strRep = "/**/ typeof okmen === 'function' && okmen({\"error\":0,\"errorDescription\":\"\",\"iscomment\":1,"
    folder = "json/"
    for url in data["JSON_URL"]:
        sleep(2)
        response = urllib.request.urlopen(url)
        str_response = response.read().decode('utf-8')
        pre = str_response.replace(strRep, "{", 1)
        content = json.loads(pre[:-2])

        with open("json/%i.json" %i, 'w') as ofile:
            json.dump(content, ofile, sort_keys = True, indent = 4, ensure_ascii = False)
            print("Writeout {idx}.json -----> DONE".format(idx = i))
            
        i +=1

def parse_json(data_json):
    objects = data_json["data"]["items"]
    content = []
    article_id =[]
    comment_id = []
    userid = []
    userlike = []

    for obj in objects:
        article_id.append(obj["article_id"])
        content.append(obj["content"])
        comment_id.append(obj["comment_id"])
        userlike.append(obj["userlike"])
        userid.append(obj["userid"])
        
        if obj["replys"]:
            rep_objects = obj["replys"]["items"]
            for rep in rep_objects:
                article_id.append(rep["article_id"])
                content.append(rep["content"])
                comment_id.append(rep["comment_id"])
                userlike.append(rep["userlike"])
                userid.append(rep["userid"])
    
    return (article_id, userid, comment_id, content, userlike)
                
def save_to_csv():
    list_json_file = glob.glob('json/*.json')
    list_json_file.sort()
    i = 1
    for filename in list_json_file:
        print("Opening " + str(filename))
        with open(filename) as json_file:
            data_json = json.load(json_file)
            
            #convert to text
            articleID, userID, commentID, content_comment, userLike = parse_json(data_json)

            # create column name to store in dataframe
            d = {
                'article_id':articleID,
                'user_id' : userID,
                'comment_id': commentID,
                'content': content_comment,
                'userlike': userLike
            }

            df_from_json_file = pd.DataFrame(d)
            df_from_json_file.to_csv("data/%i.csv"%i)
            print("======== Saving {idx}.csv ========".format(idx = i))
            i +=1

def main():
    driver.get("https://vnexpress.net")
    sleep(0.5)

    lsUrls = get_URL()
    data = get_info(lsUrls)
    data = pd.read_csv("urls.csv")
    
    write_to_json(data)

    save_to_csv()

if __name__ == "__main__":
    main() 



