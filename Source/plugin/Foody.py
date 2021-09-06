import os
import time
import re
import json
import threading
import time
import traceback
from requests_html import HTMLSession
from selenium import webdriver
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from utils.metric import AddMetric
from utils.logfile import create_log
from utils.signal import AddThread, DoneThread, IsExit
from model.baiviet import add_bai_viet, get_bai_viet

shareCookies = None

def khoi_tao_selenium(cookies=None,hide=True) -> WebDriver:
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

    if cookies:
        driver.execute_cdp_cmd('Network.enable', {})
        for cookie in cookies:
            driver.execute_cdp_cmd('Network.setCookie', cookie)
        driver.execute_cdp_cmd('Network.disable', {})

    return driver

def login():
    global shareCookies

    driver = khoi_tao_selenium(hide=False)
    driver.get("https://id.foody.vn/dang-nhap?ReturnUrl=https%3A%2F%2Fid.foody.vn%2Ftai-khoan")
    
    loggedinTitle = "Thông tin cơ bản"
    try:
        WebDriverWait(driver, 150).until(EC.title_is(loggedinTitle))
        shareCookies = driver.get_cookies()
        return True
    except:
        pass
    finally:
        driver.quit()

    return False

def getUrlsCategory(element: WebElement):
    anchors=None
    try:
        anchors = element.find_elements_by_css_selector(".resname h2 a")
    except:
        pass
    if anchors:
        urls = []
        for anchor in anchors:
            url = anchor.get_attribute('href')
            if url != "":
                urls.append(url)
        return urls
    return None

def laydanhsachcuahangtieptheo(driver: WebDriver, init=True):
    itemListElement = driver.find_element_by_css_selector(".filter-results > div")
    if init:
        return getUrlsCategory(itemListElement)

    btnLoad = driver.find_element_by_id("scrollLoadingPage")
    statusesSpan = btnLoad.find_elements_by_tag_name("span")

    currentSize = int(statusesSpan[0].get_attribute('innerText'))
    totalSize = int(statusesSpan[1].get_attribute('innerText'))

    if currentSize>=totalSize:
        return None

    # xóa danh sách hiện tại
    driver.execute_script("var ele=arguments[0]; ele.innerHTML = '';", itemListElement)
    # click button thêm
    btnMore = driver.find_element_by_id("scrollLoadingPage")
    driver.execute_script("var ele=arguments[0]; ele.click();", btnMore)

    for i in range(50):
        urls = getUrlsCategory(itemListElement)
        if urls and len(urls) > 1:
            return urls
        time.sleep(0.2)

    return None

def getUrlsBrand(element: WebElement):
    anchors = element.find_elements_by_css_selector("li.ldc-item h2>a")
    if anchors:
        urls = []
        for anchor in anchors:
            url = anchor.get_attribute("href")
            urls.append(url)
        return urls
    return None

def laydanhsachcuahangtuchinhanh(url):
    global shareCookies
    driver = khoi_tao_selenium(shareCookies)
    driver.get(url)
    # wait
    while True:
        page_state = driver.execute_script('return document.readyState;')
        if page_state == 'complete':
            break
        time.sleep(0.3)
        
    itemListElement = driver.find_element_by_css_selector(".ldc-items-list")

    while True:
        btnLoad = None
        try:
            btnLoad = driver.find_element_by_class_name("fd-btn-more")
        except:
            pass
        if btnLoad:
            btnLoad.click()
            time.sleep(0.5)
        else:
            break
    time.sleep(0.5)
    ret = getUrlsBrand(itemListElement)
    driver.close()
    return ret

def laychuyenmuc():
    req = HTMLSession()
    html = req.get("https://www.foody.vn/common/_topcategorygroupmenu?isUseForSearch=false",cookies={"floc":"217"}).html
    wrapper = html.find("ul li")[1]
    links = wrapper.find("ul li a")
    ret = []
    for link in links:
        ret.append({
            "name": link.attrs["title"],
            "link": list(link.absolute_links)[0]
        })
    return ret

def laychitietcuahang(url):
    req = HTMLSession()
    html = req.get(url).html
    texthtml = html.html

    rex = re.search("initData = (.+?);",texthtml)
    if rex:
        storeDetailText = rex.group(1)
        storeDetail = json.loads(storeDetailText)

        districtFormat = storeDetail.get("District").lower().replace("quận ","").replace("tp.","").strip()
        rate = storeDetail.get("AvgRating")
        
        try:
            rate = float(rate)
        except:
            rate = 0

        active_time = {}
        TimeRanges = storeDetail.get("TimeRanges")
        OpeningTime = storeDetail.get("OpeningTime")
        if len(OpeningTime)>0:
            active_time["open"] = OpeningTime[0]["TimeOpen"]["Hours"]
            active_time["close"] = OpeningTime[len(OpeningTime)-1]["TimeClose"]["Hours"]
        elif len(TimeRanges)>0:
            active_time["open"] = TimeRanges[0].get("StartTime24h")
            active_time["close"] = TimeRanges[len(TimeRanges)-1].get("EndTime24h")
        else:
            active_time["open"] = "00:00"
            active_time["close"] = "00:00"

        TotalReview = storeDetail.get("TotalReview")
        try:
            TotalReview = float(TotalReview)
        except:
            TotalReview = 0

        TotalFavourite = storeDetail.get("TotalFavourite")
        try:
            TotalFavourite = float(TotalFavourite)
        except:
            TotalFavourite = 0

        PriceMin = storeDetail.get("PriceMin")
        try:
            PriceMin = float(PriceMin)
        except:
            PriceMin = 0

        PriceMax = storeDetail.get("PriceMax")
        try:
            PriceMax = float(PriceMax)
        except:
            PriceMax = 0

        other_service = []
        otherServiceList = html.find(".micro-property li:not(.none)")
        for otherService in otherServiceList:
            other_service.append(otherService.text)

        return len(texthtml), {
            "id": storeDetail.get("RestaurantID"),
            "url": url,
            "district": districtFormat,
            "rate": rate,
            "active_time": active_time,
            "full_name": storeDetail.get("Name"),
            "phone": storeDetail.get("Phone"),
            "rate_count": TotalReview,
            "favorite":TotalFavourite,
            "price_from":PriceMin,
            "price_to":PriceMax,
            "other_service":other_service
        }
    return len(texthtml), None

