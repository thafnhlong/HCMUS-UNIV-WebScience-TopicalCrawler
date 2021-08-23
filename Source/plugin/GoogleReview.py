import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

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

    #get all item
    listItem = driver.find_elements_by_class_name("VkpGBb")
    for item in listItem:
        #Get link item
        tag_current = item.find_element_by_tag_name('a')
        tag_current.click()
        time.sleep(3)
        url_page = driver.current_url

        #Get info detail
        title = item.find_element_by_class_name("dbg0pd").find_element_by_tag_name('div').text
        fullTittle = driver.find_element_by_class_name("SPZz6b").find_element_by_tag_name('h2 span').text
        score = item.find_element_by_class_name("rllt__details").find_element_by_tag_name('div span').text
        address = item.find_element_by_class_name("rllt__details").find_element_by_tag_name('div:nth-child(2)').text
        addressDetail = driver.find_element_by_class_name("LrzXr").text
        website = url
        phone = ""
        try:
            phone = driver.find_element_by_class_name("kno-fv").find_element_by_tag_name('a span').text
        except NoSuchElementException: 
            pass
        
        other_service = ""
        try:
            other_service = driver.find_element_by_xpath("//c-wiz[@class='u1M3kd W2lMue']").find_element_by_tag_name('div').text
        except NoSuchElementException: 
            pass
        
        price = ""
        try:
            price = driver.find_element_by_class_name("vk_gy").find_element_by_tag_name('span span').text
        except NoSuchElementException: 
            pass

        timeActive = ""
        tableActive = ""
        try:
            active = driver.find_element_by_class_name("JjSWRd")
            active.click()
            tableActive = driver.find_element_by_class_name("WgFkxc").text
        except NoSuchElementException: 
            pass

        danhGiaGg = driver.find_element_by_class_name("hqzQac").find_element_by_tag_name('span a span').text
        
        
        print("title", title)
        print("fullTittle", fullTittle)
        print("price", price)
        print("other_service", other_service)


        print("score", score)
        print("address", address)
        print("addressDetail", addressDetail)
        print("phone", phone)
        print("danhGia", danhGiaGg)
        print("tableActive", tableActive)

        print('==============')
        
        #Handle info from page
        #field change: website_id_quan, rate, phone, rate_count, price_from, price_to, other_service, tableActive
        phone_change = phone.replace(" ", "")
        rate_change = float(str(score.replace(",", "."))) * 2
        rate_count_change = danhGiaGg.split(" ")[0]

        print("phone_change", phone_change)
        print("rate_change", rate_change)
        print("rate_count_change", rate_count_change)
        