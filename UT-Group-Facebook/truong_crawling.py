from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException

import time
import json

import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

class FacebookScraper(object):
    def __init__(self,scroll_time = 10, max_miss = 53):

        self.scroll_time = scroll_time
        self.max_miss = max_miss

        chrome_options = webdriver.ChromeOptions()

        prefs = {"profile.default_content_setting_values.notifications" : 2}

        chrome_options.add_experimental_option("prefs", prefs)
        chrome_options.add_argument("--headless") #headless: dont display chromebrowser

        #chrome_options.add_argument("--start-fullscreen")
        self.driver = webdriver.Chrome('./chromedriver_win32/chromedriver.exe', chrome_options=chrome_options)

    def load_facebook(self, url):

        self.driver.get(url)

        for i in range(self.scroll_time):
            time.sleep(1)

            if i % 32 == 0:
                print("Scroll {0}".format(i))

            self.scroll_page()

    def __scrape(self, i):

        thread_xpath = '//*[@id="mount_0_0"]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div[4]/div/div/div/div/div[1]/div[2]/div/div['+str(i)+']/div/div/div/div/div/div/div/div[2]/div'
        try:
            auth = self.driver.find_element_by_xpath(thread_xpath + '/div[2]/div/div[2]/div/div[1]/span/h2/strong').text
            cmt = self.driver.find_element_by_xpath(thread_xpath + '/div[3]/div[1]/div').text
            react = self.driver.find_element_by_xpath(thread_xpath + '/div[4]/div/div/div[1]/div/div[1]/div/div[1]/span[2]/span/span').text
            return auth, cmt, react
        except:
            print("[FAILED]: Failed at ", i)

    def get_comment(self, file_out):
        self.scroll_page()
        time.sleep(5)
        miss = 0
        data = list()
        i = 2
        while True:
            comment = dict()
            try:
                auth, cmt, react = self.__scrape(i)
                i +=1
                miss = 0
            except:
                miss +=1
                i+=1
                if miss > self.max_miss:
                    break
                continue
            comment['author'] = auth
            comment['text'] = cmt
            comment['reaction'] = react
            data.append(comment)

        with open(file_out, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    def scroll_page(self):
        # Scroll down to bottom

        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    def close(self):
        self.driver.close()

if __name__ == '__main__':

    url = "https://www.facebook.com/groups/dhgtvt.tphcm/"

    scraper = FacebookScraper(2, 7)
    scraper.load_facebook(url)
    scraper.get_comment('./data/gtvt.json')
    scraper.close()
    print(">>[INFO] Done\n")
