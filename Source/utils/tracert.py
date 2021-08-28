import sys
import time

def _readLog(path):
    file = open(path,mode="r",encoding="utf-8")
    while True:
        where = file.tell()
        line = file.read()
        if not line:
            time.sleep(0.5)
            file.seek(where)
        elif line.split("\n")[-1] == "~":
            print("\n".join(line.split("\n")[0:-1]),end="",flush=True)
            break
        else:
            print(line,end="",flush=True)
    file.close()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        path = sys.argv[1]
        _readLog(path)
        print("Bấm enter để kết thúc")
        input()

