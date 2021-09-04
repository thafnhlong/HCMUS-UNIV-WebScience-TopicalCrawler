import json
import threading
import time
import math
import requests
import traceback
from requests.sessions import Session, session
from utils.metric import AddMetric
from utils.logfile import create_log
from utils.signal import AddThread, DoneThread, IsExit
from model.baiviet import add_bai_viet, get_bai_viet

def khoitaoReq():
    req = requests.session()
    # tạo giả lập:
    headers = {
        'x-foody-api-version': '1',
        'x-foody-client-language': 'vi',
        'x-foody-client-type': '1',
        'x-foody-app-type': '1004',
        'x-foody-client-id': '',
        'x-foody-access-token': '',
        'x-foody-client-version': '3.0.0',
        'referer': 'https://shopeefood.vn/',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36',
    }
    req.headers.update(headers)
    return req

def laychudevaquan(req):
    resp = req.get("https://gappapi.deliverynow.vn/api/meta/get_metadata").json()
    data = resp.get("reply").get("country")
    cities = data.get("cities")

    DistrictList = {}
    for tp in cities:
        if tp["id"] == 217:
            districts = tp.get("districts")
            for district in districts:
                DistrictList[district.get("district_id")] = district.get("name").lower().replace("quận ","").strip()

    CategoryList = []
    
    now_services = data.get("now_services")

    for it in range(len(now_services)):
        bigCat = now_services[it]
        nameBigCat = bigCat.get("name")
        idBigCat = bigCat.get("id")
        categories = bigCat.get("categories")

        for category in categories:
            CategoryList.append(
                {
                    "idBigCat": idBigCat,
                    "name": "%s-%s" % (nameBigCat,category.get("name")),
                    "idCat": category.get("id"),
                }
            )
        CategoryList.append(
            {
                "idBigCat": idBigCat,
                "name": "%s-%s" % (nameBigCat, "Tất cả"),
            }
        )

    return CategoryList,DistrictList

def init():
    req = khoitaoReq()

    print("Đang truy xuất lấy data...",end="")
    CategoryList,DistrictList = laychudevaquan(req)
    print("ok")

    print("ShopeeFood có những chủ đề hot như sau:")
    
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

    start(chude,DistrictList,req)

# khởi tạo luồng mới bắt buộc đặt tên thread, và không trùng
num = 1
def start(chude,DistrictList,req):
    global num
    # create thread

    nameTH = "ShopeeFood %s"%num
    t1 = threading.Thread(target=process, name=nameTH,args=(chude,DistrictList,req,))
    t1.setDaemon(True)
    t1.start()

    num += 1


def laytoanbocuahangtrongchude(chude,req:Session):
    body = {
        "category_group": 1, #static
        "city_id": 217, # HCM
        "delivery_only": True, #static
        "keyword": "", #static
        "sort_type": 8, #static
        "foody_services": [
            chude["idBigCat"] # (1)
        ],
        "full_restaurant_ids": True,
    }
    if chude.get("idCat"):
        body["combine_categories"]= [  
            {
                "code": 1, #static
                "id": chude["idCat"] # (2)
            }
        ]

    resp = req.post("https://gappapi.deliverynow.vn/api/delivery/search_global",json=body).json()

    RestaurantList = []

    search_result = resp.get("reply").get("search_result")
    for result in search_result:
        restaurant_ids = result.get("restaurant_ids")
        service_type = result.get("service_type")
        for restaurant_id in restaurant_ids:
            RestaurantList.append({
                "id": restaurant_id,
                "service_type": service_type
            })
    return RestaurantList

def weekday2text(week_day):
    if week_day == 1:
        return "monday"
    if week_day == 2:
        return "tuesday"
    if week_day == 3:
        return "wednesday"
    if week_day == 4:
        return "thursday"
    if week_day == 5:
        return "friday"
    if week_day == 6:
        return "saturday"
    if week_day == 7:
        return "sunday"

