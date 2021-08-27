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
        website = url

        score = item.find_element_by_class_name("rllt__details").find_element_by_tag_name('div span').text
        address = item.find_element_by_class_name("rllt__details").find_element_by_tag_name('div:nth-child(2)').text
        addressDetail = driver.find_element_by_class_name("LrzXr").text
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

        
        #Handle info from page
        #field change: website_id_quan, rate, phone, rate_count, price_from, price_to, other_service, tableActive
        website_id_quan_change = "GoogleRV_"+str(hash(addressDetail))
        website_change = "Google Review"
        list_district = addressDetail.split(",")
        district_change = ""
        if len(list_district) > 0:
            for district_element in list_district:
                element = district_element.lower()
                if element.find("quận") > 0:
                    district_change = element.replace("quận", "").replace(" ", "")

        tableActive_change = []
        if len(tableActive) > 0:
            tableActive_change = tableActive.split("\n")

        phone_change = phone.replace(" ", "")
        rate_change = float(str(score.replace(",", "."))) * 2
        rate_count_change = danhGiaGg.split(" ")[0]
        
        print('==============')
        #field no change: website, url
        price_from = 0
        price_to = 0
        if len(price) > 0:
            if len(price) == 1:
                price_to = 20
                price_from = 100
            if len(price) == 2:
                price_to = 100
                price_from = 300
            if len(price) > 2:
                price_to = 200
                price_from = 1000

        array_service = []
        if len(other_service) > 0:
            array_service = other_service.split("·")

        #field no change: website, url
        url_change = url_page
        fullName_change = fullTittle
        print("---------------------------------")