isLogin = False

def init():
    global isLogin
    if not isLogin:
        if not login():
            print("Vui lòng login foody để sử dụng plugin này.")
            return
        isLogin = True
        
    print("Đang truy xuất lấy data...",end="")
    CategoryList = laychuyenmuc()
    print("ok")

    print("Foody có những chủ đề ẩm thực hot như sau:")
    
    # tạo menu cho người dùng chọn
    c = 1
    for sub in CategoryList:
        print("%s. %s"%(c,sub["name"])) #1. abc-xyz
        c+=1
    print("%s. %s"%(c,"Quay lại")) 
    
    print("Bạn chọn: ", end="")

    while True:
        choose = None
        try:
            choose = int(input())
        except:
            pass
        if choose is None or choose < 1 or choose > c:
            print("Lựa chọn không hợp lệ, vui long chọn lại: ",end="")
        else:
            break
    
    chude = None
    
    if choose < c:
        chude = CategoryList[choose-1]
        print("Đang tiến hành crawl data theo chủ đề: %s"% chude["name"])
    else:
        return

    start(chude)

# khởi tạo luồng mới bắt buộc đặt tên thread, và không trùng
num = 1
def start(chude):
    global num
    # create thread

    nameTH = "Foody %s"%num
    t1 = threading.Thread(target=process, name=nameTH,args=(chude,))
    t1.setDaemon(True)
    t1.start()

    num += 1

# luồng hoạt động chính
def process(chude):
    global shareCookies
    # tạo logger
    logger = create_log()
    name = threading.current_thread().name

    AddThread(name)
    logger.write("Lấy chủ đề: %s"%chude["name"])

    driver = khoi_tao_selenium(shareCookies)
    driver.get(chude["link"])
    # wait
    while True:
        page_state = driver.execute_script('return document.readyState;')
        if page_state == 'complete':
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
            break
        time.sleep(0.3)

    # scroll sẽ gây refresh
    time.sleep(1)

    while True:
            page_state = driver.execute_script('return document.readyState;')
            if page_state == 'complete':
                break
            time.sleep(0.3)

    isError = False

    isFirst=True
    pageindex = 1
    try: 
        # bat buoc nam trong block try except
        while True:
            # kiểm tra xem có tín hiệu thoát từ main
            if IsExit():
                isError = True
                break
            
            start_time = time.time()

            #lay ra cua hang trang i
            logger.write("Xử lý các cửa hàng trên trang số %s..."%(pageindex))

            urlList = laydanhsachcuahangtieptheo(driver,isFirst)
            if urlList:
                while len(urlList) > 0:
                    url = urlList.pop(0)

                    if not url: #đôi khi None
                        continue
                    
                    if "/thuong-hieu/" in url:
                        try:
                            urlRes = laydanhsachcuahangtuchinhanh(url)
                            urlList.extend(urlRes)
                        except:
                            # logger.write(traceback.format_exc()) # only debugging
                            # logger.write("Error by: %s"%url)
                            pass

                    else:
                        data = None
                        try:
                            size, data = laychitietcuahang(url)
                            AddMetric(size)
                        except:
                            # logger.write(traceback.format_exc()) # only debugging
                            # logger.write("Error by: %s"%url)
                            pass
                        
                        if data:
                            try:
                                add_bai_viet(
                                    website_id_quan= "Foody_%s"%data["id"],
                                    website="Foody",
                                    url=data["url"],
                                    district=data["district"],
                                    rate=data["rate"],
                                    active_time=json.dumps(data["active_time"]),
                                    full_name=data["full_name"],
                                    phone=data["phone"],
                                    rate_count=data["rate_count"],
                                    favorite=data["favorite"],
                                    price_from=data["price_from"],
                                    price_to=data["price_to"],
                                    other_service=json.dumps(data["other_service"]),
                                )
                            except Exception:
                                # logger.write(traceback.format_exc()) # only debugging
                                # duplicate or any error
                                pass
            else:
                break
            
            end_time = time.time()
            logger.write("Thời gian xử lý: %.2f" % (end_time-start_time))

            pageindex+=1
            isFirst=False

    except Exception as e:
        isError = True
        # logger.write(traceback.format_exc()) # only debugging
        logger.write("Stop! "+str(e))

    #garbage
    driver.close()

    if not isError:
        logger.write("Đã crawler hết tất cả cửa hàng của chủ đề này.")

    logger.close()
    DoneThread(name)
