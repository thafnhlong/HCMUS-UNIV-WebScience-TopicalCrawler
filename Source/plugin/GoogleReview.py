import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys

def init():
    print("GoogleReview có những chủ đề hot như sau:")
    mock= ["Nhà hàng quận 1", "Nhà hàng quận 2", "Nhà hàng quận 3", "Nhà hàng quận 4"]
    # tạo menu cho người dùng chọn
    c = 1
    for sub in mock:
        print("%s. %s"%(c,sub))
        c+=1
    
    print("%s. %s"%(c,"Tất cả"))
    
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
    
    if choose < c:
        print("Đang tiến hành crawl data theo chủ đề: %s"%mock[choose-1])
    else:
        print("Đang tiến hành crawl data của tất cả chủ đề")
    
    # ...
    chrome_options = Options()
    chrome_options.add_argument("--window-size=1920x1080")
    driver = webdriver.Chrome(chrome_options=chrome_options, executable_path="webdriver\chromedriver")
    url = "https://google.com"
    driver.get(url)
    time.sleep(2)
    
    # input 
    login = driver.find_element_by_xpath("//input").send_keys(mock[choose-1])
    driver.find_element_by_xpath("//input").send_keys(Keys.ENTER)
    time.sleep(2)

    # select button Xem Tat ca
    confirm = driver.find_element_by_xpath("//*[text()= 'Xem tất cả']")
    confirm.click()
