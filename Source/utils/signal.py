exit_app = False
current_list_th = set()

def IsExit():
    global exit_app
    return exit_app

def SetExit():
    global exit_app
    exit_app = True

def AddThread(nameth):
    global current_list_th
    current_list_th.add(nameth)

def DoneThread(nameth):
    global current_list_th
    current_list_th.remove(nameth)

def IsDoneAllThread():
    global current_list_th
    return len(current_list_th) == 0