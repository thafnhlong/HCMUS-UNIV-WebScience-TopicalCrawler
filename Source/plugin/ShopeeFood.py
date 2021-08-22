import threading
import time
from utils.signal import AddThread, DoneThread, IsExit
from model.baiviet import add_bai_viet, get_bai_viet

def init():
    print("ShopeeFood có những chủ đề hot như sau:")
    # get some subject
    mock= ["Đồ ăn", "Đồ uống", "Đồ chay"]
    
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

num = 1

def start():
    global num
    # create thread

    nameTH = "ShopeeFood %s"%num
    t1 = threading.Thread(target=process, name=nameTH)
    t1.setDaemon(True)
    t1.start()

    num += 1

def logger(msg,end="\n"):
    name = threading.current_thread().name
    print("[%s]" % name,msg,end=end)

def process():
    name = threading.current_thread().name

    AddThread(name)
    time.sleep(1)

    try: 
        # bat buoc nam trong block

        # fake:
        # ci=1
        while True:
            if IsExit():
                break
            
            # lấy data
            # cho vao db
            # lap lai

            # khong su dung logger de tranh tràn console
            # chi de test
            logger("Lấy data...")

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

            # sleep for cpu
            time.sleep(3.5)

        # test
        # print(get_bai_viet())
    
    except Exception as e:
        logger("Stop!", str(e))

    DoneThread(name)