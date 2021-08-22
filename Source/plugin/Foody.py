import threading
import time
import requests
from bs4 import BeautifulSoup
from utils.signal import AddThread, DoneThread, IsExit
from model.baiviet import add_bai_viet, get_bai_viet



def init():
    print("Foody gồm có những chủ đề như sau:")
    
    mock= ["Thức ăn", "Nước uống", "Ăn vặt"]
    
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
url = "https://www.foody.vn/ha-noi"

def start():
    response = requests.get(url)
    
    content = BeautifulSoup(response.content, "html.parser")
    titles = soup.findAll('h3', class_='title')

    links = [link.find('a').attrs["href"] for link in titles]
    
    for link in links:
        news = requests.get("https://www.foody.vn/ha-noi" + link)
        soup = BeautifulSoup(news.content, "html.parser")
        title = soup.find("h1", class_="article-title").text
        abstract = soup.find("h2", class_="sapo").text
        body = soup.find("div", id="main-detail-body")
        content = body.findChildren("p", recursive=False)[0].text + body.findChildren("p", recursive=False)[1].text
        print("Tiêu đề: " + title)
        print("Nội dung: " + content)

