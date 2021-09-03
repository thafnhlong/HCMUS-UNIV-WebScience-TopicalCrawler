import threading
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from requests_html import HTML, HTMLSession
from bs4 import BeautifulSoup
from utils.signal import AddThread, DoneThread, IsExit
from model.baiviet import add_bai_viet, get_bai_viet
import io

def init():
    #xử lý selenium
    browser = webdriver.Chrome(executable_path='chromedriver.exe')
    browser.get('https://www.foody.vn/ha-noi')
    find = HTML(html=browser.page_source)
    time.sleep(3)
    browser.find_element_by_tag_name('html').send_keys(Keys.ESCAPE)
    from_location = browser.find_elements_by_id('head-navigation')
    from_location[0].click()
    from_location = browser.find_elements(By.XPATH, "//*[text()='Ăn uống']")
    hover_title = browser.find_element_by_id("gcat-1")
    hover = ActionChains(browser).move_to_element(hover_title)
    hover.perform()
    time.sleep(3)
    page_source = browser.execute_script("return document.body.innerHTML;")
    f = open('foody.html', 'w', encoding='utf-8') 
    f.write("<meta charset='UTF-8'> \n")
    f.write(page_source)
    time.sleep(3)

    # xử lý dữ liệu về file
    html_file = open('foody.html',mode='r',encoding='utf-8')
    source = html_file.read()
    html = HTML(html=source)

    print("Foody gồm có những chủ đề như sau:")
     
    check = html.find('#nav-place-1', first=True).text
    print(check)

    

    # mock= ["Thức ăn", "Nước uống", "Ăn vặt"]

    # c = 1
    # for sub in mock:
    #     print("%s. %s"%(c,sub))
    #     c+=1

    # print("%s. %s"%(c,"Tất cả"))

    # print("Bạn chọn: ", end="")

    # while True:
    #     choose = None
    #     try:
    #         choose = int(input())
    #     except:
    #         pass
    #     if choose is None or choose < 1 or choose > c:
    #         print("Lựa chọn không hợp lệ, vui long chọn lại: ",end="")

    #     else:
    #         break

    # if choose < c:
    #     print("Đang tiến hành crawl data theo chủ đề: %s"%mock[choose-1])
    # else:
    #     print("Đang tiến hành crawl data của tất cả chủ đề")

    start()


def start():
    print("end")
