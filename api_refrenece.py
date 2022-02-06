from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pymongo import MongoClient
from urllib import parse
import pandas as pd
import time
import requests
import re
import urllib.request
import ddddocr
import cv2




class PostCodeAPI:
    def get_NewTaipeiCity_postCode(self):
        districtList = []           # 記錄新北市 postcode
        websiteURL = 'https://payroll.nsysu.edu.tw/pay/rcxf_CITYCODE.php?s_CITY=%B7s%A5_%A5%AB&TextBox1=1'      # 新北市 郵遞區號網頁
        browser = webdriver.Chrome(executable_path='./chromedriver.exe')

        browser.get(websiteURL)
        bs = BeautifulSoup(browser.page_source, 'html.parser')
        allPostCode = bs.findAll('a')

        for postCode in allPostCode:
            try:
                onclickValue = str(postCode['onclick'])
                startIndex = onclickValue.find("(")
                endIndex = onclickValue.find(")")
                postCode_and_district = onclickValue[startIndex + 1:endIndex].replace("'", "")
                postCode_and_district = postCode_and_district.split(',')
                districtList.append([postCode_and_district[0], postCode_and_district[1]])
            except:
                print('district not find')

        return districtList


    def get_NewTaipeiCity_street(self):
        postCodeAPI = PostCodeAPI()
        websiteURL = 'https://www.319papago.idv.tw/lifeinfo/postcode/'              # 中華郵政網頁

        newTaipeiCityPostCode = postCodeAPI.get_NewTaipeiCity_postCode()
        browser = webdriver.Chrome(executable_path='./chromedriver.exe')


        for row in newTaipeiCityPostCode:
            streetInfoList = []         # 紀錄當前地區所有路段
            websiteURL_withPostCode = websiteURL + 'postcode-' + row[0] + '.html'
            browser.get(websiteURL_withPostCode)
            bs = BeautifulSoup(browser.page_source, 'html.parser')
            districtStreet = bs.findAll('td', string=re.compile(r'{}'.format(row[0])))

            for rowStreet in districtStreet:
                try:
                    streetInfo = rowStreet.find_next_sibling("td").text
                    if streetInfo.replace(row[1], "") not in streetInfoList:
                        streetInfoList.append(streetInfo.replace(row[1], ""))
                except:
                    print('street not find')
            row.append(streetInfoList)

        return newTaipeiCityPostCode


class MongodbAPI():
    def writeToMongodb(totalLicenseList):
        client = MongoClient()                                   # MongoDB: Client of LocalHost
        database = client["License"]                             # MongoDB: Database Name
        collection = database["NewTaipeiCityLicense"]            # MongoDB: Collection Name

        columns_name = ['區域', '使照號碼', '建照號碼', '起造人', '設計人', '建築地址(代表號)', '發照日期']
        license_df = pd.DataFrame()
        license_df = license_df.append(pd.DataFrame(totalLicenseList, columns=columns_name), ignore_index=True)
        print('MongoDB size:'  + str(license_df.shape))

        records = license_df.to_dict(orient="records")
        collection.insert_many(records)



