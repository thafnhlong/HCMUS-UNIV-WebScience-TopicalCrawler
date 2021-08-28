from utils.signal import AddThread, DoneThread, IsExit
from utils.logfile import create_log
from utils.lock import synchronized

import threading
import time

MonitorGlobal = {
    "size":0,
    "count":0
}

@synchronized
def AddMetric(size: int):
    global MonitorGlobal
    MonitorGlobal["size"] += size
    MonitorGlobal["count"] += 1

def _watch():
    global MonitorGlobal
    logger = create_log()
    name = threading.current_thread().name
    AddThread(name)
    
    start_time = time.time()
    time.sleep(1)


    while True:
        if IsExit():
            break
        
        try:
            end_time = time.time()
            all_time = end_time - start_time
            sizePerS = MonitorGlobal["size"] / all_time
            countPerS = MonitorGlobal["count"] / all_time

            logger.write("Số trang xử lý: %.2f / giây" % countPerS)
            logger.write("Lượng thông tin xử lý: %s / giây" % sizeof_fmt(sizePerS) )
            logger.write("")
        except:
            break

        time.sleep(5)
    
    logger.close()
    DoneThread(name)


def start():
    nameTH = "Monitor"
    t1 = threading.Thread(target=_watch, name=nameTH)
    t1.setDaemon(True)
    t1.start()



def sizeof_fmt(num, suffix='B'):
    for unit in ['','Ki','Mi','Gi','Ti','Pi','Ei','Zi']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Yi', suffix)