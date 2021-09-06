import threading
import time
from requests.sessions import session
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from requests_html import HTML, HTMLSession
from bs4 import BeautifulSoup
from utils.signal import AddThread, DoneThread, IsExit
from model.baiviet import add_bai_viet


def init():
    # xử lý selenium
    browser = webdriver.Chrome(executable_path='chromedriver.exe')
    browser.get('https://www.foody.vn/')
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
    html_file = open('foody.html', mode='r', encoding='utf-8')
    source = html_file.read()
    html = HTML(html=source)
    # bien check la can convert sang ma
    check = html.find('#nav-place-1', first=True).text
    list_check = list(check.split("\n"))
    list_check_string = []
    for name in list_check:
        list_check_string.append(name.rsplit(" ", 1)[0])
    browser.close()

    print("Foody gồm có những chủ đề như sau:")

    c = 1
    for sub in list_check_string:
        print("%s. %s" % (c, sub))
        c += 1

    print("%s. %s" % (c, "Tất cả"))
    print("Bạn chọn: ", end="")
    while True:
        choose = None
        try:
            choose = int(input())
        except:
            pass
        if choose is None or choose < 1 or choose > c:
            print("Lựa chọn không hợp lệ, vui long chọn lại: ", end="")
        else:
            break
    if choose < c:
        print("Đang tiến hành crawl data theo chủ đề: %s" %
              list_check_string[choose-1])
    else:
        print("Đang tiến hành crawl data của tất cả chủ đề")
    start(choose)


num = 1


def start(choose):
    global num
    # create thread
    nameTH = "FoodyFood %s" % num
    t1 = threading.Thread(target=process, name=nameTH, args=(choose,))
    t1.setDaemon(True)
    t1.start()
    num += 1


def process(choose):
    # xử lý scroll selenium và ghi ra file html
    name = threading.current_thread().name
    AddThread(name)
    isError = False
    time.sleep(1)
    browser = webdriver.Chrome(executable_path='chromedriver.exe')
    link_foody = ['https://www.foody.vn/ho-chi-minh/food/sang-trong','https://www.foody.vn/ho-chi-minh/food/buffet','https://www.foody.vn/ho-chi-minh/food/nha-hang',
    'https://www.foody.vn/ho-chi-minh/food/an-vat-via-he','https://www.foody.vn/ho-chi-minh/food/an-chay','https://www.foody.vn/ho-chi-minh/food/cafe',
    'https://www.foody.vn/ho-chi-minh/food/quan-an','https://www.foody.vn/ho-chi-minh/food/bar-pub','https://www.foody.vn/ho-chi-minh/food/quan-nhau',
    'https://www.foody.vn/ho-chi-minh/food/beer-club','https://www.foody.vn/ho-chi-minh/food/tiem-banh','https://www.foody.vn/ho-chi-minh/food/tiec-tan-noi',
    'https://www.foody.vn/ho-chi-minh/food/shop-online','https://www.foody.vn/ho-chi-minh/food/giao-com-van-phong','https://www.foody.vn/ho-chi-minh/food/foodcourt']
    try:
        start_time = None
        browser.get(link_foody[choose - 1])
        find = HTML(html=browser.page_source)
        time.sleep(2)
        browser.find_element_by_tag_name('html').send_keys(Keys.ESCAPE)
        height = browser.execute_script("return document.body.scrollHeight")
        for scroll in range(100, height, 400):
            browser.execute_script(f"window.scrollTo(0,{scroll})")
            time.sleep(1.5)
        page_source = browser.execute_script("return document.body.innerHTML;")
        f = open('OptionCategory.html', 'w', encoding='utf-8')
        f.write("<meta charset='UTF-8'> \n")
        f.write(page_source)
        time.sleep(2)
        html_file = open('OptionCategory.html', mode='r', encoding='utf-8')
        source = html_file.read()
        html = HTML(html=source)

        # xử lý link detail
        start_time = time.time()
        website = 'https://www.foody.vn'
        check = html.find('.filter-results', first=True)
        links = check.xpath('//a/@href')
        link_details = []

        for link in links:
            if "https" not in link:
                if "/thuong-hieu" in link:
                    link_details.append(website + link)
                elif ("quan" not in link) and ("/ho-chi-minh" in link):
                    link_details.append(website + link)

        # link all url item
        link_details = list(set(link_details))
        session = HTMLSession()
        link_child_detail = []
        for url in link_details:
            r = session.get(url)
            item = r.html.find('.res-common', first=True)
            if(item != None):
                full_name = item.find('.main-info-title', first=True).text
                full_name = full_name.split("\n")[0]  # Name
                active_time = item.find('.micro-timesopen', first=True).text
                active_time = active_time[0:26]  # Time
                range_price = item.find('.res-common-minmaxprice', first=True).text
                range_price = range_price.split("- ")
                price_from = range_price[0]  # Price
                price_to = range_price[1]
                rate = item.find('.microsite-point-avg',first=True).text  # Rate
                district = item.find('.res-common-add', first=True).text
                district = district.rsplit(", ", 2)[1]  # District
                # add_bai_viet(active_time=active_time, full_name=full_name,
                #              price_from=price_from, price_to=price_to,rate=rate,district=district)
            
            #xử lý chi nhánh => đang dấu hiểu bỏ
            elif(item == None):
                branch = r.html.find('.ldc-items-list', first=True)
                link_child = branch.xpath('//a/@href')               
                for url_child in link_child:
                    if "https" not in url_child:
                        if("/ho-chi-minh" in url_child):
                            link_child_detail.append(website + url_child)
                link_child_detail = list(set(link_child_detail))
                for item_child in link_child_detail:
                    r_child = session.get(item_child)
                    item_branch = r_child.html.find('.res-common', first=True)
                    if(item_branch != None):
                        full_name_branch = item_branch.find('.main-info-title', first=True).text
                        full_name_branch = full_name_branch.split("\n")[0]  # Name
                        list_check = list(full_name_branch.split("\n"))
                        list_check_string = []
                        # for name in list_check:
                        #     list_check_string.append(name.rsplit(" ", 1)[0])
                        # list_check_string = list(set(list_check_string))
                        print(list_check_string)   
                   
        time.sleep(2)
        end_time = time.time()
    except Exception as e:
        isError = True
        print(e)
    DoneThread(name)