def laychitietcuahang(restaurant,DistrictList,req:Session):
    uri = "https://gappapi.deliverynow.vn/api/delivery/get_detail?id_type=%s&request_id=%s" % \
        (restaurant["service_type"],restaurant["id"])
    resp = req.get(uri).text
    jp = json.loads(resp)

    oldSize = len(resp)
    # nếu service type không hợp lệ thì thử lại với loại 3-x ( 1 => 2, 2 => 1)
    if jp.get("result") != "success":
        uri = "https://gappapi.deliverynow.vn/api/delivery/get_detail?id_type=%s&request_id=%s" % \
            ((3-restaurant["service_type"]),restaurant["id"])
        resp = req.get(uri).text
        jp = json.loads(resp)
        oldSize += len(resp)

        if jp.get("result") != "success":
            return oldSize,None

    delivery_detail = jp.get("reply").get("delivery_detail")

    # đôi khi cửa hàng không thuộc thành phố
    if delivery_detail["city_id"] != 217:
        return oldSize,None

    active_time = {}
    week_days = delivery_detail.get("delivery").get("time").get("week_days")
    for week_day in week_days:
        active_time[weekday2text(week_day["week_day"])] = "%s-%s" % (week_day["start_time"],week_day["end_time"])

    price_range = delivery_detail["price_range"]
    rating = delivery_detail["rating"]

    return oldSize,{
        "active_time": json.dumps(active_time),
        "district": DistrictList[delivery_detail["district_id"]],
        "id": delivery_detail["id"],
        "full_name": delivery_detail["name"],
        "phone": ', '.join(delivery_detail["phones"]),
        "price_from": price_range["min_price"],
        "price_to": price_range["max_price"],
        "rate": rating["avg"] * 2,
        "rate_count": rating["total_review"],
        "favorite": delivery_detail["user_favorite_count"],
        "url": delivery_detail["url"],
    }

# luồng hoạt động chính
def process(chude,DistrictList,req):
    # tạo logger
    logger = create_log()
    name = threading.current_thread().name

    AddThread(name)
    logger.write("Lấy chủ đề: %s"%chude["name"])
    time.sleep(1)

    isError = False

    try: 
        # bat buoc nam trong block try except
       
        # lay toan bo cua hang nam trong chu de
        RestaurantList = laytoanbocuahangtrongchude(chude,req)
        # chia ra 25 items / page

        logger.write("Tổng số trang tìm được: %s ứng với %s cửa hàng"%(
            math.ceil(len(RestaurantList)/25) ,len(RestaurantList))
        )

        restaurant_index=0
        start_time = None

        while True:
            # kiểm tra xem có tín hiệu thoát từ main
            if IsExit():
                isError = True
                break

            if restaurant_index == len(RestaurantList):
                break
            
            # mỗi 25 trang thì 
            if restaurant_index % 25 == 0:
                start_time = time.time()
                logger.write("Xử lý các cửa hàng trên trang số %.0f..."%(restaurant_index/25+1))
            
            data= None
            try:
                size,data = laychitietcuahang(RestaurantList[restaurant_index],DistrictList,req)
                AddMetric(size)
            except Exception:
                logger.write(traceback.format_exc())
                errorItem = RestaurantList[restaurant_index]
                logger.write("Lỗi tại cửa hàng id:%s - type:%s"%(errorItem["id"],errorItem["service_type"]))

            if data is not None:
                try:
                    add_bai_viet(
                        active_time=data["active_time"],
                        district=data["district"],
                        full_name=data["full_name"],
                        phone=data["phone"],
                        price_from=data["price_from"],
                        price_to=data["price_to"],
                        rate=data["rate"],
                        rate_count=data["rate_count"],
                        favorite=data["favorite"],
                        url=data["url"],
                        website="ShopeeFood",
                        website_id_quan= "ShopeeFood_"+ str(data["id"]),
                    )
                except Exception:
                    # logger.write(traceback.format_exc()) # only debugging
                    # duplicate or any error
                    pass

            # trang cuối cùng cua page hoặc list
            if (restaurant_index %24 == 0 and restaurant_index > 0) or restaurant_index == len(RestaurantList)-1:
                end_time = time.time()
                logger.write("Thời gian xử lý: %.2f" % (end_time-start_time))

            restaurant_index += 1

            # sleep for cpu
            time.sleep(0.1)
                
    except Exception as e:
        isError = True
        logger.write("Stop! "+str(e))

    if not isError:
        logger.write("Đã crawler hết tất cả cửa hàng của chủ đề này.")

    logger.close()
    DoneThread(name)

    # garbage
    req.close()