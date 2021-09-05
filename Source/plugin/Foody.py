import os
import tempfile
import time
from selenium import webdriver
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def khoi_tao_selenium(hide=True) -> WebDriver:
    options = webdriver.ChromeOptions()
    options.add_argument("user-data-dir=%s"%tempfile.gettempdir())
    options.add_argument("--disable-extensions")
    options.add_experimental_option('excludeSwitches', ['enable-logging'])

    if hide:
        # options.add_argument('headless')
        pass

    driver = webdriver.Chrome(os.path.dirname(__file__)+"/../webdriver/chromedriver.exe",
        chrome_options=options
    )

    return driver

def login():
    driver = khoi_tao_selenium()
    driver.get("https://id.foody.vn/dang-nhap?ReturnUrl=https%3A%2F%2Fid.foody.vn%2Ftai-khoan")
    
    loggedinTitle = "Thông tin cơ bản"
    try:
        WebDriverWait(driver, 120).until(EC.title_is(loggedinTitle))
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
    anchors = element.find_elements_by_css_selector("li ul.service-list li a")
    if anchors:
        urls = []
        for anchor in anchors:
            url = anchor.get_attribute('href')
            if url != "":
                urls.append(url)
        return urls
    return None

def laydanhsachcuahangtuchinhanh(url):
    driver = khoi_tao_selenium()
    driver.get(url)
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
    ret = getUrlsBrand(itemListElement)
    driver.close()
    return ret

login()

# ví dụ  Ăn uống - Sang trọng
# https://www.foody.vn/ha-noi/tiec-tan-noi + ?categorygroup=&c=

url = "https://www.foody.vn/ha-noi/tiec-tan-noi?categorygroup=&c="
driver = khoi_tao_selenium()
driver.get(url)

print(laydanhsachcuahangtieptheo(driver))
print(laydanhsachcuahangtieptheo(driver,False))
print(laydanhsachcuahangtieptheo(driver,False))
print(laydanhsachcuahangtieptheo(driver,False))

# print(laydanhsachcuahangtuchinhanh("https://www.foody.vn/thuong-hieu/king-bbq?c=ho-chi-minh"))

driver.close()
exit()


def init():
    print("Foody có những chủ đề hot như sau:")
    # ...