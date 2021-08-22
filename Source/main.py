import plugin.Foody as Foody
import plugin.ShopeeFood as ShopeeFood
import plugin.GoogleReview as GoogleReview
import utils.database
import time
from utils.signal import IsDoneAllThread, SetExit


def clean():
    utils.database.close_connection()

def main():
    conn = utils.database.create_connection()

    if conn is not None:
        if not utils.database.create_schema():
            print("Init database error")
            clean()
            exit(1)

def input_website():
    print("1. Foody")
    print("2. Shopeefood")
    print("3. Google review")
    print("Bạn chọn: ", end="")
    while True:
        choose = None
        try:
            choose = int(input())
        except:
            pass
        if choose is None or choose < 1 or choose > 3:
            print("Lựa chọn không hợp lệ, vui long chọn lại: ",end="")
        else:
            break

    if choose == 1:
        Foody.init()
    elif choose == 2:
        ShopeeFood.init()
    elif choose == 3:
        GoogleReview.init()
    
def menu():
    print("Project: TopicalCrawler")
    print("Web of Science")
    print()
    print("Chon website cần crawler:")
    input_website()
    while True:
        print("Nhập bất kỳ để tiếp tục chọn website khác")
        print("Nhập exit để thoát chương trình")
        inp = input()
        if inp == "exit":
            SetExit()
            break
        else:
            print("Chon website cần crawler:")
            input_website()

    print("Chương trình đang tắt ",end="")
    while not IsDoneAllThread():
        time.sleep(1)
        print(".",end="",flush=True)
    print("ok!")

if __name__ == '__main__':
    main()
    menu()
    clean()