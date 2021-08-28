import tempfile
import os
import time
import threading
import subprocess
import config.env

class LoggingFile:
    def __init__(self, file, isClose=False):
        self.fd = file
        self.isClose = isClose
    def __write(self,msg,end):
        bytearray = msg + end
        self.fd.write(bytearray.encode())
        self.fd.flush()
    def write(self,msg,end="\n"):
        if self.isClose:
            return
        try:
            name = threading.current_thread().name
            msg = "[%s] %s" % (name,msg)
            self.__write(msg,end)        
        except Exception as e:
            print(e)
    def close(self):
        if not self.isClose:
            try:
                self.isCLose = True
                self.__write("\n~","")
                time.sleep(1.5)
                self.fd.close()
                os.unlink(self.fd.name)
            except Exception as e:
                print(e)

def create_log() -> LoggingFile:
    if config.env.external_log:
        fd = tempfile.NamedTemporaryFile(delete=False)
        tracert = os.path.dirname(__file__)+"/tracert.py"
        subprocess.Popen([config.env.python_launcher,tracert,fd.name],creationflags=subprocess.CREATE_NEW_CONSOLE)
        return LoggingFile(fd)
    else:
        return LoggingFile(None,True)