import os
import threading
import time
import json
import traceback
import urllib.parse
import hashlib
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from utils.logfile import create_log
from utils.signal import AddThread, DoneThread, IsExit
from utils.metric import AddMetric
from model.baiviet import add_bai_viet, get_bai_viet

def init():
    print("GoogleReview plugin")
    
    chude = input("Nhập vào chủ đề cần crawl (exit để quay lại): ")

    if chude.strip()=="exit":
        return

    print("Đang tiến hành crawl data theo chủ đề: %s"% chude)

    start(chude)

num = 1
def start(chude):
    global num
    # create thread

    nameTH = "GoogleReview %s"%num
    t1 = threading.Thread(target=process, name=nameTH,args=(chude, ))
    t1.setDaemon(True)
    t1.start()

    num += 1

# luồng hoạt động chính
def process(chude):
    # tạo logger
    logger = create_log()
    name = threading.current_thread().name

    AddThread(name)

    logger.write("Lấy chủ đề: %s"%chude)

    driver = khoi_tao_selenium()
    driver.get("https://www.google.com/search?&tbm=lcl&q=%s+tp.hcm"%(urllib.parse.quote_plus(chude)))
    # wait
    while True:
        page_state = driver.execute_script('return document.readyState;')
        if page_state == 'complete':
            break
        time.sleep(0.3)

    time.sleep(1)

    isError = False

    try: 
        # bat buoc nam trong block try except
       
        # trang i = 0
        indexPage=1
        while True:
            # kiểm tra xem có tín hiệu thoát từ main
            if IsExit():
                isError = True
                break
            
            start_time = time.time()

            # lay noi dung trang i
            logger.write("Xử lý các cửa hàng trên trang số %s..."%(indexPage))

            preAddress = laydiachicuahanghientai(driver)
            
            #get all item
            listItem = laydanhsachcuahanghientai(driver)
            for item in listItem:
                #Get link item

                try:
                    # Ấn vào link để mở ra trang thông tin
                    driver.execute_script("var ele=arguments[0]; ele.click();", item)
                except:
                    # logger.write(traceback.format_exc()) # only debugging
                    # bỏ qua
                    continue
                
                for _ in range(20):
                    currentAddress = laydiachicuahanghientai(driver)
                    if currentAddress and currentAddress != preAddress:
                        preAddress=currentAddress
                        break
                    time.sleep(0.3)

                objectData = None

                try:
                    objectData = laychitietcuahang(driver)
                except:
                    # logger.write(traceback.format_exc()) # only debugging
                    pass

                if objectData:
                    AddMetric(len(json.dumps(objectData)))

                    # insert DB
                    try:
                        add_bai_viet(
                            active_time=json.dumps(objectData["active_time"]),
                            district=objectData["district"],
                            full_name=objectData["full_name"],
                            phone=objectData["phone"],
                            price_from=objectData["price_from"],
                            price_to=objectData["price_to"],
                            rate=objectData["rate"],
                            rate_count=objectData["rate_count"],
                            url=objectData["url"],
                            website="GoogleReview",
                            website_id_quan= "GoogleReview_%s"%(objectData["id"]),
                            other_service= json.dumps(objectData["other_service"])
                        )
                    except Exception:
                        # logger.write(traceback.format_exc()) # only debugging
                        # duplicate or any error
                        pass

            end_time = time.time()
            logger.write("Thời gian xử lý: %.2f" % (end_time-start_time))

            #click next page
            try:
                # lưu lại item đầu
                listItemFirst = listItem[0].get_attribute('data-cid')

                btnLoad = driver.find_element_by_id("pnnext")
                driver.execute_script("var ele=arguments[0]; ele.click();", btnLoad)
                
                for _ in range(20):
                    listItemNextFirst = laydanhsachcuahanghientai(driver)[0].get_attribute('data-cid')
                    if listItemNextFirst and listItemNextFirst != listItemFirst:
                        break
                    time.sleep(0.3)
                # chờ load
                time.sleep(1)
                # chờ tắt overlay
                for _ in range(10):
                    overlay = driver.find_element_by_class_name("rlfl__loading-overlay")
                    if not overlay.get_attribute('style'):
                        break
                    time.sleep(0.2)

            except:
                break


            indexPage+=1

    except Exception as e:
        isError = True
        # logger.write(traceback.format_exc())
        logger.write("Stop! "+str(e))

    #garbage
    driver.close()

    if not isError:
        logger.write("Đã crawler hết tất cả cửa hàng của chủ đề này.")

    logger.close()
    DoneThread(name)

