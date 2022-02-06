from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pymongo import MongoClient
from urllib import parse
import time
import requests
import re
import urllib.request
import ddddocr
import cv2
import api_refrenece




def main():
    webBrowserAPI = api_refrenece.WebBrowserAPI()
    websiteURL = 'https://building-management.publicwork.ntpc.gov.tw/bm_query.jsp?rt=3'              # 建管便民服務資訊網
    browser = webdriver.Chrome(executable_path='./chromedriver.exe')
    browser.get(websiteURL)

    # click the initial button
    button = browser.find_elements_by_xpath("//input[@value='關閉']")[0]
    button.click()

    # 獲得新北市地區和區內地址
    newTaipeiCityPostCode = webBrowserAPI.pass_districtInfoToWebBrowser()


    for row in newTaipeiCityPostCode:
        totalLicenseList = []
        browser.get(websiteURL)
        if int(row[0]) >= 243:
            for streetName in row[2]:
                browser.get(websiteURL)
                print('districtId: ' + str(row[1] + ', streetName: ' + streetName))
                webBrowserAPI.webInquiring(browser, districtId=row[0], streetName=streetName)
                licenseList = webBrowserAPI.webVisiting(browser, row[1])

                if licenseList:
                    totalLicenseList.extend(licenseList)
                print('totalLicenseList: ' + str(len(totalLicenseList)))
                browser.get(websiteURL)
                time.sleep(5)
            api_refrenece.MongodbAPI.writeToMongodb(totalLicenseList)       # write to Mongodb
    browser.quit()
main()