class WebBrowserAPI():
    def pass_districtInfoToWebBrowser(self):
        postCodeAPI = PostCodeAPI()
        return postCodeAPI.get_NewTaipeiCity_street()

    def find_totalPages(self, browser):
        try:
            totalpagesText = browser.find_element_by_tag_name('tfoot').text
            startIndex = str(totalpagesText).find('[')
            endIndex = str(totalpagesText).find(']')

            totalpages = str(totalpagesText)[startIndex:endIndex + 1]
            totalpages = totalpages.split('，')[1]
            startIndexofPage = str(totalpages).find('共')
            endIndexofPage = str(totalpages).find('頁')

            totalpages = totalpages[startIndexofPage + 1:endIndexofPage]
            totalpages = int(totalpages)

            return totalpages
        except:
            return None


    def webInquiring(self, browser, districtId, streetName):
        jsScript = "document.getElementById('D1').value='{}'".format(districtId)            # 輸入地區 postcode
        street = browser.find_element_by_id('D3')                                           # 輸入地區路名
        browser.execute_script(jsScript)
        street.send_keys(streetName)

        self.get_VerificationCode(browser)
        browser.find_element_by_class_name('bouton-contact').click()


    def webVisiting(self, browser, districtName):
        bs = BeautifulSoup(browser.page_source, 'html.parser')
        totalpages = self.find_totalPages(browser)

        licenseList = []
        print('totalpages: ' + str(totalpages))
        currentPage = 1
        if totalpages:
            while currentPage <= totalpages:
                print('currentPage: ' + str(currentPage) + ', totalpages: ' + str(totalpages))
                pageDetail = self.get_licenseInfo_ALLPage(browser, districtName)
                licenseList.extend(pageDetail)
                currentPage += 1
                if currentPage <= totalpages:
                    try:
                        nextPagebutton = browser.find_elements_by_xpath("//a[contains(@onclick,'gop(" + str(currentPage) + ");return false;')]")[0]
                        nextPagebutton.click()
                    except:
                        print('nextPagebutton error')
            return licenseList
        else:
            print('查無資料')

    def get_licenseInfo_ALLPage(self, browser, districtName):
        bs = BeautifulSoup(browser.page_source, 'html.parser')
        licenseDetail = bs.findAll('tr')
        pageDetail = self.get_licenseInfo_Detail(licenseDetail, districtName)

        return pageDetail

    def get_licenseInfo_Detail(self, bspage, districtName):
        dummy = []
        for row in bspage:
            temp = []
            try:
                # districtName: 區域
                # licenseNumber: 使照號碼
                # buildingNumber: 建照號碼
                # buildPerson: 起造人
                # designer: 設計人
                # address: 建築地址(代表號)
                # issueDate: 發照日期
                temp.append(districtName)
                licenseNumber = row.find('a', {'headers':'th_a1'}).text
                temp.append(licenseNumber)
                try:
                    buildingNumber = row.find('td', {'headers':'th_a2'}).text
                    temp.append(buildingNumber)
                except:
                    temp.append('')
                try:
                    buildPerson = row.find('td', {'headers':'th_a3'}).text
                    temp.append(buildPerson)
                except:
                    temp.append('')
                try:
                    designer = row.find('td', {'headers':'th_a3-1'}).text
                    temp.append(designer)
                except:
                    temp.append('')
                try:
                    address = row.find('td', {'headers':'th_a4'}).text
                    temp.append(address)
                except:
                    temp.append('')
                try:
                    issueDate = row.find('td', {'headers':'th_a5'}).text
                    temp.append(issueDate)
                except:
                    temp.append('')
                dummy.append(temp)
            except:
                print('not license datail row')
        return dummy

    def img_process(self, filePath):
        img = cv2.imread(filePath)
        img = img[420:460,420:520]
        # img = img[400:450,580:700]
        cv2.imwrite(filePath, img)


    def get_VerificationCode(self, browser):
        mainTab = browser.current_window_handle                             # 主頁面tab id
        imageURL = browser.find_element_by_id("codeimg").get_attribute("data-source")

        browser.switch_to.new_window('tab')                                 # 切換到新分頁並開啟驗證碼
        browser.get('https://building-management.publicwork.ntpc.gov.tw/ImageServlet')
        browser.save_screenshot('VerificationCodeScreenshot.png')           # 儲存驗證碼圖片
        self.img_process('VerificationCodeScreenshot.png')                  # 裁切驗證碼圖片

        ocr = ddddocr.DdddOcr()
        with open('VerificationCodeScreenshot.png', 'rb') as f:
            imageDigit = f.read()
        ocr_result = ocr.classification(imageDigit)

        browser.close()                                                     # 關閉分頁
        browser.switch_to.window(mainTab)                                   # 切換回主分頁
        verify_code = browser.find_element_by_id('Z1')
        verify_code.send_keys(ocr_result)