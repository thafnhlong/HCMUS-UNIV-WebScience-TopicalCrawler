import utils.database
import time



def add_bai_viet():
    utils.database.insert_value("baiviet",(int(time.time()),"title","page"))

def get_bai_viet():
    listData = utils.database.fetch_value("select * from baiviet where id>?",[2])
    print(listData.fetchall())
