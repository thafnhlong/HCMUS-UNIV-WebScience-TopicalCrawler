import threading
import time
import json
import traceback
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from utils.logfile import create_log
from utils.signal import AddThread, DoneThread, IsExit
from utils.metric import AddMetric
from model.baiviet import add_bai_viet, get_bai_viet

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

    chude = mock[choose-1]
    start(chude)

num = 1
def start(chude):
    print('1', chude)
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
    print('2', chude)
    logger = create_log()
    name = threading.current_thread().name

    AddThread(name)
    time.sleep(1)

    try: 
        # bat buoc nam trong block try except
       
        # trang i = 0

        while True:
            # kiểm tra xem có tín hiệu thoát từ main
            if IsExit():
                break
            
            start_time = time.time()

            # lay noi dung trang i
            logger.write("Lấy data...")

            # i++
            # goi ham lay noi dung trang
            # ...
            chrome_options = Options()
            chrome_options.add_argument("--window-size=1920x1080")
            driver = webdriver.Chrome(chrome_options=chrome_options, executable_path="webdriver\chromedriver")
            url = "https://google.com"
            driver.get(url)
            time.sleep(2)

            login = driver.find_element_by_xpath("//input").send_keys(chude)
            driver.find_element_by_xpath("//input").send_keys(Keys.ENTER)
            time.sleep(2)

            # select button Xem Tat ca
            confirm = driver.find_element_by_xpath("//*[text()= 'Xem tất cả']")
            confirm.click()

            isNextPage = True
            while isNextPage:
                #get all item
                listItem = driver.find_elements_by_class_name("VkpGBb")
                print(0)
                print(listItem)
                for item in listItem:
                    #Get link item
                    tag_current = item.find_element_by_tag_name('a')
                    print(tag_current)
                    print(0.2)
                    tag_current.click()
                    time.sleep(3)
                    url_page = driver.current_url

                    #Get info detail
                    title = item.find_element_by_class_name("dbg0pd").find_element_by_tag_name('div').text
                    print('title', title)
                    fullTittle = driver.find_element_by_class_name("SPZz6b").find_element_by_tag_name('h2 span').text
                    score = item.find_element_by_class_name("rllt__details").find_element_by_tag_name('div span').text
                    address = item.find_element_by_class_name("rllt__details").find_element_by_tag_name('div:nth-child(2)').text
                    print(1)
                    addressDetail = driver.find_element_by_class_name("LrzXr").text
                    print(2)
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
                    print('1')
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
                    print(3)
                    
                    danhGiaGg = ""
                    try:
                        danhGiaGg = driver.find_element_by_class_name("hqzQac").find_element_by_tag_name('span a span').text
                    except NoSuchElementException: 
                        pass

                    other_service = ""
                    try:
                        other_service = driver.find_element_by_xpath("//c-wiz[@class='u1M3kd W2lMue']").find_element_by_tag_name('div').text
                    except NoSuchElementException: 
                        pass
                

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
                    phone_change = phone.replace(" ", "")
                    district_change = ""
                    if len(list_district) > 0:
                        for district_element in list_district:
                            element = district_element.lower()
                            if element.find("quận") > 0:
                                district_change = element.replace("quận", "").replace(" ", "")

                    tableActive_change = []
                    if len(tableActive) > 0:
                        tableActive_change = tableActive.split("\n")

                    if score != "":
                        temp = str(score.replace(",", ".").replace("Quảng cáo·", ""))
                        if temp != "":
                            rate_change = float(temp) * 2
                            rate_count_change = float(danhGiaGg.split(" ")[0])
                        else :
                            rate_change = 0
                            rate_count_change = 0
                    else :
                        rate_change= 0
                        rate_count_change = 0
                    
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
                    end_time = time.time()
                    time.sleep(0.1)

                    # lap tung item
                    # lay noi dung 
                    objectData ={
                        "website_id_quan": website_id_quan_change,
                        "website": website_change,
                        "url": url_change,
                        "district": district_change,
                        "rate": rate_change,
                        "active_time": json.dumps({
                            "monday": "06:00-22:00",
                            "tuesday": "06:00-22:00"
                        }),
                        "full_name": fullName_change,
                        "phone": phone_change,
                        "rate_count": rate_count_change,
                        "price_from": price_from,
                        "price_to": price_to,
                        "other_service": json.dumps(array_service)
                    }

                    # insert DB
                    try:
                        add_bai_viet(
                            active_time=objectData["active_time"],
                            district=objectData["district"],
                            full_name=objectData["full_name"],
                            phone=objectData["phone"],
                            price_from=objectData["price_from"],
                            price_to=objectData["price_to"],
                            rate=objectData["rate"],
                            rate_count=objectData["rate_count"],
                            url=objectData["url"],
                            website=objectData["website"],
                            website_id_quan= objectData["website_id_quan"],
                            other_service= objectData["other_service"]
                        )
                    except Exception:
                        logger.write(traceback.format_exc()) # only debugging
                        # duplicate or any error
                        pass

                    time.sleep(0.05)
                    print("---------------------------------")
                    AddMetric(len(json.dumps(objectData)))

                #click next page
                exist = check_exists_button_next(driver)
                if exist == True:
                    driver.find_element_by_xpath('//a[@id="pnnext"]').click()
                    time.sleep(1)
                else :
                    isNextPage = False
                logger.write("Thời gian xử lý: %.2f" % (end_time-start_time))
            
            # tach ra các item trong trang
            # time.sleep(0.1)

            # lap tung item
            # lay noi dung 

            time.sleep(0.3)
            AddMetric(len("đây là nội dung đã xử lý"))

            # insert DB

            time.sleep(0.05)

            # lap

            # lấy data crawler ...


            # test
            # phai co try, nếu insert trung
            # try:
            #     add_bai_viet(
            #         "shopeefood_%s"%(ci),"shopeefood","http://example.com","bình thạnh",9.5,r"[....]",
            #         "Quán nào đó", None, 3000, 200, 30000,100000,"máy lạnh, quạt,xe"
            #     )
            # except:
            #     pass
            # ci+=1

            # lấy thời gian thực thi
            # end_time = time.time()
            # logger.write("Thời gian xử lý: %.2f" % (end_time-start_time))

            # sleep for cpu
            time.sleep(3.5)
                
    except Exception as e:
        logger.write(traceback.format_exc())
        logger.write("Stop! "+str(e))

    logger.close()
    DoneThread(name)

def check_exists_button_next(driver):
    try:
        driver.find_element_by_xpath('//a[@id="pnnext"]')
    except NoSuchElementException:
        return False
    return True