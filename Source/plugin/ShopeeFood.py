import threading
import time
from utils.metric import AddMetric
from utils.logfile import create_log
from utils.signal import AddThread, DoneThread, IsExit
from model.baiviet import add_bai_viet, get_bai_viet

def init():
    print("ShopeeFood có những chủ đề hot như sau:")
    # get some subject
    # gọi api hoặc định nghĩa ra sẵn các chủ đề cho người dùng chọn
    mock= ["Đồ ăn", "Đồ uống", "Đồ chay"]
    
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

    start()

# khởi tạo luồng mới bắt buộc đặt tên thread, và không trùng
num = 1
def start():
    global num
    # create thread

    nameTH = "ShopeeFood %s"%num
    t1 = threading.Thread(target=process, name=nameTH)
    t1.setDaemon(True)
    t1.start()

    num += 1

# luồng hoạt động chính
def process():
    # tạo logger
    logger = create_log()
    name = threading.current_thread().name

    AddThread(name)
    time.sleep(1)

    try: 
        # bat buoc nam trong block try except

        # fake:
        # ci=1
        while True:
            # kiểm tra xem có tín hiệu thoát từ main
            if IsExit():
                break
            
            # lấy data crawler ...
            start_time = time.time()
            logger.write("Lấy data...")
            
            # lấy data
            time.sleep(0.1)

            # xử lý data
            time.sleep(0.3)
            AddMetric(len("đây là nội dung đã xử lý"))

            # cho vao db ...
            time.sleep(0.05)

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
            end_time = time.time()
            logger.write("Thời gian xử lý: %.2f" % (end_time-start_time))

            # sleep for cpu
            time.sleep(3.5)
            
        # test
        # print(get_bai_viet())
    
    except Exception as e:
        logger.write("Stop! "+str(e))

    logger.close()
    DoneThread(name)