def laydiachicuahanghientai(driver):
    try:
        return driver.find_element_by_css_selector(".LrzXr").get_attribute('innerText')
    except:
        pass
    return None

def laydanhsachcuahanghientai(driver):
    try:
        return driver.find_elements_by_css_selector('[jsname="GZq3Ke"] a.a-no-hover-decoration')
    except:
        pass
    return None

def khoi_tao_selenium(hide=True):
    options = webdriver.ChromeOptions()
    options.add_argument("disable-extensions")
    options.add_argument("window-size=300,300")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36")
    
    # for remove debugger log
    options.add_experimental_option('excludeSwitches', ['enable-logging'])

    if hide:
        options.add_argument('headless')
    
    driver = webdriver.Chrome(os.path.dirname(__file__)+"/../webdriver/chromedriver.exe",
        chrome_options=options
    )

    return driver

def laychitietcuahang(driver: WebDriver):
    url_page = driver.current_url

    #Get info detail
    try:
        fullTittle = driver.find_element_by_css_selector('[data-attrid="title"]').get_attribute("innerText")
    except:
        fullTittle = ""
    try:   
        score = driver.find_element_by_css_selector(".Ob2kfd .Aq14fc").get_attribute("innerText")
    except:
        score = "2.5"

    groupInfo = driver.find_elements_by_class_name("LrzXr")
    addressDetail = groupInfo[0].get_attribute("innerText")
    phone = ""
    try:
        phone = groupInfo[1].get_attribute("innerText")
    except: 
        pass

    groupInfo = driver.find_elements_by_css_selector(".YhemCb")
    price = ""
    if len(groupInfo) > 1:
        price = groupInfo[0].get_attribute("innerText")

    tableActive = ""
    try:
        active = driver.find_element_by_class_name("WgFkxc")
        driver.execute_script("var ele=arguments[0]; ele.click();", active)
        time.sleep(0.1)
        tableActive = active.get_attribute("innerText")
    except: 
        pass
    
    danhGiaGg = "0"
    try:
        danhGiaGg = driver.find_element_by_css_selector('[data-sort_by="qualityScore"]').get_attribute("innerText")
    except: 
        pass

    other_service = ""
    try:
        other_service = driver.find_element_by_class_name("d2aWRb").find_element_by_xpath('..').get_attribute("innerText")
        other_service = other_service.replace("Các tùy chọn dịch vụ:","")
    except: 
        pass

    #Handle info from page
    #field change: website_id_quan, rate, phone, rate_count, price_from, price_to, other_service, tableActive
    hashID = hashlib.md5(addressDetail.encode('utf-8')).hexdigest()
    phone_change = phone.replace(" ", "")

    list_district = addressDetail.split(",")
    district_change = ""
    if len(list_district) > 0:
        for district_element in list_district:
            element = district_element.lower()
            if element.find("quận") > 0:
                district_change = element.replace("quận", "").strip()
        if district_change == "":
            district_change = list_district[-2].lower().strip()

    list_active_change = None
    if len(tableActive) > 0:
        try:
            list_active_change = {}
            list_timeActive = tableActive.split("\n")
            for str_time in list_timeActive:
                temp_active = str_time.index("\t",4)
                day_active = str_time[:temp_active]
                time_active = str_time[temp_active + 1:]
                list_active_change[day_active]=time_active
        except:
            list_active_change = None


    if not list_active_change:
        list_active_change = {
            "open": "00:00",
            "close": "23:59",
        }

    if score != "":
        temp = str(score.replace(",", ".").replace("Quảng cáo·", ""))
        try:
            rate_change = float(temp) * 2
        except:
            rate_change = 0
    else :
        rate_change= 0

    try:    
        rate_count_change = float(danhGiaGg.split(" ")[0])
    except:
        rate_count_change = 0

    price_from = 0
    price_to = 0

    vndCount = price.count("₫₫")
    if vndCount > 0:
        if len(price) == 1:
            price_from = 20000
            price_to = 100000
        if len(price) == 2:
            price_from = 100000
            price_to = 300000
        if len(price) > 2:
            price_from = 500000
            price_to = 1000000

    array_service = []
    if len(other_service) > 0:
        array_service = other_service.split("·")

    #field no change: website, url
    url_change = url_page
    fullName_change = fullTittle

    # lay noi dung 
    objectData ={
        "id": hashID,
        "url": url_change,
        "district": district_change,
        "rate": rate_change,
        "active_time": list_active_change,
        "full_name": fullName_change,
        "phone": phone_change,
        "rate_count": rate_count_change,
        "price_from": price_from,
        "price_to": price_to,
        "other_service": array_service
    }
    return objectData